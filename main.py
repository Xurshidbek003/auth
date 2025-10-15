from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.users import user_router


app = FastAPI(docs_url='/')


app.include_router(user_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)