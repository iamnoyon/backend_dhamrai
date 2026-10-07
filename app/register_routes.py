from fastapi import APIRouter

# import routers from modules
from app.modules.auth.route import router as auth_router
from app.modules.upazila.route import router as upazila_router
from app.modules.union.route import router as union_router
from app.modules.ward.route import router as ward_router
from app.modules.features.route import router as feature_router

# create a router instance
combine_router = APIRouter()


# register all routes
combine_router.include_router(auth_router)
combine_router.include_router(upazila_router)
combine_router.include_router(union_router)
combine_router.include_router(ward_router)
combine_router.include_router(feature_router)