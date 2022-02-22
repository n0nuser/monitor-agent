import subprocess
import psutil
import typing
import time
import os


class Command:
    def __init__(self, command: str, timeout: int):
        self.command = command
        self.stdout, self.stderr, self.timeout, self.elapsed_time = _executeCommand(
            command, timeout
        )


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
    end_time = 0.0
    built_in_cmd_commands = [
        "ASSOC",
        "BREAK",
        "CALL",
        "CD",
        "CHDIR",
        "CLS",
        "COLOR",
        "COPY",
        "DATE",
        "DEL",
        "DIR",
        "DPATH",
        "ECHO",
        "ENDLOCAL",
        "ERASE",
        "EXIT",
        "FOR",
        "FTYPE",
        "GOTO",
        "IF",
        "KEYS",
        "MD",
        "MKDIR",
        "MKLINK",
        "MOVE",
        "PATH",
        "PAUSE",
        "POPD",
        "PROMPT",
        "PUSHD",
        "REM",
        "REN",
        "RENAME",
        "RD",
        "RMDIR",
        "SET",
        "SETLOCAL",
        "SHIFT",
        "START",
        "TIME",
        "TITLE",
        "TYPE",
        "VER",
        "VERIFY",
        "VOL",
    ]
    start_time = time.time()
    proc = command.split()
    print(proc[0].upper())
    try:
        if os.name == "nt" and proc[0].upper() in built_in_cmd_commands:
            # UTF-8 Codec can't decode bytes
            # https://stackoverflow.com/questions/64948722/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xbe-in-position-2-in
            # shell=True MUST NOT BE USED:
            # https://stackoverflow.com/questions/48763362/python-subprocess-kill-with-timeout
            print("Windows CMD built-in.")
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                universal_newlines=True,
                shell=True,
                bufsize=100,
                check=True,
            )
        else:
            print("Linux or Windows command.")
            process = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                universal_newlines=True,
                shell=False,
                bufsize=100,
                check=True,
            )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as msg:
        process = msg
    except (ValueError, FileNotFoundError) as msg:
        end_time = round(time.time() - start_time, 2)
        return "", msg, timeout, end_time

    end_time = round(time.time() - start_time, 2)
    return process.stdout, process.stderr, timeout, end_time
