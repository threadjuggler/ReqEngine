from fastapi import FastAPI
from routers import auth, startx

app = FastAPI()


app.include_router(auth.router)
app.include_router(startx.router)