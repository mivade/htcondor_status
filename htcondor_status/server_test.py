import json
from unittest import mock

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

from . import server


class HandlerTestCase(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return server.make_app(debug=False)


class TestIndexHandler(HandlerTestCase):
    @gen_test
    async def test_get(self) -> None:
        response = await self.http_client.fetch(self.get_url("/"))
        assert response.headers["Content-Type"].startswith("text/html")


class TestJobsHandler(HandlerTestCase):
    @gen_test
    async def test_get(self) -> None:
        with mock.patch.object(server, "get_jobs", return_value=[]):
            response = await self.http_client.fetch(self.get_url("/jobs.json"))

        assert response.headers["Content-Type"].startswith("application/json")
        body = json.loads(response.body)
        assert body == {"jobs": []}
