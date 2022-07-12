from argparse import ArgumentParser, _SubParsersAction
import asyncio
import json
from pathlib import Path
import pkgutil
from typing import Optional

from nodejs import npm

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
    parser.set_defaults(command=generate_json)
    parser.add_argument("--indent", "-i", type=int, help="indent spaces")
    parser.add_argument("--file", "-f", type=str, help="where to write the output")
    return parser


def generate_json(*, file: Optional[str], indent: Optional[int]) -> None:
    """Generate a JSON file with job status.

    :param file: where to write the JSON file to (stdout if not None)

    """
    data = {"jobs": asyncio.run(jobs.get_jobs())}

    if file is None:
        print(json.dumps(data, indent=indent))
    else:
        with open(file, "w") as f:
            json.dump(data, f, indent=indent)


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

    for resource in ("condor.jpg", "condor.png", "favicon.ico", "index.html"):
        data = pkgutil.get_data("htcondor_status.static", resource)
        filepath = path.joinpath(resource)
        print(f"Writing {filepath}")
        filepath.write_bytes(data)


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
