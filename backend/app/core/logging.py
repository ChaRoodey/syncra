import logging
import sys

from app.core.config import settings

logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    fmt="%(levelname)s %(name)s %(message)s",
)

handler.setFormatter(formatter)
logger.addHandler(handler)
