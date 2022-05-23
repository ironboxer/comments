import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.staticfiles import StaticFiles

from comment import routers
from comment.__version__ import __version__
from comment.bootstrap import bootstrap
from comment.config import settings
from comment.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from comment.exceptions import BaseCustomError, ErrorCode, custom_errors

logging.config.dictConfig(settings.LOGGING)

LOGGER = logging.getLogger(__file__)

app = FastAPI(
    title='Comment System',
    version=__version__,
    debug=True,
)

app.router.redirect_slashes = False
app.include_router(routers.router)
app.mount('/', StaticFiles(directory='static', html=True), name='static')


# @app.on_event('startup')
# def startup_event():
#    LOGGER.info('on startup_event')
#    bootstrap()


# @app.on_event("shutdown")
# def shutdown_event():
#    teardown()


@app.get('/', response_class=RedirectResponse)
async def index(request: Request):
    return request.url + '/index.html'


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
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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


if __name__ == '__main__':
    bootstrap()
    uvicorn.run('comment.main:app', port=8000, reload=True, access_log=True)
