import asyncio
import base64

import aiohttp
import yaml

from verdandi.util.image import image_to_bytes
from verdandi.widget import ALL_WIDGETS


async def docgen(http: aiohttp.ClientSession):
    for widget in ALL_WIDGETS:
        img = await widget.example().render(http)
        img_data = image_to_bytes(img)
        b64_data = base64.b64encode(img_data).decode("utf8")

        example_config = [
            {
                "name": widget.name,
                "config": widget.example().dict(),
            }
        ]

        print("##", widget.__name__)
        print()
        print(f"![{widget.name}](data:image/png;base64,{b64_data})")
        print()
        print("| | value |")
        print("|---|---|")
        print(f"| **name** | {widget.name} |")
        print(f"| **width** | {widget.width()} |")
        print(f"| **height** | {widget.height()} |")
        print()
        print("### Configuration Example")
        print()
        print("```yaml")

        print(
            yaml.dump(
                example_config,
                sort_keys=False,
                Dumper=getattr(yaml, "CSafeDumper", yaml.SafeDumper),
            )
        )

        print("```")


async def main():
    connector = aiohttp.TCPConnector(ssl=False)  # todo: is this a nixos issue?

    async with aiohttp.ClientSession(connector=connector) as http:
        await docgen(http)


def run():
    asyncio.run(main())
