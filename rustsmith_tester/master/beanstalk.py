import subprocess
import threading
from time import sleep
from typing import List, Optional

import greenstalk
from halo import Halo

from rustsmith_tester.master.utils import is_port_in_use


class Beanstalk:
    tubes: List[str]
    process: Optional[subprocess.Popen]
    client: Optional[greenstalk.Client]
    put_lock: threading.Lock

    def __init__(self, tubes: List[str]):
        self.tubes = tubes
        self.put_lock = threading.Lock()

    def start(self):
        if not is_port_in_use(11300):
            with Halo(text="Starting beanstalk", spinner="dots") as halo:
                self.process = subprocess.Popen(
                    ["beanstalkd", "-l", "0.0.0.0", "-p", "11300", "-z", "8096000"], start_new_session=True
                )
                sleep(1)
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

    def put_file_in_tube(self, file: bytes, tube: str):
        self.client.use(tube)
        self.client.put(file)

    def add_file_to_queue(self, file: bytes):
        self.put_lock.acquire()
        for tube in self.tubes:
            self.put_file_in_tube(file, tube)
        self.put_lock.release()