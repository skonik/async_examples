import asyncio
import math
import os

from time import time
import aiobotocore

AWS_S3_HOST = 'http://localhost:9000'
AWS_SECRET_ACCESS_KEY = 'FAKE_SECRET_KEY'
AWS_ACCESS_KEY_ID = 'FAKE_ACCESS_KEY'
AWS_MULTIPART_BYTES_PER_CHUNK = 6000000  # ~ 5mb
AWS_S3_BUCKET_NAME = 'test'

part_info = {
    'Parts': []
}


async def upload_chunk(client, fp, upload_id, chunk_number, bytes_per_chunk, source_size, key):
    global part_info
    start = time()
    offset = chunk_number * bytes_per_chunk
    remaining_bytes = source_size - offset
    bytes_to_read = min([bytes_per_chunk, remaining_bytes])
    part_number = chunk_number + 1

    fp.seek(offset)
    data = fp.read(bytes_to_read)
    resp = await client.upload_part(
        Bucket=AWS_S3_BUCKET_NAME,
        Body=data,
        UploadId=upload_id,
        PartNumber=part_number,
        Key=key
    )

    part_info['Parts'].append(
        {
            'PartNumber': part_number,
            'ETag': resp['ETag']
        }
    )
    print('done in ', time() - start)


async def multipart_upload_to_s3(file_path, folder_name,
                                 host=AWS_S3_HOST,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                 aws_access_key_id=AWS_ACCESS_KEY_ID,
                                 bytes_per_chunk=AWS_MULTIPART_BYTES_PER_CHUNK):
    filename = os.path.basename(file_path)
    key = '{}/{}'.format(folder_name, filename)

    loop = asyncio.get_event_loop()
    session = aiobotocore.get_session(loop=loop)
    async with session.create_client(
            's3', endpoint_url=host,
            aws_secret_access_key=aws_secret_access_key,
            aws_access_key_id=aws_access_key_id
    ) as client:

        source_size = os.stat(file_path).st_size
        chunks_count = int(math.ceil(source_size / float(bytes_per_chunk)))
        print('coro count: ', chunks_count)

        create_multipart_upload_resp = await client.create_multipart_upload(
            ACL='bucket-owner-full-control',
            Bucket=AWS_S3_BUCKET_NAME,
            Key=key,
        )

        upload_id = create_multipart_upload_resp['UploadId']

        # We have to keep info about uploaded parts.
        # https://github.com/boto/boto3/issues/50#issuecomment-72079954
        global part_info
        tasks = []
        with open(file_path, 'rb') as fp:
            for chunk_number in range(chunks_count):
                tasks.append(
                    upload_chunk(
                        client=client,
                        fp=fp,
                        chunk_number=chunk_number,
                        bytes_per_chunk=bytes_per_chunk,
                        key=key, upload_id=upload_id,
                        source_size=source_size
                    )
                )

            await asyncio.gather(*tasks)

        list_parts_resp = await client.list_parts(
            Bucket=AWS_S3_BUCKET_NAME,
            Key=key,
            UploadId=upload_id
        )

        part_list = sorted(part_info['Parts'], key=lambda k: k['PartNumber'])
        part_info['Parts'] = part_list

        if len(list_parts_resp['Parts']) == chunks_count:
            print('Done uploading file')
            await client.complete_multipart_upload(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=key,
                UploadId=upload_id,
                MultipartUpload=part_info
            )

            return True

        else:
            print('Aborted uploading file.')
            await client.abort_multipart_upload(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=key,
                UploadId=upload_id
            )

            return False


if __name__ == '__main__':
    start = time()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(multipart_upload_to_s3('examples/large.txt', 'testing'))
    except Exception as e:
        print('error: ', e)
    finally:
        print('took: ')
        print(time() - start)
