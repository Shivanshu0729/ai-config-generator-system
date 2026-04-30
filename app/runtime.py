from fastapi import FastAPI
from typing import Dict, Any


def create_handler(name: str):
    async def handler():
        return {"message": f"{name} endpoint works"}
    return handler


def build_runtime_app(config: Dict[str, Any]) -> FastAPI:
    app = FastAPI(title=config.get("app_name", "Generated App"))

    endpoints = config.get("api_schema", {}).get("endpoints", [])

    for ep in endpoints:
        path = ep.get("path", "/")
        method = ep.get("method", "GET").lower()
        name = ep.get("name", "endpoint")

        handler = create_handler(name)

        if method == "get":
            app.get(path)(handler)
        elif method == "post":
            app.post(path)(handler)
        elif method == "put":
            app.put(path)(handler)
        elif method == "delete":
            app.delete(path)(handler)
        else:
            app.get(path)(handler)

    return app