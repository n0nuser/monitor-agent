from typing import List

import psutil
from monitor_agent.domain.entities.user import User
from monitor_agent.domain.services.os_functions.utils import timestamp_to_isoformat


def logged_users() -> List[User]:
    """Returns a list of logged users.

    Returns:
        List[User]: List of logged users.
    """
    return [
        User(
            username=user.name,
            terminal=user.terminal or None,
            host=user.host or None,
            started=timestamp_to_isoformat(user.started),
        )
        for user in psutil.users()
    ]
