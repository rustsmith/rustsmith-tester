import os
from typing import Dict

import docker
from halo import Halo

CONTAINER_LABEL = "rustsmith-worker"

def sanitize(s):
    return "".join(x for x in s if x.isalnum())

class DockerClient:
    config: Dict[str, int]
    client: docker.DockerClient

    def __init__(self, config: Dict[str, int]):
        self.config = config
        self.client = docker.from_env()

    def start_containers(self):
        with open("worker/Dockerfile", "r") as dockerfile:
            file = dockerfile.read()
        for version, count in self.config.items():
            updated_file = file.replace("RUSTMITH_VERSION", version)
            sanitized_name = sanitize(version)
            with open(f"worker/Dockerfile-{sanitized_name}", "w") as new_file:
                new_file.write(updated_file)
            with Halo(text=f"Running container for version {version}", spinner="dots") as halo:
                self.client.images.build(
                    dockerfile=f"Dockerfile-{sanitized_name}", tag=f"rustsmith-tester-{version}", path="worker", rm=True
                )
                for i in range(count):
                    self.client.containers.run(
                        image=f"rustsmith-tester-{version}",
                        detach=True,
                        network_mode="host",
                        restart_policy={"Name": "always"},
                        name=f"rustsmith-tester-{sanitized_name}-{i + 1}",
                        labels=[CONTAINER_LABEL],
                    )
                    halo.text = f"Running container for version {version} [{i + 1}/{count}]"
                halo.succeed()
            os.remove(f"worker/Dockerfile-{sanitized_name}")

    def stop_containers(self):
        containers = self.client.containers.list(all=True, filters={"label": CONTAINER_LABEL})
        for container in containers:
            with Halo(text=f"Stopping container {container.name}", spinner="dots") as halo:
                container.stop()
                container.remove()
                halo.succeed()
