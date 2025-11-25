import asyncio
import json
import typing
from datetime import datetime
from io import TextIOWrapper
from pathlib import Path
from typing import Generator
from warnings import warn
from types import GenericAlias, EllipsisType

import aiohttp
import yaml
from pydantic.fields import FieldInfo

from verdandi.tests.conftest import get_mocked_http
from verdandi.widget import ALL_WIDGETS
from verdandi.widget.abs_widget import Widget
from verdandi.app import generate_canvas
from verdandi.configuration import ApiConfiguration

DOCS_PATH = Path(__file__).parent.parent.parent / "doc"

EXAMPLE_CONFIG_PATH = (
    Path(__file__).parent.parent
    / "verdandi"
    / "tests"
    / "fixtures"
    / "test-config.yaml"
)


def iter_fields_flattened(
    obj_type: type[Widget],
    parents: tuple = (),
) -> Generator[tuple[tuple[str, ...], FieldInfo]]:
    for name, field in obj_type.model_fields.items():
        field_parents = parents + (name,)

        if isinstance(field.annotation, GenericAlias):
            match typing.get_args(field.annotation):
                case (inside, EllipsisType()):
                    field_parents = parents + (f"{name}[]",)
                    yield from iter_fields_flattened(inside, field_parents)
                case _:
                    warn("Type %s is not yet supported for %s", ".".join(field_parents))
        elif hasattr(field.annotation, "model_fields"):
            yield from iter_fields_flattened(field.annotation, field_parents)
        else:
            yield field_parents, field


async def generate_documentation(http: aiohttp.ClientSession, docs_file: TextIOWrapper):
    print("Update widgets documentation in", DOCS_PATH)

    def line(*args):
        return print(*args, file=docs_file)

    for widget in ALL_WIDGETS:
        assert issubclass(widget, Widget)
        img = await widget.example().render(http)
        img.save(DOCS_PATH / "images" / "widgets" / (widget.name + ".png"))

        example_config = [
            {
                "name": widget.name,
                "config": json.loads(widget.example().model_dump_json()),
            }
        ]

        line("##", widget.__name__)
        line()
        line(f"![{widget.name}](./images/widgets/{widget.name}.png)")
        line()
        line("| | value |")
        line("|---|---|")
        line(f"| **name** | {widget.name} |")
        line(f"| **width** | {widget.width()} |")
        line(f"| **height** | {widget.height()} |")
        line()
        line("### Configuration parameters")
        line()
        line("| param | type | description |")
        line("|---|---|---|")

        for parents, field in iter_fields_flattened(widget):
            name = ".".join(parents)
            description = field.description or ""
            type_str = getattr(field.annotation, "__name__", "")
            line(f"| **{name}** | {type_str} | {description} |")

        line()
        line("### Configuration Example")
        line()
        line("```yaml")

        line(
            yaml.dump(
                example_config,
                sort_keys=False,
                Dumper=getattr(yaml, "CSafeDumper", yaml.SafeDumper),
            )
        )

        line("```")


async def generate_example():
    path = DOCS_PATH / "images" / "example.png"
    print("Generate example at", path)

    async with get_mocked_http():
        now = datetime.now().astimezone()
        resp = await generate_canvas(ApiConfiguration.load(EXAMPLE_CONFIG_PATH), now)

    with open(path, "wb") as f:
        f.write(resp.body)


async def main():
    await generate_example()

    with open(DOCS_PATH / "widgets.md", "wt") as f:
        async with get_mocked_http() as http:
            await generate_documentation(http, f)


def run():
    asyncio.run(main())
