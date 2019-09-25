from argparse import ArgumentParser, _SubParsersAction


def make_serve_parser(subparsers: _SubParsersAction) -> _SubParsersAction:
    """Make the ``serve`` subcommand."""
    parser = subparsers.add_parser("serve")
    parser.set_defaults(command=serve)
    parser.add_argument("--port", "-p", default=9100, help="port to listen on")
    parser.add_argument("--debug", action="store_true", help="enable debug mode")


def main() -> None:
    """Main CLI entry point."""
    parser = ArgumentParser(prog="htcondor_status")
    parser.set_defaults(command=lambda **_: parser.print_usage())
    subparsers = parser.add_subparsers()
    make_serve_parser(subparsers)
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


if __name__ == "__main__":
    main()
