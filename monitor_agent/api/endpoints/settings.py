from typing import Annotated

from litestar import MediaType, post
from litestar.status_codes import HTTP_204_NO_CONTENT
from litestar.params import Body

from monitor_agent.settings import Settings


@post(path="/", media_type=MediaType.JSON, status_code=HTTP_204_NO_CONTENT)
async def mod_settings(
    settings: Annotated[
        Settings, Body(title="Settings", description="Update the settings.")
    ],
) -> None:
    """Endpoint for modifying the settings.

    Args:
        settings (Annotated[Settings, Body, optional)].
    """
    settings.write_settings()
