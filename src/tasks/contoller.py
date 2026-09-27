from  src.tasks.dtos import TaskSchema
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.tasks.models import TaskModel
from src.user.models import UserModel




def create_task(body:TaskSchema,db:Session, user:UserModel):
    data=body.model_dump()
    new_task=TaskModel(title=data["title"],
                       description=data["description"],
                       is_completed=data["is_completed"],
                       user_id=user.id)
                    
                    

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_task(db:Session, user:UserModel):
    tasks=db.query(TaskModel).filter(TaskModel.user_id==user.id).all()
    return tasks

def get_task_byid(task_id:int,db:Session):
    one_task=db.query(TaskModel).get(task_id)
    if not one_task:
        raise HTTPException(404,details="Task id is incorrect")
    

    return one_task

def update_task(task_id:int, body:TaskSchema, db:Session, user:UserModel):
    one_task = db.query(TaskModel).filter_by(id=task_id).first()
    if not one_task:
        raise HTTPException(404, detail="Task with this id is not found")

    if one_task.user_id!=user.id:
        raise HTTPException(404, detail="You are not allowwed to update this task")
    update_data = body.model_dump()
    for field, value in update_data.items():
        setattr(one_task, field, value)

    db.commit()
    db.refresh(one_task)

    return one_task


def delete_task(task_id:int, db:Session, user:UserModel):
    one_task = db.query(TaskModel).filter_by(id=task_id).first()
    if not one_task:
        raise HTTPException(404, detail="The task want to delete is not found for the given id")

    if one_task.user_id!=user.id:
        raise HTTPException(404, detail="you are not authorized to delete this task")

    db.delete(one_task)
    db.commit()

    return None
