import asyncio
import json
from pathlib import Path
from io import TextIOWrapper

import aiohttp
import yaml

from verdandi.widget import ALL_WIDGETS
from verdandi.tests.conftest import get_mocked_http


DOCS_PATH = Path(__file__).parent.parent.parent / "doc"


async def docgen(http: aiohttp.ClientSession, docs_file: TextIOWrapper):
    print("Update widgets documentation in", DOCS_PATH)

    def line(*args):
        return print(*args, file=docs_file)

    for widget in ALL_WIDGETS:
        img = await widget.example().render(http)
        img.save(DOCS_PATH / "images" / (widget.name + ".png"))

        example_config = [
            {
                "name": widget.name,
                "config": json.loads(widget.example().model_dump_json()),
            }
        ]

        line("##", widget.__name__)
        line()
        line(f"![{widget.name}](./images/{widget.name}.png)")
        line()
        line("| | value |")
        line("|---|---|")
        line(f"| **name** | {widget.name} |")
        line(f"| **width** | {widget.width()} |")
        line(f"| **height** | {widget.height()} |")
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


async def main():
    with open(DOCS_PATH / "widgets.md", "wt") as f:
        async with get_mocked_http() as http:
            await docgen(http, f)


def run():
    asyncio.run(main())
