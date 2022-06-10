import subprocess
import typing
import time
import os
import re


class Command:
    def __init__(self, command: str, timeout: int):
        self.command = command
        self.timeout, self.elapsed_time, self.stdout, self.stderr = _executeCommand(command, timeout)


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
    try:
        if os.name == "nt" and command.split()[0].upper() in built_in_cmd_commands:
            # UTF-8 Codec can't decode bytes
            # https://stackoverflow.com/questions/64948722/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xbe-in-position-2-in
            # shell=True MUST NOT BE USED:
            # https://stackoverflow.com/questions/48763362/python-subprocess-kill-with-timeout
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
        end_time = time.time() - start_time
        return "", msg.strerror, timeout, end_time

    end_time = time.time() - start_time

    ansi_escape = re.compile(r'(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x1b\(|\x1b=|\x9B)[0-?]*[ -/]*[@-~])')
    if process.stdout:
        if not isinstance(process.stdout, str):
            stdout = process.stdout.decode("utf-8", "ignore")
            stdout = ansi_escape.sub('', stdout).replace("\n", "<br>")
            process.stdout = stdout
    else:
        process.stdout = ""

    if process.stderr:
        if not isinstance(process.stderr, str):
            stderr = process.stderr.decode("utf-8", "ignore")
            stderr = ansi_escape.sub('', stderr).replace("\n", "<br>")
            process.stderr = stderr
    else:
        process.stderr = ""

    return timeout, end_time, process.stdout, process.stderr
