from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get('/')
def root():
    return PlainTextResponse(content="OK")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)