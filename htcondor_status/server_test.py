import json
from unittest import mock

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

from . import server


class HandlerTestCase(AsyncHTTPTestCase):
    def get_app(self) -> Application:
        return server.HTCondorStatusApp(debug=False)


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


class TestJobCountHandler(HandlerTestCase):
    @gen_test
    async def test_get(self) -> None:
        jobs = [{"JobStatus": 1}, {"JobStatus": 2}, {"JobStatus": 5}]

        with mock.patch.object(server.JobCountHandler, "jobs", jobs):
            response = await self.http_client.fetch(self.get_url("/counts.json"))

        body = json.loads(response.body)
        assert body == {"total": 3, "idle": 1, "running": 1, "held": 1}
