from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api_router
from starlette.responses import RedirectResponse
from db_manager import Base, engine, db_notempty, fill_db

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(api_router.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)


@app.get("/")
async def main():
    return RedirectResponse(
        url = "/docs/")


@app.on_event("startup")
async def startup():
    if not db_notempty():
        fill_db()

