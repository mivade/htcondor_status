import asyncio
import json
from subprocess import PIPE
from typing import Any, Dict, List


async def get_jobs(all: bool = True, global_: bool = True) -> List[Dict[str, Any]]:
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


if __name__ == "__main__":
    jobs = asyncio.run(get_jobs())
    print(jobs)
