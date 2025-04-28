import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends
from app.controllers.property_controller import PropertyController
from app.controllers.task_controller import TaskController
from app.core.dependency import get_property_controller, get_current_active_user
from app.schemas.property_schema import PropertySchema
from app.schemas.user_schema import UserSchema

router = APIRouter()


@router.post("/property/extract_images")
async def extract_images_from_property_pdf(
        property_data: PropertySchema,
        property_controller: PropertyController = Depends(get_property_controller),
):
    task = asyncio.create_task(
        property_controller.extract_images_from_property_om(property_data)
    )
    # await property_controller.extract_images_from_property_om(
    #     property_data
    # )

    return {'response': 'okay'}

@router.get("/properties/{property_id}/images")
async def get_property_images(
        property_id: str,
        property_controller: PropertyController = Depends(get_property_controller),
        user: UserSchema = Depends(get_current_active_user)
):
    images = await property_controller.get_property_om_images(
        property_id=property_id
    )

    return images
