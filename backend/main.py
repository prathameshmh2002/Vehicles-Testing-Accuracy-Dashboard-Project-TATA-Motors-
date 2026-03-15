from fastapi import FastAPI
from api import routes, db, models

models.Base.metadata.create_all(bind=db.engine)

app = FastAPI(title="ECU Dashboard API")

app.include_router(routes.router)
