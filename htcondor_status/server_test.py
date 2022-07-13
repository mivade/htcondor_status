import json
import random
import secrets
import time
from typing import Any
from unittest import mock

from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

from . import server
from .jobs import JobList


class HandlerTestCase(AsyncHTTPTestCase):
    @property
    def sample_job_list(self) -> JobList:
        def make_entry(status: int) -> dict[str, Any]:
            return {
                "JobStatus": status,
                "ClusterId": random.randint(1, 100),
                "GlobalJobId": secrets.token_hex(16),
                "QDate": time.time(),
                "Owner": "me",
                "Cmd": "/bin/sleep",
            }

        return [make_entry(1), make_entry(2), make_entry(5)]

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
        with mock.patch.object(server.JobCountHandler, "jobs", self.sample_job_list):
            response = await self.http_client.fetch(self.get_url("/counts.json"))

        body = json.loads(response.body)
        assert body == {"total": 3, "idle": 1, "running": 1, "held": 1}


class TestJobSummaryHandler(HandlerTestCase):
    @gen_test
    async def test_get(self) -> None:
        with mock.patch.object(server.JobSummaryHandler, "jobs", self.sample_job_list):
            response = await self.http_client.fetch(self.get_url("/summary.json"))

        body = json.loads(response.body)
        assert "jobs" in body
        assert len(body["jobs"]) == len(self.sample_job_list)
