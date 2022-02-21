import subprocess

# import os


class Command:
    def __init__(self, command: str, timeout: int):
        self.command = command
        self.stdout, self.stderr, self.timeout = _executeCommand(command, timeout)


def _executeCommand(command: str, timeout: int):
    # You should NOT use shell=True:
    # os.path.expandvars("$PATH")
    try:
        process = subprocess.run(command.split(), capture_output=True, timeout=timeout)
    except subprocess.CalledProcessError as msg:
        process = msg
    except subprocess.TimeoutExpired as msg:
        process = msg
    except ValueError as msg:
        return None, str(msg), -1, timeout
    except FileNotFoundError as msg:
        return None, str(msg), -1, timeout
    return process.stdout, process.stderr, process.timeout if process.timeout else timeout
