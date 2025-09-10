from fastapi import FastAPI
from api.routes import router
import uvicorn


app = FastAPI(title="Finance Research MVP")
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)