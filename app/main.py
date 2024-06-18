from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langserve import server

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)
