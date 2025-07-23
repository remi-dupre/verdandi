import asyncio
from verdandi.widget import ALL_WIDGETS


async def main():
    for widget in ALL_WIDGETS:
        print(widget.name)
        print(widget.example().model_dump_json())
        img = await widget.example().render()
        img.save(widget.name + ".png")


if __name__ == "__main__":
    asyncio.run(main())
