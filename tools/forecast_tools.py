from typing import Dict, Any
from datetime import datetime, timedelta
from langchain_core.tools import tool
from clients.openWeatherAPI import OpenWeatherClient
from settings import Settings
import pytz


@tool
async def get_forecast(lat: float, lon: float, timeframe: str = "tomorrow", units: str = "metric") -> Dict[str, Any]:
    """
    Get weather forecast for a specific timeframe.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        timeframe: Time period - "tonight", "tomorrow", "weekend", or "next_3_days"
        units: Unit system - "metric" (Celsius), "imperial" (Fahrenheit), or "standard" (Kelvin)
    
    Returns:
        A dictionary with filtered forecast data for the requested timeframe
    
    Assumptions:
    - "tonight": 6 PM today to 6 AM tomorrow (local time approximation using UTC)
    - "tomorrow": Next calendar day (midnight to midnight)
    - "weekend": Next Saturday and Sunday
    - "next_3_days": Next 72 hours from now
    - Forecast data is in 3-hour intervals
    
    Edge cases:
    - If it's already past midnight, "tonight" may return empty results
    - Weekend calculation assumes Saturday-Sunday; may vary by culture
    - API provides max 5 days; requests beyond that return all available data
    - Timezone is approximated; actual local time may differ
    """
    try:
        async with OpenWeatherClient() as client:
            raw = await client.forecast_5day(
                lat=lat,
                lon=lon,
                units=units,
                lang=Settings().default_lang
            )
        
        forecast_list = raw.get("list", [])
        if not forecast_list:
            return {"error": "No forecast data available", "entries": []}
        
        # Determine unit suffix
        temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        
        # Filter based on timeframe
        now = datetime.utcnow()
        filtered_entries = []
        
        if timeframe == "tonight":
            # Tonight: 6 PM today to 6 AM tomorrow (UTC approximation)
            tonight_start = now.replace(hour=18, minute=0, second=0, microsecond=0)
            if now.hour >= 18:
                # Already evening, start from now
                tonight_start = now
            tonight_end = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
            
            filtered_entries = [
                entry for entry in forecast_list
                if tonight_start <= datetime.fromtimestamp(entry["dt"]) <= tonight_end
            ]
        
        elif timeframe == "tomorrow":
            # Tomorrow: next calendar day
            tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow_end = tomorrow_start + timedelta(days=1)
            
            filtered_entries = [
                entry for entry in forecast_list
                if tomorrow_start <= datetime.fromtimestamp(entry["dt"]) < tomorrow_end
            ]
        
        elif timeframe == "weekend":
            # Next Saturday and Sunday
            days_until_saturday = (5 - now.weekday()) % 7
            if days_until_saturday == 0 and now.hour >= 12:
                # If it's Saturday afternoon, get next weekend
                days_until_saturday = 7
            
            weekend_start = (now + timedelta(days=days_until_saturday)).replace(hour=0, minute=0, second=0, microsecond=0)
            weekend_end = weekend_start + timedelta(days=2)
            
            filtered_entries = [
                entry for entry in forecast_list
                if weekend_start <= datetime.fromtimestamp(entry["dt"]) < weekend_end
            ]
        
        else:  # "next_3_days" or default
            # Next 72 hours
            end_time = now + timedelta(hours=72)
            filtered_entries = [
                entry for entry in forecast_list
                if datetime.fromtimestamp(entry["dt"]) <= end_time
            ]
        
        # Normalize entries
        normalized = []
        for entry in filtered_entries:
            main = entry.get("main", {})
            weather = entry.get("weather", [{}])[0]
            wind = entry.get("wind", {})
            
            normalized.append({
                "datetime": datetime.fromtimestamp(entry["dt"]).isoformat(),
                "timestamp": entry["dt"],
                "temp": main.get("temp"),
                "temp_unit": temp_unit,
                "feels_like": main.get("feels_like"),
                "temp_min": main.get("temp_min"),
                "temp_max": main.get("temp_max"),
                "condition": weather.get("main", "Unknown"),
                "description": weather.get("description", ""),
                "precipitation_prob": entry.get("pop", 0) * 100,  # Convert to percentage
                "wind_speed": wind.get("speed"),
                "humidity": main.get("humidity"),
                "clouds": entry.get("clouds", {}).get("all"),
            })
        
        return {
            "timeframe": timeframe,
            "entries": normalized,
            "count": len(normalized),
        }
        
    except Exception as e:
        return {
            "error": f"Failed to fetch forecast data: {str(e)}",
            "timeframe": timeframe,
            "entries": [],
            "count": 0,
        }
