import logging

from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from comment.__version__ import __version__
from comment.config import settings
from comment.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

logging.config.dictConfig(settings.LOGGING)

app = FastAPI(
    title='Comment System',
    version=__version__,
)

app.router.redirect_slashes = False


@app.get('/healthz', response_class=HTMLResponse)
async def health():
    """For Health Check"""
    return ''


@app.middleware('http')
async def handle_http204(request: Request, call_next):
    """Return empty content when status set to 204

    FastAPI (starlette) doesn't handle this properly
    https://github.com/tiangolo/fastapi/issues/449#issuecomment-761838535
    """
    response = await call_next(request)

    if response.status_code == status.HTTP_204_NO_CONTENT:
        return Response(status_code=204)

    return response


@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    # fixup
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + ' - Swagger UI',
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url='https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js',
        swagger_css_url='https://unpkg.com/swagger-ui-dist@3/swagger-ui.css',
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get('/redoc', include_in_schema=False)
async def custom_redoc_html():
    # fixup
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + ' - ReDoc',
        redoc_js_url='https://unpkg.com/redoc@2.0.0-rc.58/bundles/redoc.standalone.js',
    )
