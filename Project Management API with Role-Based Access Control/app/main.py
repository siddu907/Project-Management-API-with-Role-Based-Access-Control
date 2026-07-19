from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import auth, projects, tasks, members, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Project Management API with RBAC",description="""
## Task Manager API 

This API allows users to manage their daily tasks and projects based on the role based access control...

Thank you for using it and have a nice day from Stackly India

""")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(members.router, prefix="/projects", tags=["Project Members"])
app.include_router(users.router, prefix="/users", tags=["Users"])
