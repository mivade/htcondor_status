import asyncio
import logging
from pathlib import Path

from tornado.log import enable_pretty_logging
from tornado.web import Application, RequestHandler

from .jobs import get_jobs

logger = logging.getLogger("__name__")


class IndexHandler(RequestHandler):
    def get(self) -> None:
        """Get ``index.html``."""
        self.render("index.html")


class JobsHandler(RequestHandler):
    async def get(self) -> None:
        """Get the most recent list of HTCondor jobs."""
        jobs = await get_jobs()
        self.write({"jobs": jobs})


def make_app(debug: bool) -> Application:
    """Make the Tornado web application.

    :param debug: enable debug mode

    """
    here = Path(__file__).parent
    app = Application(
        [
            (r"/", IndexHandler, {}, "index.html"),
            (r"/jobs.json", JobsHandler, {}, "jobs.json"),
        ],
        static_path=str(here.joinpath("static")),
        template_path=str(here.joinpath("static")),
        debug=debug,
    )
    return app


async def main(*, port: int = 9100, debug: bool = False) -> None:
    """Main entry point.

    :param port: port to serve on (default: 9100)
    :param debug: enable debug mode

    """
    enable_pretty_logging()
    app = make_app(debug=debug)
    app.listen(port)
    logger.info(f"Listening on port {port}")
    await asyncio.Event().wait()
