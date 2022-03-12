import sys
from datetime import datetime

LOG_FILE = "monitor-agent.log"
MODE = "a+"


def save2log(filename: str = LOG_FILE, mode: str = MODE, data="", type=""):
    try:
        with open(filename, mode) as f:
            timestamp = datetime.now().strftime("%d/%m/%Y:%H:%M:%S")
            f.write(f"{type} - - [{timestamp}] : {data}\n")
    except OSError as msg:
        print(f"ERROR: Couldn't open file {filename} - {msg}", file=sys.stderr)
