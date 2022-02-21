import subprocess
import typing
import time
import os

class Command:
    def __init__(self, command: str, timeout: int):
        self.command = command
        self.stdout, self.stderr, self.timeout, self.elapsed_time = _executeCommand(command, timeout)


def _executeCommand(command: str, timeout: int) -> typing.Tuple[str, str, int, float]:
    """Executes a command in a maximum time set by a timeout.

    Args:
        command (str): Command to execute
        timeout (int): Maximum time the command can take to finish

    Returns:
        stdout (str): Standard Output of the command
        stderr (str): Standard Error of the command
        timeout (int): Maximum time the command can take to finish
        elapsed_time (float): Time that the command took to finish
    """    
    # You should NOT use shell=True on Linux:
    # os.path.expandvars("$PATH")
    end_time = 0.0
    start_time = time.time()
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
        return "", str(msg), timeout, round(time.time() - start_time, 2)
    except FileNotFoundError as msg:
        return "", str(msg), timeout, round(time.time() - start_time, 2)
    
    end_time = round(time.time() - start_time, 2)
    try:
        return process.stdout, process.stderr, process.timeout, end_time
    except AttributeError:
        return process.stdout, process.stderr, timeout, end_time
