from fastapi import APIRouter
from app.api.v1.endpoints.main import router as main_router
from app.api.v1.endpoints.property import router as property_router
from app.api.v1.endpoints.task import router as task_router
from app.api.v1.endpoints.realpage import router as realpage_router

routers = APIRouter()
router_list = [main_router, property_router, task_router, realpage_router]

for router in router_list:
    router.tags = routers.tags.append("v1")
    routers.include_router(router)
