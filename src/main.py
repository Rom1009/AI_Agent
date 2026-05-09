from fastapi import FastAPI
import uvicorn
from src.app.api import register_modules
from src.db.db import init_db
from src.app.core.exception_handler import app_exception_handler, app_unexception_handler
from src.app.core.middleware import log_request
from src.app.exceptions.exceptions import AppError


def create_app():
    app = FastAPI(title = "AI Agent")

    app.add_exception_handler(AppError, app_exception_handler)
    app.add_exception_handler(Exception, app_unexception_handler)

    app.middleware("http")(log_request)

    register_modules(app)
    return app

app = create_app()

if __name__ == "__main__":
    init_db()

    uvicorn.run("src.main:app", host="localhost", port=8000, reload = True)