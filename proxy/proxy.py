import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
from loguru import logger

app = FastAPI()

# OPENAI_BASE_URL = "https://api.openai.com"
# OPENAI_BASE_URL = "http://host.docker.internal:8000"
OPENAI_BASE_URL = "https://api.vsegpt.ru/v1"


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return Response(status_code=401, content="Missing Authorization header")

    headers = {key: value for key, value in request.headers.items() if key.lower() != "host"}

    url = f"{OPENAI_BASE_URL}/{full_path}"
    body = await request.body()

    logger.info(f"PROXY\n\turl: {url},\n\tbody: {body.decode('utf-8')}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                # stream=True
            )

            data = await resp.aread()

            logger.info(f"PROXIED\n\turl: {url},\n\tdata: {data.decode('utf-8')}")


            return Response(content=data, status_code=resp.status_code, headers=resp.headers)

            # content_type = resp.headers.get("content-type", "")
            # if "text/event-stream" in content_type:
            #     return StreamingResponse(resp.aiter_raw(), status_code=resp.status_code, headers=resp.headers)
            # else:
            #     data = await resp.aread()
            #     return Response(content=data, status_code=resp.status_code, headers=resp.headers)
        except httpx.HTTPError as e:
            return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
