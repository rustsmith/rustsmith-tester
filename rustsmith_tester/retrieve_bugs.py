import time

import greenstalk
import uuid

from rustsmith_tester.config import config

client = greenstalk.Client(("127.0.0.1", 11300))


def get_files_from_bug_tube(version: str):
    tube_name = f"bugs-{version}"
    client.use(tube_name)
    client.watch(tube_name)
    bug_files_total = client.stats_tube(tube_name)['current-jobs-ready']
    for i in range(bug_files_total):
        file_name = f"{tube_name}-{uuid.uuid4()}.txt"
        print("Retrieving job...")
        job = client.reserve()
        print("Job retrieved...")
        f = open(file_name, "w")
        f.write(str(job.body))
        f.close()
        time.sleep(2)


for k, v in config["versions"].items():
    get_files_from_bug_tube(k)
