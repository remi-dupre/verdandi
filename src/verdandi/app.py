import logging
import asyncio
from uuid import UUID, uuid4
from typing import Annotated

from PIL import Image
from fastapi import FastAPI, Response, Path, Query
from pydantic import BaseModel, Field

from verdandi.state import DepState
from verdandi.configuration import configuration
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
async def _generate_canvas():
    # Render all widgets concurently
    widget_imgs = await asyncio.gather(
        *(widget.config.render() for widget in configuration.widgets)
    )

    # Paste rendered widgets to appropriate locations in a canvas
    img = Image.new(mode="1", size=configuration.size, color=1)

    for widget, widget_img in zip(configuration.widgets, widget_imgs):
        img.paste(widget_img, widget.position)

    # Encode image to a buffer and respond
    return Response(
        content=image_to_bytes(img),
        media_type="image/png",
    )


class PrepareResponse(BaseModel):
    entry_id: Annotated[
        UUID,
        Field(title="Unique identifier for the generated canvas."),
    ]

    ready: Annotated[
        bool,
        Field(title="Wether the canvas is already ready to be fetched."),
    ]


@app.get(
    "/canvas/new/",
    tags=["canvas"],
    description="Start the generation of a new canvas.",
)
async def canvas_prepare(
    state: DepState,
    wait: Annotated[
        bool,
        Query(title="Wait for the canvas to be ready before returning"),
    ] = False,
) -> PrepareResponse:
    entry_id = uuid4()
    task = asyncio.create_task(_generate_canvas(), name=f"generate-canvas-{entry_id}")
    await state.set_response(entry_id, task)

    if wait:
        await task

    return PrepareResponse(
        entry_id=entry_id,
        ready=task.done(),
    )


@app.get(
    "/canvas/get/{entry_id}/",
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
    return await _generate_canvas()
