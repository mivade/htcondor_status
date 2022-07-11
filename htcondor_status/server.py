import asyncio
from datetime import timedelta
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from tornado.ioloop import PeriodicCallback
from tornado.log import enable_pretty_logging
from tornado.web import Application, RequestHandler

from .jobs import get_jobs, simulate_jobs

logger = logging.getLogger("__name__")


class IndexHandler(RequestHandler):
    def get(self) -> None:
        """Get ``index.html``."""
        self.render("index.html")


class JobsHandler(RequestHandler):
    def get(self) -> None:
        """Get the most recent list of HTCondor jobs."""
        self.write({"jobs": self.application.jobs})


class JobCountHandler(RequestHandler):
    def get(self) -> None:
        """Get counts of jobs in different states."""
        jobs = pd.DataFrame(self.application.jobs)
        self.write(
            {
                "total": len(jobs),
                "idle": len(jobs[jobs.JobStatus == 1]),
                "running": len(jobs[jobs.JobStatus == 2]),
                "held": len(jobs[jobs.JobStatus == 5]),
            }
        )


class JobSummaryHandler(RequestHandler):
    def get(self) -> None:
        """Get data needed only to render a table with job summary info."""
        jobs = pd.DataFrame(self.application.jobs)
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
        super().__init__(
            [
                ("/", IndexHandler, {}, "index.html"),
                ("/jobs.json", JobsHandler, {}, "jobs.json"),
                ("/counts.json", JobCountHandler, {}, "counts.json"),
                ("/summary.json", JobSummaryHandler, {}, "summary.json"),
            ],
            static_path=str(here.joinpath("static")),
            template_path=str(here.joinpath("static")),
            debug=debug,
        )
        self.simulate = simulate
        self.jobs: list[dict[str, Any]] = []
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
