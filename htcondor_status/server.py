import asyncio
from pathlib import Path
from signal import SIGTERM, SIGINT

from tornado.log import enable_pretty_logging
from tornado.web import Application, RequestHandler

from .jobs import get_jobs

HERE = Path(__file__).parent


class IndexHandler(RequestHandler):
    def get(self):
        self.render("jobs.html")


class JobsHandler(RequestHandler):
    async def get(self):
        jobs = await get_jobs()
        self.write({"jobs": jobs})


def make_app(debug: bool) -> Application:
    app = Application(
        [(r"/", IndexHandler), (r"/jobs.json", JobsHandler)],
        static_path=str(HERE.joinpath("static")),
        template_path=str(HERE.joinpath("static")),
        debug=debug,
    )
    return app


def main(port: int = 9100, debug: bool = False) -> None:
    app = make_app(debug=debug)
    app.listen(port)
    loop = asyncio.get_event_loop()

    for signal in (SIGTERM, SIGINT):
        loop.add_signal_handler(signal, loop.stop)

    loop.run_forever()


if __name__ == "__main__":
    enable_pretty_logging()
    main(debug=True)
