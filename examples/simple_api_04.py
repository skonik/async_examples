import json

from aiohttp import web

users = [
    {
        'id': 1,
        'first_name': 'Pavel',
        'last_name': 'Durov',
        'role': 'telegram_owner',
        'location': 'Unknown'
    },
    {
        'id': 2,
        'first_name': 'Vlaidmir',
        'last_name': 'Putin',
        'role': 'president',
        'location': 'Moscow'
    },

]

routes = web.RouteTableDef()


@routes.get('/users')
async def get_users(request):
    users = request.app['users']
    users = list(filter(lambda x: x is not None, users))

    return web.Response(
        status=200,
        body=json.dumps(users),
        content_type='application/json'
    )


@routes.get(r'/users/{id:\d+}')
async def get_user(request):
    id = request.match_info.get('id')
    user_not_found = web.Response(
            status=404,
            body=json.dumps(
                {
                    'description': 'User not found.'
                }
            ),
            content_type='application/json'
        )
    try:
        users = request.app['users']
        user = users[int(id) - 1]
        if user is None:
            response = user_not_found
        else:
            response = web.Response(
                status=200,
                body=json.dumps(user),
                content_type='application/json'
            )
    except IndexError:
        response = user_not_found

    return response


@routes.delete(r'/users/{id:\d+}')
async def delete_user(request):
    users = request.app['users']
    id = request.match_info.get('id')
    try:
        users[int(id) - 1] = None
        response = web.Response(
            status=204,
            content_type='application/json'
        )
    except IndexError:
        response = web.Response(
            status=404,
            body=json.dumps(
                {
                    'description': 'User not found.'
                }
            ),
            content_type='application/json'
        )

    return response


@routes.post('/users')
async def create_user(request):
    users = request.app['users']
    data = await request.json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    role = data.get("role", "user")
    location = data.get("location", "Unkown")

    new_user = {
            'id': len(users) + 1,
            'first_name': first_name,
            'last_name': last_name,
            'role': role,
            'location': location
        }

    users.append(new_user)

    return web.Response(
        status=201,
        body=json.dumps(new_user),
        content_type='application/json'
    )


def create_app():
    app = web.Application()
    app['users'] = users
    app.add_routes(routes)

    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app)