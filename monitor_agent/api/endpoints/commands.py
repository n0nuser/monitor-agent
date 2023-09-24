@api.post(endpoints["command"])
async def command(
    command: str,
    timeout: int,
) -> dict:
    """Executes a command and returns the output.

    Args:
        command (str): Command as string.
        timeout (int): Timeout in seconds for the command to finish.
        credentials (HTTPBasicCredentials, optional): Credentials. Defaults to Depends(security).

    Returns:
        dict: A dictionary with the output of the command.
    """
    return Command(command, timeout).__dict__
