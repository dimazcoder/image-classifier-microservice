from fastapi import APIRouter, Depends, BackgroundTasks

from app.controllers.realpage_controller import RealpageController
from app.schemas.realpage_schema import TestQuery

router = APIRouter()

@router.post("/realpage/test", status_code=200)
async def realpage_test(
    request: TestQuery,
    controller: RealpageController = Depends(RealpageController),
):
    result = controller.test(
        query=request.query
    )

    return result

@router.post("/realpage/process/local", status_code=200)
async def realpage_process_local(
    background_task: BackgroundTasks,
    task_controller: RealpageController = Depends(RealpageController),
):
    background_task.add_task(
        task_controller.process_local_files
    )
    return {'response': 'okay'}
