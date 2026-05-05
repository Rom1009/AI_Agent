from fastapi import FastAPI, APIRouter
from sqlmodel import Session
from src.app.module.user_module import UserModule

def register_modules(app: FastAPI):
    
    api_router = APIRouter()
    
    modules = [
        UserModule(session=Session()),
    ]

    for module in modules:
        module.setup_router()
        api_router.include_router(module.router, prefix=module.prefix, tags=module.tags)
    
    app.include_router(api_router)