from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, controllers
from .database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Tasks Api",
    description="Tasks Api created for a Continuous Integration Project",
    summary="Deadpool's favorite app. Nuff said.",
    version="0.0.1",
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@app.get("/", response_model=dict, tags=["Health Check"])
def api_status():
    return {"status": "running"}


@app.post("/tasks/", response_model=schemas.Task, tags=["Tasks"])
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return controllers.create_task(db=db, task=task)


@app.get("/tasks/", response_model=List[schemas.Task], tags=["Tasks"])
def get_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return controllers.get_tasks(db=db, skip=skip, limit=limit)


@app.get("/tasks/{task_id}", response_model=schemas.Task, tags=["Tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    db_task = controllers.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.put("/tasks/{task_id}", response_model=schemas.Task, tags=["Tasks"])
def update_task(task_id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = controllers.update_task(db, task_id=task_id, updated_task=updated_task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@app.delete("/tasks/{task_id}", response_model=schemas.Task, tags=["Tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = controllers.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)