import subprocess
from typing import Optional


class Generator:
    def __init__(self, exec_path: str):
        self.exec_path = exec_path

    def generate(self) -> Optional[bytes]:
        run_result = subprocess.run(f"{self.exec_path} -p".split(" "), stdout=subprocess.PIPE)
        if run_result.returncode == 0:
            return run_result.stdout
        else:
            return None
