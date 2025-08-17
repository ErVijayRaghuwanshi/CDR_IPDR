# main.py
from fastapi import FastAPI
import models
from database import engine
from routers import targets, rules, target_groups

# This command creates all the tables in the database based on the models
# In a production environment, you would use a migration tool like Alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Surveillance System API",
    description="API for managing targets, rules, and groups.",
    version="1.0.0"
)

# Include the routers
app.include_router(targets.router)
app.include_router(rules.router)
app.include_router(target_groups.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Surveillance System API"}