from fastapi import FastAPI

app = FastAPI()

api_root = "/api/v1/"

@app.get(f"{api_root}")
async def root():
    return {"message": "Hello World!!"}
