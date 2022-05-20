from typing import Any, Dict

from pydantic import BaseSettings


class Settings(BaseSettings):

    LOGGING: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                '()': 'logging.Formatter',
                'fmt': '[{levelname:1.1s} {asctime} {module}:{funcName}:{lineno}] {message}',  # noqa
                'style': '{',
            },
            'colored': {
                '()': 'colorlog.ColoredFormatter',
                'fmt': '{log_color}[{levelname:1.1s} {asctime} {module}:{funcName}:{lineno}] {message}',  # noqa
                'style': '{',
                'datefmt': '%H:%M:%S',
                'log_colors': {
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                },
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'colored',
            },
        },
        'loggers': {
            'comment': {'handlers': ['stdout'], 'level': 'DEBUG', 'propagate': False},
        },
    }


settings = Settings()
