import asyncio
import logging
from pathlib import Path
from signal import SIGTERM, SIGINT

from tornado.log import enable_pretty_logging
from tornado.web import Application, RequestHandler

from .jobs import get_jobs

logger = logging.getLogger("__name__")


class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")


class JobsHandler(RequestHandler):
    async def get(self):
        jobs = await get_jobs()
        self.write({"jobs": jobs})


def make_app(debug: bool) -> Application:
    here = Path(__file__).parent
    app = Application(
        [(r"/", IndexHandler), (r"/jobs.json", JobsHandler)],
        static_path=str(here.joinpath("static")),
        template_path=str(here.joinpath("static")),
        debug=debug,
    )
    return app


def main(port: int = 9100, debug: bool = False) -> None:
    enable_pretty_logging()
    app = make_app(debug=debug)
    app.listen(port)
    logger.info(f"Listening on port {port}")
    loop = asyncio.get_event_loop()

    def shutdown():
        logger.info("Shutting down...")
        loop.stop

    for signal in (SIGTERM, SIGINT):
        loop.add_signal_handler(signal, loop.stop)

    loop.run_forever()


if __name__ == "__main__":
    main(debug=True)
