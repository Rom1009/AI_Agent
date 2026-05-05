from fastapi import FastAPI
import uvicorn
from src.app.api import register_modules
from src.db.db import init_db



def create_app():
    app = FastAPI(title = "AI Agent")
    register_modules(app)
    return app

app = create_app()

if __name__ == "__main__":
    init_db()

    uvicorn.run("src.main:app", host="localhost", port=8000, reload = True)