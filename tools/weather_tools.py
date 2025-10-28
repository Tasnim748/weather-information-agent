# tools/weather_tools.py
from typing import Dict, Any
from langchain_core.tools import tool
from clients.openWeatherAPI import OpenWeatherClient
from settings import Settings


@tool
async def city_to_coords(city: str) -> Dict[str, Any]:
    """
    Convert a city name to geographic coordinates.
    
    Args:
        city: The name of the city to geocode (e.g., "Paris", "New York, US", "Tokyo, Japan")
    
    Returns:
        A dictionary with lat, lon, and normalized_name
    """
    settings = Settings()

    print("city from tool:", city)
    
    async with OpenWeatherClient() as client:
        results = await client.geocode_direct(
            q=city,
            limit=1,
            lang=settings.default_lang
        )
        
        if not results:
            return {
                "error": f"Could not find coordinates for '{city}'",
                "lat": None,
                "lon": None,
                "normalized_name": None
            }
        
        place = results[0]
        normalized_name = place.get("name", "")
        if place.get("state"):
            normalized_name += f", {place['state']}"
        if place.get("country"):
            normalized_name += f", {place['country']}"
        
        return {
            "lat": place["lat"],
            "lon": place["lon"],
            "normalized_name": normalized_name
        }


@tool
async def get_current_weather(lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
    """
    Get current weather conditions for specific coordinates.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        units: Unit system - "metric" (Celsius), "imperial" (Fahrenheit), or "standard" (Kelvin)
    
    Returns:
        A dictionary with normalized weather data including temperature, feels_like, condition, wind, humidity, and clouds
    """
    print("lat from weather tool:", lat)
    try:
        async with OpenWeatherClient() as client:
            raw = await client.current_weather(
                lat=lat,
                lon=lon,
                units=units,
                lang=Settings().default_lang
            )
        
        # Normalize response
        main = raw.get("main", {})
        weather = raw.get("weather", [{}])[0]
        wind = raw.get("wind", {})
        clouds = raw.get("clouds", {})
        
        # Determine unit suffix
        temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        wind_unit = "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"
        
        return {
            "temp": main.get("temp"),
            "temp_unit": temp_unit,
            "feels_like": main.get("feels_like"),
            "condition": weather.get("main", "Unknown"),
            "description": weather.get("description", ""),
            "wind_speed": wind.get("speed"),
            "wind_unit": wind_unit,
            "wind_deg": wind.get("deg"),
            "humidity": main.get("humidity"),
            "clouds": clouds.get("all"),
            "pressure": main.get("pressure"),
            "visibility": raw.get("visibility"),
        }
        
    except Exception as e:
        return {
            "error": f"Failed to fetch weather data: {str(e)}",
            "temp": None,
            "feels_like": None,
            "condition": None,
            "description": None,
            "wind_speed": None,
            "humidity": None,
            "clouds": None
        }