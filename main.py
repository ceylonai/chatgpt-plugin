import json
import uvicorn
from pprint import pprint

from fastapi import FastAPI, Request
from pydantic import BaseSettings
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, PlainTextResponse, StreamingResponse
from fastapi.openapi.utils import get_openapi


is_secure = False
app = FastAPI()
origins = [
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/myself/{name}")
async def get_today(name):
    return {
        "name": name,
        "display": f"![Profile Picture](https://dummyimage.com/600x400/000/fff)",
    }


@app.get("/image/{name}")
async def get_fig(name):
    return f"https://placehold.co/600x400?text={name}"


@app.get("/logo.png", include_in_schema=False)
async def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')


@app.get("/.well-known/ai-plugin.json", response_class=PlainTextResponse, include_in_schema=False)
async def plugin_manifest(request: Request):
    host = request.headers["host"]

    def iterfile():
        with open("ai-plugin.json") as f:
            text = f.read()
            text = text.replace("PLUGIN_HOSTNAME", f"http://{host}")
            yield from text

    return StreamingResponse(iterfile(), media_type="text/json")


def custom_openapi():
    openapi_schema = get_openapi(
        title="ChatGPT4 Plugin: About Myself",
        version="2.5.0",
        description="Try to chat with Me!",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app='main:app', reload=True, host="0.0.0.0")
