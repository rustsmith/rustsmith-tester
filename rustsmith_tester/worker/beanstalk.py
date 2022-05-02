import time
from typing import List

import greenstalk


class Beanstalk:
    def __init__(self, tube: str):
        self.tube = tube
        self.client = greenstalk.Client(("127.0.0.1", 11300))
        self.client.watch(tube)
        print("Connected to beanstalk instance")

    def close(self):
        print("Closing beanstalk client")
        self.client.close()

    def poll(self) -> greenstalk.Job:
        self.client.use(self.tube)
        while True:
            try:
                return self.client.reserve(5)
            except:
                time.sleep(1)

    def delete(self, job: greenstalk.Job):
        try:
            self.client.use(self.tube)
            self.client.delete(job)
        except:
            print("Could not delete. Moving on...")

    def submit_bug(self, file: str, version: str, outputs: List[str]):
        self.client.use(f"bugs-{self.tube}")
        file += "\nRUST COMPILER VERSION {}\n".format(version)
        file += str(outputs)
        self.client.put(file)
        self.client.use(self.tube)
