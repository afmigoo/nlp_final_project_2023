from fastapi import FastAPI
import api_router

app = FastAPI()
app.include_router(api_router.search)
app.include_router(api_router.data)