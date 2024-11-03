from fastapi import FastAPI
from .auth import models
from app.database import engine
from .auth.routes import router as auth_router
from .items.routes import router as items_router


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(items_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
