from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import instruments, market

app = FastAPI(title="QuantPulse Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instruments.router)
app.include_router(market.router)

@app.get("/")
def root():
    return {"message": "QuantPulse Engine Running"}
