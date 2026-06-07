import sys
from loguru import logger

# Configure logger: JSON output, level INFO, stream to stdout
logger.remove()
logger.add(sys.stdout, level="INFO", serialize=True, backtrace=False, diagnose=False)

def get_logger(name: str = "stt"):
    """Return a logger bound with a module name for easier filtering.

    Args:
        name: Identifier for the module emitting logs.
    """
    return logger.bind(module=name)
