import time
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from starlette.staticfiles import StaticFiles

from src.tap_bank.router import tap_bank_route
from src.users.router import users_router
from src.config import get_config
from src.utils.logger import get_logger


config = get_config()
logger = get_logger(config.LOG_LVL, config.LOG_NAME, config.LOGS_PATH)


app = FastAPI(docs_url=None, redoc_url=None, title='Salt API')


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(
        f'Unhandled exception. Request endpoint: {request.url.path}. Request method: {request.method}.\n'
        f'Exception: {exc}\nTraceback: {traceback.format_exc()}\n'
    )
    return JSONResponse(
        status_code=500,
        content={'detail': 'Internal Server Error'}
    )


# TODO перенести?
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/js/swagger-ui-bundle.js",
        swagger_css_url="/static/css/swagger-ui.css",
        swagger_favicon_url="/static/img/favicon.png"
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response


origins = ['http://localhost:8000']


static_dir = Path(__file__).parent.parent / 'static'
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(users_router)
app.include_router(tap_bank_route)
