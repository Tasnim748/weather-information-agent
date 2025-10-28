# prompts/tool_prompts.py
"""
System prompts for different tool contexts.
These guide the LLM on how to interpret and use tool outputs.
"""

TOOL_SYSTEM_PROMPTS = {
    "city_to_coords": """You have received geographic coordinates for a location.
Use these coordinates to fetch weather data if needed.
If the location was not found (error field present), politely ask the user to provide a more specific city name or verify the spelling.""",

    "get_current_weather": """You have received current weather data for a location.
Present this information in a clear, conversational way:
- Lead with the current temperature and condition
- Mention feels-like temperature if significantly different
- Include wind speed and humidity when relevant
- Use appropriate units based on the data provided
- Keep the response concise but informative

If there's an error field, inform the user that weather data is temporarily unavailable and suggest trying again.""",
}


def get_tool_prompt(tool_name: str) -> str:
    """
    Get the system prompt for a specific tool.
    Returns a generic prompt if tool-specific prompt not found.
    """
    return TOOL_SYSTEM_PROMPTS.get(
        tool_name,
        "Process the tool result and provide a helpful response to the user."
    )
