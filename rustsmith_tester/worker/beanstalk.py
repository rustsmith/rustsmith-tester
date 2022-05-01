from typing import Optional, List

import greenstalk


class Beanstalk:
    def __init__(self, tube: str):
        self.tube = tube
        self.client = greenstalk.Client(("host.docker.internal", 11300))
        self.client.watch(tube)
        print("Connected to beanstalk instance")

    def close(self):
        print("Closing beanstalk client")
        self.client.close()

    def poll(self) -> greenstalk.Job:
        self.client.use(self.tube)
        return self.client.reserve()

    def delete(self, job: greenstalk.Job):
        self.client.delete(job)

    def submit_bug(self, file: str, version: str, outputs: List[str]):
        self.client.use("bugs")
        file += "\nRUST COMPILER VERSION {}\n".format(version)
        file += str(outputs)
        self.client.put(file)
