from argparse import ArgumentParser, _SubParsersAction
import asyncio
import json
import os
from pathlib import Path
import shutil
from typing import Optional

from nodejs import npm

from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.testing import bind_unused_port

from htcondor_status import jobs, server


def make_serve_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Make the ``serve`` subcommand."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    parser.add_argument("--port", "-p", default=8500, help="port to listen on")
    parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")
    parser.add_argument(
        "--simulate", "-s", action="store_true", help="simulate calls to condor_q"
    )
    return parser


def serve(*, port: int, debug: bool, simulate: bool) -> None:
    """Run the server.

    :param port: port to serve on
    :param debug: when True, enable debug mode
    :param simulate: simulate ``condor_q`` calls

    """
    if debug:
        npm_run = npm.Popen(["run", "watch"])
    else:
        npm_run = None

    try:
        asyncio.run(server.main(port=port, debug=debug, simulate=simulate))
    except KeyboardInterrupt:
        if npm_run is not None:
            npm_run.terminate()


def make_json_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Make the ``json`` subcommand."""
    parser = subparsers.add_parser("json")
    parser.set_defaults(
        command=lambda *args, **kwargs: asyncio.run(generate_json(*args, **kwargs))
    )
    parser.add_argument("directory", type=str, help="directory to write JSON files to")
    return parser


async def generate_json(*, directory: Optional[str]) -> None:
    """Generate JSON files with job status information.

    :param directory: directory to write the JSON files to (default: CWD)

    """
    output_directory = directory or os.getcwd()
    sock, port = bind_unused_port()
    http_server = HTTPServer(server.HTCondorStatusApp())
    http_server.add_socket(sock)
    client = AsyncHTTPClient()

    for filename in ["jobs.json", "counts.json", "summary.json"]:
        response = await client.fetch(
            f"http://127.0.0.1:{port}/{filename}",
            headers={"Accept": "application/json"},
        )
        Path(output_directory, filename).write_bytes(response.body)


def make_static_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Make the ``static`` subcommand to write all static files."""
    parser = subparsers.add_parser("static")
    parser.set_defaults(command=write_static_files)
    parser.add_argument("directory", type=str, help="directory to write files to")
    return parser


def write_static_files(*, directory: str) -> None:
    """Write the static files to the given directory."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).parent
    shutil.rmtree(here / "static", ignore_errors=True)
    npm.run(["run", "build"])

    for filepath in here.joinpath("static").glob("*"):
        print(f"Copying {filepath} to {directory}")
        shutil.copy(filepath, directory)


def main() -> None:
    """Main CLI entry point."""
    parser = ArgumentParser(prog="htcondor_status")
    parser.set_defaults(command=lambda **_: parser.print_usage())
    subparsers = parser.add_subparsers()
    make_serve_parser(subparsers)
    make_json_parser(subparsers)
    make_static_parser(subparsers)
    namespace = parser.parse_args()
    args = vars(namespace)
    command = args.pop("command")
    command(**args)


if __name__ == "__main__":
    main()
