from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DIR_DATA = Path(__file__).parent.parent.parent / "static"

executor = ThreadPoolExecutor(max_workers=4)
