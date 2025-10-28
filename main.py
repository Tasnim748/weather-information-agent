# main.py
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Request

from agents.weather_agent import WeatherAgent
from models.chat import ChatRequest, ChatResponse
from settings import Settings
from clients.openWeatherAPI import OpenWeatherClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = Settings()
    app.state.agent = WeatherAgent()
    # Try to create and reuse a single client (connection pooling)
    try:
        app.state.ow = OpenWeatherClient()
    except ValueError:
        # API key not set yet; endpoints will surface a clear 500
        app.state.ow = None
    yield
    if app.state.ow:
        await app.state.ow.aclose()


app = FastAPI(
    title="Weather Info Agent API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/geocode")
async def geocode(request: Request, q: str, limit: int = 1, lang: Optional[str] = None):
    """Proxy to OpenWeather Direct Geocoding; returns raw JSON list."""
    ow: Optional[OpenWeatherClient] = request.app.state.ow
    if not ow:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured.")
    try:
        return await ow.geocode_direct(q=q, limit=limit, lang=lang)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")


@app.get("/api/weather/current")
async def current_weather(
    request: Request,
    lat: float,
    lon: float,
    units: str = "metric",
    lang: Optional[str] = None,
):
    """Proxy to OpenWeather Current Weather; returns raw JSON object."""
    ow: Optional[OpenWeatherClient] = request.app.state.ow
    if not ow:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured.")
    try:
        return await ow.current_weather(lat=lat, lon=lon, units=units, lang=lang)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """
    Chat endpoint that processes user queries about weather.
    The agent will automatically call tools when needed.
    """
    agent: WeatherAgent = req.app.state.agent
    
    # Invoke the agent with the user's message
    print("message from route:", request.message)
    response = await agent.invoke(request.message)

    print("response from route:", response)
    
    return ChatResponse(
        response=str(response.content),
        conversation_id=request.conversation_id
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
