from fastapi import APIRouter, BackgroundTasks, Depends
from app.controllers.realpage_controller import RealpageController
from app.controllers.task_controller import TaskController
from app.schemas.property_schema import PropertySchema
from app.schemas.task_schema import TaskSchema

router = APIRouter()

@router.post("/tasks", status_code=200)
async def add_task(
    task_data: TaskSchema,
    background_task: BackgroundTasks,
    task_controller: TaskController = Depends(TaskController),
):
    task_id = task_controller.register_task(
        task_data
    )

    background_task.add_task(
        task_controller.handle_task,
        task_data
    )
    return {'task_id': task_id}

@router.get("/tasks/status/{task_id}", status_code=200)
async def task_status(
    task_id: str
):
    return {'status': 'done'}

@router.post("/tasks/local", status_code=200)
async def add_local_task(
    background_task: BackgroundTasks,
    task_controller: RealpageController = Depends(RealpageController),
):
    background_task.add_task(
        task_controller.process_local_files
    )
    return {'response': 'okay'}


@router.post("/tasks/sendtest", status_code=200)
async def add_test_task(
    property_data: PropertySchema,
    task_controller: TaskController = Depends(TaskController),
):
    await task_controller.send_test(property_data)
    return {'response': 'okay'}
