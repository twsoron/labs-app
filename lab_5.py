import requests
from openai import OpenAI
import streamlit as st 
import json
def get_current_weather(location, api_key, units="imperial"):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={location}&appid={api_key}&units={units}"
    )
    response = requests.get(url)

    if response.status_code == 401:
        raise Exception("Authentication failed: Invalid API key (401 Unauthorized)")
    if response.status_code == 404:
        error_message = response.json().get("message")
        raise Exception(f"404 error: {error_message}")

    data = response.json()

    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    temp_min = data["main"]["temp_min"]
    temp_max = data["main"]["temp_max"]
    humidity = data["main"]["humidity"]

    return {
        "location": location,
        "temperature": round(temp, 2),
        "feels_like": round(feels_like, 2),
        "temp_min": round(temp_min, 2),
        "temp_max": round(temp_max, 2),
        "humidity": round(humidity, 2)
    }

st.title('What to Wear Bot')
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given location (City, State, Country).",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City, State, Country (e.g., 'Syracuse, NY, US')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["imperial", "metric"],
                        "description": "imperial = Fahrenheit, metric = Celsius"
                    }
                },
                "required": []
            }
        }
    }
]

WEATHER_API_KEY = st.secrets.WEATHER_API_KEY
OPEN_API_KEY = st.secrets.OPEN_API_KEY
default_location = "Syracuse, NY, US"
client = OpenAI(api_key=st.secrets.OPEN_API_KEY)
location = ""
location = st.text_input("Enter a city: (City, State, Country)")
if st.button('Get Outfit and Activity Ideas'):
    if not location:
        location = default_location
        
    messages = [{
        "role": "user",
        "content": (
            "I want outfit + outdoor activity suggestions for today. "
            f"My city is: {location}"
        )
    }]

    response = client.chat.completions.create(
        model='gpt-4.1',
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message.to_dict())
    tool_calls = response_message.tool_calls

    if tool_calls:
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        tool_args = json.loads(tool_calls[0].function.arguments)
        tool_location = tool_args.get("location") or default_location
        tool_units = tool_args.get("units") or "imperial"

        if not tool_location.strip():
            tool_location = default_location

        if tool_function_name == "get_current_weather":
            results = get_current_weather(tool_location, WEATHER_API_KEY, tool_units)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_function_name,
                "content": json.dumps(results)
            })

            model_response_with_function_call = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages
            )

            st.write(model_response_with_function_call.choices[0].message.content)

        else:
            st.write("Error with tool")

    else:
        st.write(response_message.content)