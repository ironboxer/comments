from typing import Any, Dict, Optional, Union

from pydantic import AnyUrl, BaseSettings, validator


class MySQLDsn(AnyUrl):
    allowed_schemes = {'mysql'}


class Settings(BaseSettings):
    class Config:
        env_prefix = 'COMMENT_'
        env_file = '.env'
        env_file_encoding = 'utf-8'

    MYSQL_HOST: str = 'mysql'
    MYSQL_USER: str = 'root'
    MYSQL_PASSWORD: str = 'root'
    MYSQL_PORT: str = 3306
    MYSQL_DB: str = 'comment'

    SECRET_KEY: str = ''
    SQLALCHEMY_DATABASE_URI: Optional[MySQLDsn] = None
    SQLALCHEMY_ECHO: Union[bool, str] = False

    @validator('SQLALCHEMY_DATABASE_URI', pre=True)
    def generate_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return MySQLDsn.build(
            scheme='mysql',
            user=values.get('MYSQL_USER'),
            password=values.get('MYSQL_PASSWORD'),
            host=values.get('MYSQL_HOST'),
            port=values.get('MYSQL_PORT'),
            path=f'/{values.get("MYSQL_DB") or ""}',
        )

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
