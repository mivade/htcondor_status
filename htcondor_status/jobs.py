import asyncio
import importlib.resources
import json
import random
from subprocess import PIPE
from typing import Any

JobList = list[dict[str, Any]]


async def get_jobs(all: bool = True, global_: bool = True) -> JobList:
    """Get a list of jobs using ``condor_q``.

    :param all: include the ``-all`` option (default: True)
    :param global_: include the ``-global`` option (default: True)

    """
    args = ["condor_q", "-json"]

    if global_:
        args.append("-global")

    if all:
        args.append("-all")

    p = await asyncio.create_subprocess_exec(*args, stdout=PIPE)
    out, _ = await p.communicate()

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def _read_sample_data() -> JobList:
    data = importlib.resources.read_text(
        "htcondor_status", "sample_condor_q_output.json"
    )
    return json.loads(data)


def simulate_jobs() -> JobList:
    """Simulate getting jobs from ``condor_q``."""
    data = _read_sample_data()
    total = len(data)
    return random.sample(data, k=random.randint(1, total - 1))


if __name__ == "__main__":
    jobs = asyncio.run(get_jobs())
    print(jobs)
