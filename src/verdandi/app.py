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
from simpleeval import simple_eval

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
async def _generate_canvas(configuration: ApiConfiguration):
    now = datetime.now()

    # Render all widgets concurently
    connector = aiohttp.TCPConnector(ssl=False)  # TODO: is this a NixOS issue?

    async with aiohttp.ClientSession(connector=connector) as http:
        widget_imgs = await asyncio.gather(
            *(widget.config.render(http) for widget in configuration.widgets)
        )

    # Paste rendered widgets to appropriate locations in a canvas
    img = Image.new(mode="L", size=configuration.size, color=CW)

    for widget, widget_img in zip(configuration.widgets, widget_imgs):
        is_displayed = simple_eval(
            widget.when,
            names={
                "now": {
                    "hour": now.hour,
                    "minute": now.minute,
                    "weekday": now.weekday(),
                    "month": now.month,
                    "day": now.day,
                }
            },
        )

        if not isinstance(is_displayed, bool):
            logger.warning("`when` does not evaluate to bool for %s", widget.name)

        if is_displayed:
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

    task = asyncio.create_task(
        _generate_canvas(state.configuration),
        name=f"generate-canvas-{entry_id}",
    )

    await state.set_response(entry_id, task)

    if wait:
        await task

    return RedirectResponse(
        filename=str(entry_id),
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
    return await _generate_canvas(state.configuration)
