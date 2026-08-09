import logging

from rich.logging import RichHandler


def setup_logging() -> None:
    # 🎨 Configure readable terminal logs.
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%d %b %Y | %I:%M:%S %p]",
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                show_path=False,
            )
        ],
    )
