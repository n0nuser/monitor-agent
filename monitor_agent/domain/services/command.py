import os
import re
import subprocess
import time
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Class to store the result of a command execution.
    - stdout (str): Standard Output of the command
    - stderr (str): Standard Error of the command
    - timeout (int): Maximum time the command can take to finish
    - elapsed_time (float): Time that the command took to finish
    """

    timeout: float
    elapsed_time: float
    stdout: str
    stderr: str


class Command:
    ANSI_ESCAPE = re.compile(
        r"(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x1b\(|\x1b=|\x9B)[0-?]*[ -/]*[@-~])"
    )

    def __init__(self, command: str, timeout: int):
        self.command = command
        self.timeout = timeout

    def __call__(self) -> CommandResult:
        start_time = time.time()

        try:
            if os.name == "nt":
                # UTF-8 Codec can't decode bytes
                # https://stackoverflow.com/questions/64948722/error-unicodedecodeerror-utf-8-codec-cant-decode-byte-0xbe-in-position-2-in
                # shell=True MUST NOT BE USED:
                # https://stackoverflow.com/questions/48763362/python-subprocess-kill-with-timeout
                process = subprocess.run(
                    self.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    universal_newlines=True,
                    bufsize=100,
                    check=True,
                )
            else:
                process = subprocess.run(
                    self.command.split(),
                    shell=False,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    universal_newlines=True,
                    bufsize=100,
                    check=True,
                )
            self._fix_output_process(process)
            return CommandResult(
                stdout=process.stdout,
                stderr=process.stderr,
                timeout=self.timeout,
                elapsed_time=time.time() - start_time,
            )
        except subprocess.CalledProcessError as msg:
            self._fix_output_process(msg)
            return CommandResult(
                stdout=str(msg.stdout),
                stderr=str(msg.stderr),
                timeout=self.timeout,
                elapsed_time=time.time() - start_time,
            )
        except subprocess.TimeoutExpired as msg:
            self._fix_output_process(msg)
            return CommandResult(
                stdout=str(msg.stdout),
                stderr=str(msg.stderr),
                timeout=float(msg.timeout),
                elapsed_time=time.time() - start_time,
            )
        except ValueError:
            return CommandResult(
                stdout="",
                stderr="",
                timeout=self.timeout,
                elapsed_time=time.time() - start_time,
            )
        except FileNotFoundError as msg:
            return CommandResult(
                stdout="",
                stderr=msg.strerror,
                timeout=self.timeout,
                elapsed_time=time.time() - start_time,
            )

    def _fix_output_process(self, process):
        """Fix the output of the process to remove ANSI escape characters.

        Args:
            process (Any): Process to fix the output. Must contain stdout and/or stderr attributes.
        """
        for std in ["stdout", "stderr"]:
            if not isinstance(getattr(process, std), str):
                output = getattr(process, std).decode("utf-8", "ignore")
                output = self.ANSI_ESCAPE.sub("", output).replace("\n", "<br>")
                output = self.ANSI_ESCAPE.sub("", getattr(process, std)).replace(
                    "\n", "<br>"
                )
                setattr(process, std, output)
