from fastapi import FastAPI, APIRouter
from src.app.module.user_module import UserModule
from src.app.module.ai_module import AIModule

def register_modules(app: FastAPI):
    
    api_router = APIRouter(prefix="/api")
    
    modules = [
        UserModule(),
        AIModule(),
    ]

    for module in modules:
        module.setup_router()
        api_router.include_router(module.router, prefix=module.prefix, tags=module.tags)
    
    app.include_router(api_router)