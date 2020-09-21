"""
Основной модуль приложения
"""

import argparse
import asyncio
import asyncpg
from aiohttp import web
from aiojobs.aiohttp import setup

from api_helper import validate_params, get_local_news
from data_updater import background_parser

__author__ = 'Novozhilov A.S.'

routes = web.RouteTableDef()


@routes.get('/posts')
async def posts(request: web.Request) -> web.Response:
    """
    Обработчик get-запроса на адрес /posts
    Args:
        request: Данные запроса

    Returns:
        web.Response: ответ в формате json
    """
    request_params = request.rel_url.query
    if not validate_params(request_params):
        raise web.HTTPNotImplemented(text='Not valid params!')

    res = await get_local_news(db=request.app['db_conn'], **request_params)
    return web.json_response(res)


def init_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-user', dest='user')
    arg_parser.add_argument('-passwd', dest='passwd')
    arg_parser.add_argument('-host', dest='host')
    arg_parser.add_argument('-port', dest='port')
    arg_parser.add_argument('-dbname', dest='dbname')
    arg_parser.add_argument('-max-news', dest='max_news', type=int)
    arg_parser.add_argument('-timeout', dest='timeout', type=int)
    args = arg_parser.parse_args()
    return args


async def init_app() -> web.Application:
    """
    Инициализация приложения
    Returns:
        app(web.Application): инстанс приложения
    """
    args = init_args()
    app = web.Application()
    app['db_conn'] = await asyncpg.create_pool(
        f'postgres://{args.user}:{args.passwd}@{args.host}:{args.port}/{args.dbname}'
    )
    app.add_routes(routes)
    setup(app)
    asyncio.get_event_loop().create_task(background_parser(
        app['db_conn'],
        timeout=args.timeout,
        max_news_count=args.max_news
    ))
    return app

if __name__ == '__main__':
    app = asyncio.get_event_loop().run_until_complete(init_app())
    web.run_app(app)


