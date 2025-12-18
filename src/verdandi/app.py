import logging
import asyncio
import os
from datetime import datetime
from uuid import UUID, uuid4
from typing import Annotated

import aiohttp
from PIL import Image
from fastapi import FastAPI, Response, Path, Query
from pydantic import BaseModel, AnyHttpUrl

from verdandi.util.color import CW
from verdandi.state import DepState
from verdandi.configuration import ApiConfiguration
from verdandi.util.logging import async_log_duration
from verdandi.util.image import image_to_bytes

logger = logging.getLogger(__name__)

app = FastAPI(
    openapi_tags=[
        {
            "name": "canvas",
            "description": "Generate a new canvas through an asynchronous API.",
        },
    ]
)


@async_log_duration(logger, "Canvas generation")
async def generate_canvas(configuration: ApiConfiguration, now: datetime):
    # Render all widgets concurently
    connector = aiohttp.TCPConnector(ssl=False)  # TODO: is this a NixOS issue?

    displayed_widgets = [
        widget for widget in configuration.widgets if widget.is_displayed_at(now)
    ]

    async with aiohttp.ClientSession(connector=connector) as http:
        widget_imgs = await asyncio.gather(
            *(widget.config.render(http) for widget in displayed_widgets)
        )

    # Paste rendered widgets to appropriate locations in a canvas
    img = Image.new(mode="L", size=configuration.size, color=CW)

    for widget, widget_img in zip(displayed_widgets, widget_imgs):
        img.paste(widget_img, widget.position)

    # Encode image to a buffer and respond
    return Response(
        content=image_to_bytes(img),
        media_type="image/png",
    )


class RedirectResponse(BaseModel):
    """
    Response specified by trmnl's redirect API.
    See https://help.usetrmnl.com/en/articles/11035846-redirect-plugin
    """

    filename: str
    url: AnyHttpUrl
    refresh_rate: int = 30 * 60


@app.get(
    "/canvas/redirect/",
    tags=["canvas"],
    description="Start the generation of a new canvas.",
)
async def canvas_prepare(
    state: DepState,
    wait: Annotated[
        bool,
        Query(title="Wait for the canvas to be ready before returning"),
    ] = False,
) -> RedirectResponse:
    entry_id = uuid4()
    now = datetime.now().astimezone()

    task = asyncio.create_task(
        generate_canvas(state.configuration, now),
        name=f"generate-canvas-{entry_id}",
    )

    await state.set_response(entry_id, task)

    if wait:
        await task

    # Check next update time
    next_update = min(
        widget.config.next_update(now)
        for widget in state.configuration.widgets
        if widget.is_displayed_at(widget.config.next_update(now))
    )

    refresh_rate = max(
        60.0,
        (next_update - now).total_seconds(),
    )

    logger.info("Next update at %s", next_update.isoformat())

    return RedirectResponse(
        filename=f"{entry_id}.png",
        refresh_rate=int(refresh_rate),
        url=AnyHttpUrl(
            os.path.join(
                str(state.configuration.base_url),
                f"canvas/redirect-get/{entry_id}/",
            )
        ),
    )


@app.get(
    "/canvas/redirect-get/{entry_id}/",
    tags=["canvas"],
    description="Wait to retreive the new canvas.",
)
async def canvas_retreive(
    state: DepState,
    entry_id: Annotated[UUID, Path()],
):
    resp = await state.get_response(entry_id)

    if resp is None:
        return Response(
            "Could not find this entry ID",
            status_code=404,
        )

    return await state.get_response(entry_id)


@app.get(
    "/canvas/direct/",
    tags=["canvas"],
    description="Generate and wait for a new canvas.",
)
async def canvas_direct(
    state: DepState,
):
    now = datetime.now().astimezone()
    return await generate_canvas(state.configuration, now)
