import subprocess
import os


class Command:
    def __init__(self, command: str, timeout: int):
        self.command = command
        self.stdout, self.stderr, self.timeout = _executeCommand(command, timeout)


def _executeCommand(command: str, timeout: int):
    # You should NOT use shell=True on Linux:
    # os.path.expandvars("$PATH")
    try:
        if os.name == 'nt':
            # UTF-8 Codec can't decode bytes
            # https://stackoverflow.com/questions/64948722/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xbe-in-position-2-in
            process = subprocess.run(command.split(), capture_output=True, timeout=timeout, universal_newlines=True, shell=True)
        else:
            process = subprocess.run(command.split(), capture_output=True, timeout=timeout, universal_newlines=True)
    except subprocess.CalledProcessError as msg:
        process = msg
    except subprocess.TimeoutExpired as msg:
        process = msg
    except ValueError as msg:
        return None, str(msg), timeout
    except FileNotFoundError as msg:
        return None, str(msg), timeout
    
    try:
        return process.stdout, process.stderr, process.timeout
    except AttributeError:
        return process.stdout, process.stderr, timeout
