import signal

from beanstalk import Beanstalk
from generator import Generator
from rustsmith_tester.conifg import config

beanstalk = Beanstalk(list(config.keys()))
generator = Generator("/Users/mayank/Documents/RustSmith/run/rustsmith")

beanstalk.start()


def handler(signo, frame):
    beanstalk.kill()
    exit(0)


signal.signal(signal.SIGINT, handler)

files_generated = 0
while True:
    file = generator.generate()
    files_generated += 1
    print(f"Files generated: {files_generated}", end="\r")
    beanstalk.add_file_to_queue(file)
