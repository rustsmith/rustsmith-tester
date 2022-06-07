import argparse

from rustsmith_tester.config import config
from rustsmith_tester.kicker.docker_client import DockerClient

parser = argparse.ArgumentParser(description="Start and stop workers in docker containers")
parser.add_argument("command", type=str, help="Command to kicker (start, stop)")

args = parser.parse_args()
docker = DockerClient(config["versions"])

if args.command == "start":
    docker.start_containers()
elif args.command == "stop":
    docker.stop_containers()
else:
    print("Command not found")
    exit(1)
