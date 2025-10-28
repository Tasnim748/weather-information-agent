# Weather Information Agent with LangChain, LangGraph & FastAPI

A modular AI agent for handling weather queries through tool-calling and orchestration, developed as a mid-level project to demonstrate practical skills in LangChain, tool integration, and API handling. This showcases my experience as a Python web developer with LangChain fundamentals, focusing on building resilient, intent-aware agents for real-world data retrieval.

## Project Description

This backend-focused implementation creates a weather agent that resolves user queries by intelligently selecting and chaining tools: geocoding locations, fetching current conditions or forecasts, assessing air quality, and applying utilities like unit conversion. Up to the model binding stage, it emphasizes clean tool schemas, error-resilient HTTP clients, and a system prompt for accurate intent detection (e.g., distinguishing "current" from "forecast" or prompting for missing locations).

Key skills demonstrated:
- Designing and binding LangChain tools with clear descriptions and Pydantic schemas for LLM decision-making.
- Integrating external APIs (OpenWeatherMap) with retries, timeouts, and normalized outputs.
- Model configuration and prompting to enable tool selection and graceful error handling.
- Modular testing with mocked responses to ensure reliability without live API calls.

This project builds toward a full agent loop with LangGraph, highlighting my ability to orchestrate AI workflows for production-like scenarios, such as data-driven decision routing and structured responses.

## Tech Stack

- **Backend**: Python 3.10+, LangChain (tools and model binding), OpenAI API (LLM), Requests (HTTP client), Pydantic (data models).
- **External Services**: OpenWeatherMap (Geocoding, Current Weather, Forecast, Air Pollution endpoints).
- **Dependencies**: Listed in `requirements.txt` for pip installation.

## Setup and Usage

### Prerequisites
- Python 3.10+.
- OpenAI API key (for model invocation).
- OpenWeatherMap API key (free tier works for development).

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/weather-agent.git
   cd weather-agent
   ```

2. Virtual environment setup:
   ```
   python -m venv venv  # Creates a 'venv' folder
   ```
   - Activate the venv (do this every time you work on the project):
        - On Windows (Command Prompt or PowerShell):
        ```
        venv\Scripts\activate
        ```
        - On macOS/Linux (Terminal):
        ```
        source venv/bin/activate
        ``` 

2. Set up environment:

   Create and edit your `.env` file with your keys:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   WEATHER_API_KEY=your_weather_key
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Project
Launch a development server:
```
fastapi dev main.py
```
Access at `http://localhost:8000/docs` (health check endpoint available).

### Example Usage
Head over to http://localhost:8000/docs to interact with the auto-generated API documentation. Use the `/chat` endpoint to send messages and test the agent's tool-calling capabilities.[1][15]

- **Method**: POST `/chat`
- **Request Body**: JSON with `{"message": "Your query here", "conversation_id": "your_conversation_id"}` (e.g., `{"message": "should I take an umbrella today in Dhaka city?", "conversation_id": "random_number_1234"}`).
- **Response**: Structured JSON with the agent's reasoned answer, including extracted weather data (e.g., temperature, conditions, AQI if relevant), units, and sources.[15]

Sample curl command:
```
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "should I take an umbrella today in Dhaka city?", "conversation_id": "random_number_1234"}'
```

Expected response:
```json
{
  "response": "The current temperature in Dhaka is 31.98°C, but it feels like 34.57°C. The condition is Haze with a description of haze. The wind is blowing from the east at 1.54 m/s and humidity is at 51%. Given the haze, an umbrella is probably not necessary.",
  "conversation_id": "3"
}
```
## Development Progress

Completed phases (aligned with iterative builds):
- Repository structure and environment management.
- Backend bootstrap with dependencies and settings.
- FastAPI endpoints with streaming for real-time responses.
- OpenWeatherMap client for API endpoints.
- Core tools: Geocoding, Current Weather, Forecast, Air Quality, and utilities (unit conversion, time formatting).
- LLM binding with tools and a system prompt for query analysis and tool routing.

Next phases (personal roadmap):
- LangGraph implementation for conditional agent loops (e.g., geocode → weather chaining).
- Angular frontend for a chat interface to consume the agent.

This progression reflects my systematic approach to scaling from isolated components to orchestrated systems, a skill honed through Python web development and LangChain experimentation.

## Skills Showcased

This project illustrates mid-level proficiency in:
- **Agentic AI Design**: Creating tools that enable LLMs to make context-aware decisions, with schemas that guide tool selection.
- **API Integration & Resilience**: Handling external services with proper error shaping, rate limiting, and normalization (e.g., units, local time).
- **Testing & Modularity**: Ensuring components are independently verifiable, reducing integration risks.
- **Prompt Engineering**: Crafting system instructions for robust intent detection and user-friendly outputs.

Ideal for roles in AI engineering, backend development, or full-stack AI applications, where building extensible, data-informed agents is key.

## Notes

- API costs are minimal in development (OpenWeatherMap free tier: 1,000 calls/day; GeminiAPI: low-token queries at free of cost).
- No frontend yet—focus on backend logic for clear skill demonstration; UI integration planned.