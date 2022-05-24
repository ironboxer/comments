import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from comment import routers
from comment.__version__ import __version__
from comment.bootstrap import bootstrap
from comment.config import settings
from comment.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from comment.exceptions import (
    BaseCustomError,
    ErrorCode,
    ErrorResponseScheme,
    custom_errors,
)

logging.config.dictConfig(settings.LOGGING)

LOGGER = logging.getLogger(__name__)

app = FastAPI(
    title='Comment System',
    version=__version__,
    docs_url=None,
    redoc_url=None,
    responses={status.HTTP_400_BAD_REQUEST: {'model': ErrorResponseScheme}},
)


app.router.redirect_slashes = False
app.include_router(routers.router)


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


@app.exception_handler(RequestValidationError)
async def req_validation_error_handler(request: Request, exc: RequestValidationError):
    """为了统一错误信息格式, 自定义 RequestValidationError 异常处理。"""
    errors = exc.errors()
    msg = '\n'.join([err['loc'][-1] + ': ' + err['msg'] for err in errors])

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': ErrorCode.request_validation_error,
            'message': msg,
            'detail': jsonable_encoder(errors),
        },
    )


@app.exception_handler(BaseCustomError)
async def custom_error_handler(request: Request, exc: BaseCustomError):
    if not (error := custom_errors.get(exc.__class__)):
        raise exc

    return JSONResponse(
        status_code=error.status_code,
        content={'code': error.code, 'message': exc.message or error.message},
    )


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


def open_browser(url):
    import sys
    import time
    import webbrowser
    from threading import Thread

    if sys.platform.lower() == 'linux':
        return

    LOGGER.info('auto open browser')

    def f():
        time.sleep(1)
        webbrowser.open(url)

    t = Thread(target=f)
    t.start()


if __name__ == '__main__':
    bootstrap()
    open_browser(f'http://{settings.HOST}:{settings.PORT}')
    uvicorn.run(
        'comment.main:app',
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG_MODE,
        reload=settings.DEBUG_MODE,
        access_log=True,
    )
