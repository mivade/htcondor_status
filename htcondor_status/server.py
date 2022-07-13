import asyncio
from datetime import timedelta
import logging
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from tornado.ioloop import PeriodicCallback
from tornado.log import enable_pretty_logging
from tornado.web import Application, RequestHandler, StaticFileHandler

from .jobs import JobList, get_jobs, simulate_jobs

logger = logging.getLogger("__name__")


class BaseHandler(RequestHandler):
    @property
    def jobs(self) -> JobList:
        """Return the most recent list of jobs."""
        return self.application.jobs


class IndexHandler(BaseHandler):
    def get(self) -> None:
        """Get ``index.html``."""
        self.render("index.html")


class JobsHandler(BaseHandler):
    def get(self) -> None:
        """Get the most recent list of HTCondor jobs."""
        self.write({"jobs": self.jobs})


class JobCountHandler(BaseHandler):
    def get(self) -> None:
        """Get counts of jobs in different states."""
        jobs = pd.DataFrame(self.jobs)
        self.write(
            {
                "total": len(jobs),
                "idle": len(jobs[jobs.JobStatus == 1]),
                "running": len(jobs[jobs.JobStatus == 2]),
                "held": len(jobs[jobs.JobStatus == 5]),
            }
        )


class JobSummaryHandler(BaseHandler):
    def get(self) -> None:
        """Get data needed only to render a table with job summary info."""
        jobs = pd.DataFrame(self.jobs)
        self.write(
            {
                "jobs": jobs[
                    [
                        "GlobalJobId",
                        "ClusterId",
                        "QDate",
                        "Owner",
                        "Cmd",
                        "JobStatus",
                    ]  # FIXME: JobName
                ].to_dict(orient="records")
            }
        )


class HTCondorStatusApp(Application):
    """HTCondor status web application."""

    def __init__(
        self,
        *,
        debug: bool = False,
        simulate: bool = False,
        refresh_interval_seconds: int = 30,
    ) -> None:
        here = Path(__file__).parent
        static_path = f"{here}/static"
        super().__init__(
            [
                ("/", IndexHandler, {}, "index.html"),
                ("/jobs.json", JobsHandler, {}, "jobs.json"),
                ("/counts.json", JobCountHandler, {}, "counts.json"),
                ("/summary.json", JobSummaryHandler, {}, "summary.json"),
                ("/(.*)", StaticFileHandler, {"path": static_path}),
            ],
            template_path=static_path,
            debug=debug,
        )
        self.simulate = simulate
        self.jobs: JobList = []
        self._refresh_timer = PeriodicCallback(
            self.refresh_jobs_list, timedelta(seconds=refresh_interval_seconds)
        )
        self._refresh_timer.start()

    async def refresh_jobs_list(self) -> None:
        """Refresh the list of jobs using ``condor_q`` (or a simulation)."""
        logger.debug("Refreshing jobs list")

        if self.simulate:
            self.jobs = simulate_jobs()
        else:
            self.jobs = await get_jobs()


async def main(
    *, port: int = 9100, debug: bool = False, simulate: bool = False
) -> None:
    """Main entry point.

    :param port: port to serve on (default: 9100)
    :param debug: enable debug mode
    :param simulate: simulate calls to ``condor_q``

    """
    if debug:
        logger.setLevel(logging.DEBUG)

    enable_pretty_logging()
    app = HTCondorStatusApp(debug=debug, simulate=simulate)
    app.listen(port)
    logger.info(f"Listening on port {port}")
    await app.refresh_jobs_list()
    await asyncio.Event().wait()
