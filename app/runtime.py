from fastapi import FastAPI

def build_runtime_app(config: dict) -> FastAPI:
    app = FastAPI(title=config.get("app_name", "Generated App"))

    endpoints = config.get("api_schema", {}).get("endpoints", [])

    for ep in endpoints:
        path = ep.get("path", "/")
        method = ep.get("method", "GET").lower()
        name = ep.get("name", "endpoint")

        async def handler(name=name):
            return {"message": f"{name} endpoint works"}

        if method == "get":
            app.get(path)(handler)
        elif method == "post":
            app.post(path)(handler)
        elif method == "put":
            app.put(path)(handler)
        elif method == "delete":
            app.delete(path)(handler)

    return app