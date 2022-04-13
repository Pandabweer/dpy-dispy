import logging
import sys
from logging import handlers
from pathlib import Path

import coloredlogs

from constants import config

log_level = logging.DEBUG if config.debug.state else logging.INFO

# Log format
log_format = '%(asctime)s [%(levelname)s] - [%(filename)s > %(funcName)s() > %(lineno)s]: %(message)s'
log_date_format = '%m/%d/%Y|%I:%M:%S %p'

# Info color/format logger
fieldstyle = {
    "asctime": {"color": "green"},
    "levelname": {
        "bold": True,
        "color": "black"
    },
    "filename": {"color": "cyan"},
    "funcName": {"color": "blue"}
}

# Message color/format logger
levelstyles = {
    "critical": {
        "bold": True,
        "color": "red"
    },
    "debug": {"color": "green"},
    "error": {"color": "red"},
    "info": {"color": "magenta"},
    "warning": {"color": "yellow"}
}

# Creating logger
log = logging.getLogger(__name__)
log.setLevel(log_level)

streamhdlr = logging.StreamHandler(sys.stdout)
log.addHandler(streamhdlr)

if config.debug.log_file:
    # File handler
    log_file = Path("logs", "bot.log")
    log_file.parent.mkdir(exist_ok=True)
    file_handler = handlers.RotatingFileHandler(log_file, maxBytes=5242880, backupCount=7, encoding="utf8")
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(log_level)
    log.addHandler(file_handler)

coloredlogs.install(
    level=log_level,
    logger=log,
    fmt=log_format,
    datefmt=log_date_format,
    field_styles=fieldstyle,
    level_styles=levelstyles
)
