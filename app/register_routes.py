from fastapi import APIRouter

# import routers from modules
from app.modules.auth.route import router as auth_router
from app.modules.upazila.route import router as upazila_router

# create a router instance
combine_router = APIRouter()


# register all routes
combine_router.include_router(auth_router)
combine_router.include_router(upazila_router)
