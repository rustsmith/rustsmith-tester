import os
import signal
import subprocess
import time

from beanstalk import Beanstalk

rustc_version = os.environ["RUSTC_VERSION"]
beanstalk = Beanstalk(rustc_version)


def handler(signo, frame):
    beanstalk.close()
    os.remove("temp.rs")
    os.remove("out")
    exit(0)


signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

files_processed = 0
while True:
    job = beanstalk.poll()
    with open("temp.rs", "w") as temp_file:
        temp_file.write(str(job.body))
    optimization_flags = ["0", "1", "2", "3", "s", "z"]
    outputs = []
    for flag in optimization_flags:
        command = "rustc -C opt-level={} temp.rs -o out".format(flag)
        result = subprocess.run(command.split(" "), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if result.returncode == 0:
            try:
                run_result = subprocess.run("./out", stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5.0)
                output = run_result.stdout.decode()
                output += run_result.stderr.decode()
                output += "Exit Code {}".format(run_result.returncode)
                outputs.append(output)
            except subprocess.TimeoutExpired:
                outputs.append("Timeout")
        else:
            outputs.append("Compile Error")
    all_same = all(x == outputs[0] for x in outputs)
    if not all_same:
        print("BUG FOUND!")
        print(str(job.body))
        beanstalk.submit_bug(str(job.body), rustc_version, outputs)
        time.sleep(1)
    beanstalk.delete(job)
    files_processed += 1
    print("Files processed {}".format(files_processed))
