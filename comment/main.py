from fastapi import FastAPI
from starlette.responses import HTMLResponse

from comment import __version__

app = FastAPI(
    title='Comment System',
    version=__version__,
)


@app.get('/healthz', response_class=HTMLResponse)
async def health():
    """Health Check"""
    return ''
