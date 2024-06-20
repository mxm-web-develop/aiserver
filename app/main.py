from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langserve import add_routes
from fastapi.staticfiles import StaticFiles
from utils.routes import utils_router
import os

OpenAI_Key = os.getenv("OpenAI_Key")

app = FastAPI(
    title="Ai Server",
    version="1.0",
    description="我的AI服务集成",
)

app.include_router(utils_router, prefix="/utils", tags=["utils"])
add_routes(
    app,
    ChatOpenAI(model="gpt-3.5-turbo-0125", api_key=OpenAI_Key),
    path="/openai",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
