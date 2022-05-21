from logging import Filter

from comment.main import app

URL_PATH_HEALTH_CHECK = app.url_path_for('health')


class HealthCheckFilter(Filter):
    def filter(self, record):
        return URL_PATH_HEALTH_CHECK not in record.args
