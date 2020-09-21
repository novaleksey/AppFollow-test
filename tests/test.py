"""
Юнит тесты API
"""
import asyncpg
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from App.main import posts

__author__ = 'Novozhilov A.S.'


class APITest(AioHTTPTestCase):
    async def get_application(self):
        app = web.Application()
        app['db_conn'] = await asyncpg.create_pool(
            'postgres://postgres:postgres@localhost:5432/AppFollow'
        )
        app.router.add_get('/posts', posts)
        return app

    @unittest_run_loop
    async def test_params(self):
        resp = await self.client.request("GET", '/posts', params={'sort': 'desc'})
        assert resp.status == 200
        resp = await self.client.request("GET", '/posts', params={'order': 'url'})
        assert resp.status == 200
        resp = await self.client.request("GET", '/posts', params={'offset': '10'})
        assert resp.status == 200
        resp = await self.client.request("GET", '/posts', params={'order': 'foo'})
        assert resp.status == 501
        resp = await self.client.request("GET", '/posts', params={'limit': '-10'})
        assert resp.status == 501
        resp = await self.client.request("GET", '/posts', params={'offset': 'bar'})
        assert resp.status == 501
