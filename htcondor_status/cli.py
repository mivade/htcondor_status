from argparse import ArgumentParser, _SubParsersAction
from typing import Optional


def make_serve_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Make the ``serve`` subcommand."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    parser.add_argument("--port", "-p", default=9100, help="port to listen on")
    parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")
    return parser


def make_json_parser(subparsers: _SubParsersAction) -> ArgumentParser:
    """Make the ``json`` subcommand."""
    parser = subparsers.add_parser("json")
    parser.set_defaults(command=generate_json)
    parser.add_argument("--indent", "-i", type=int, help="indent spaces")
    parser.add_argument("--file", "-f", type=str, help="where to write the output")
    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = ArgumentParser(prog="htcondor_status")
    parser.set_defaults(command=lambda **_: parser.print_usage())
    subparsers = parser.add_subparsers()
    make_serve_parser(subparsers)
    make_json_parser(subparsers)
    namespace = parser.parse_args()
    args = vars(namespace)
    command = args.pop("command")
    command(**args)


def serve(*, port: int, debug: bool) -> None:
    """Run the server.

    :param port: port to serve on
    :param debug: when True, enable debug mode

    """
    from htcondor_status.server import main

    main(port, debug)


def generate_json(*, file: Optional[str], indent: Optional[int]) -> None:
    """Generate a JSON file with job status.

    :param file: where to write the JSON file to (stdout if not None)

    """
    import asyncio
    import json
    from htcondor_status.jobs import get_jobs

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(get_jobs())

    if file is None:
        print(json.dumps(data, indent=indent))
    else:
        with open(file, "w") as f:
            json.dump(data, f, indent=indent)


if __name__ == "__main__":
    main()
