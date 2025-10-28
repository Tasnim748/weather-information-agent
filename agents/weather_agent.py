# agents/weather_agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from typing import List
from langchain_core.tools import BaseTool

from prompts.system_prompts import get_tool_prompt
from tools.weather_tools import city_to_coords, get_current_weather
from settings import Settings


class WeatherAgent:
    """
    LangChain agent with Gemini LLM and weather tools.
    """
    
    def __init__(self):
        settings = Settings()
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )
        
        # Available tools
        self.tools: List[BaseTool] = [city_to_coords, get_current_weather]
        
        # Create tool map for execution
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Concise system prompt (minimal tokens)
        self.system_prompt = "You are a helpful weather assistant. Provide clear, concise weather information. Ask for clarification if location is unclear."
    
    async def invoke(self, message: str) -> str:
        """
        Send a message to the agent and get a response.
        Handles tool execution loop.
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=message)
        ]
        
        # Loop to handle tool calls
        input_Tokens = 0
        output_Tokens = 0
        total_Tokens = 0
        
        while True:
            response = await self.llm_with_tools.ainvoke(messages)

            # token accumulation
            input_Tokens += response.usage_metadata['input_tokens']
            output_Tokens += response.usage_metadata['output_tokens']
            total_Tokens += response.usage_metadata['total_tokens']
            
            print("Tool", response.tool_calls)
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message),
                response
            ]
            
            # Check if LLM wants to call tools
            if not response.tool_calls:
                # No more tool calls, return final answer
                print(input_Tokens, output_Tokens, total_Tokens)
                return response
            
            # Execute each tool call
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Get and execute the tool
                tool = self.tool_map.get(tool_name)
                if tool:
                    result = await tool.ainvoke(tool_args)
                    print("result:", result)

                    # Get tool-specific system prompt
                    tool_context = get_tool_prompt(tool_name)

                    # Inject system prompt for next LLM call
                    messages.append(
                        SystemMessage(content=tool_context)
                    )
                    # Add tool result to messages
                    messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id
                        )
                    )

        
        # If we hit max iterations, return last response
        return "I encountered an issue processing your request. Please try again."
