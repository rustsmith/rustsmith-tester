import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class RustSmithOutput:
    code: str
    inputs: str


class Generator:
    def __init__(self, exec_path: str):
        self.exec_path = exec_path

    def generate(self) -> Optional[RustSmithOutput]:
        run_result = subprocess.run(f"{self.exec_path} -p".split(" "), stdout=subprocess.PIPE)
        if run_result.returncode == 0:
            stdout = str(run_result.stdout, 'utf-8').strip('\'')
            # Last line of the output are the inputs to pass in when executing binary
            code = stdout[:stdout.rfind('\n')]
            inputs = stdout.split("\n")[-1]
            return RustSmithOutput(code, inputs)
        else:
            return None
