import dataclasses
import json
import subprocess
import threading
from typing import List, Optional

import docker
import greenstalk
from halo import Halo

from rustsmith_tester.master.generator import RustSmithOutput
from rustsmith_tester.master.utils import is_port_in_use

def sanitize(s):
    return "".join(x for x in s if x.isalnum())

class Beanstalk:
    tubes: List[str]
    process: Optional[subprocess.Popen]
    client: Optional[greenstalk.Client]
    docker: docker.DockerClient
    put_lock: threading.Lock

    def __init__(self, tubes: List[str]):
        self.tubes = tubes
        self.put_lock = threading.Lock()
        self.docker = docker.from_env()

    def start(self):
        if not is_port_in_use(11300):
            with Halo(text="Starting beanstalk", spinner="dots") as halo:
                self.docker.containers.run(
                    image="schickling/beanstalkd",
                    command=["-z", "8096000"],
                    restart_policy={"Name": "always"},
                    detach=True,
                    name=f"rustsmith-tester-beanstalkd",
                    ports={"11300/tcp": 11300, "11300/udp": 11300},
                )
                halo.succeed()
        with Halo(text="Connected to beanstalk instance", spinner="dots") as halo:
            self.client = greenstalk.Client(("0.0.0.0", 11300))
            halo.succeed()

    def all_empty(self):
        print(self.client.stats())

    def kill(self):
        with Halo(text="Closing connection to beanstalk instance", spinner="dots") as halo:
            self.client.close()
            halo.succeed()

    def put_file_in_tube(self, rustsmith_output: RustSmithOutput, tube: str):
        self.client.use(sanitize(tube))
        self.client.put(json.dumps(dataclasses.asdict(rustsmith_output)))

    def add_file_to_queue(self, rustsmith_output: RustSmithOutput):
        self.put_lock.acquire()
        for tube in self.tubes:
            self.put_file_in_tube(rustsmith_output, tube)
        self.put_lock.release()
