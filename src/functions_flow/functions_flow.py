import json
import os
import inspect
import requests
from openai import AsyncAzureOpenAI
from urllib.parse import quote
from promptflow import tool
import asyncio
import base64

MAX_ITER = 5
global client

import json
import base64

def get_current_weather(location):
    """Get the current weather in a given location"""
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = os.getenv("WEATHER_API_BASE")

    location = quote(location)    
    final_url = base_url + "key=" + api_key + "&q=" + location
    # Send a get request to the URL
    response = requests.get(final_url)
    weather_data = response.json()

    # Check if the request was successful
    if response.status_code == 200:
        # Extract data
        return json.dumps(weather_data['current'])

    else:
        raise Exception("An error occurred while fetching data: " + weather_data)


async def create_a_picture(prompt):
    """
    Creates a picture based on a description given by the user and returns the picture data as base64 encoded string. 
    """
    print("creating a picture using DALL-E")
    print("prompt", prompt)
    print("api_version", os.getenv("OPENAI_API_VERSION"))
    print("api_version from client", client._api_version)

    result = await client.images.generate(
        model=os.getenv("OPENAI_DALLE_MODEL"), # the name of your DALL-E 3 deployment
        prompt=prompt,
        style='natural',
        n=1
    )

    json_response = json.loads(result.model_dump_json())

    image_url = json_response["data"][0]["url"]  # extract image URL from response
    print(image_url)
    generated_image = requests.get(image_url).content  # download the image
    # base64 encode generated_image
    return base64.b64encode(generated_image).decode("utf-8")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state or city and country, e.g. San Francisco, CA or Tokyo, Japan",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_a_picture",
            "description": """
            Creates a picture based on a description given by the user. 
            The function will return the base64 encoded picture and that picture will be shown next to the response provided to the user.
            So, don't put a link to the picture in the response, as the picture will be shown automatically.
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The description of what the picture should be, for instance 'a drawing of a cat' or 'a phtograph of a room with a table and a chair' ",
                    }
                },
                "required": ["prompt"],
            },
        },
    }
]


async def call_tool(tool_call, message_history):
    available_functions = {
        "get_current_weather": get_current_weather,
        "create_a_picture": create_a_picture,
    }  # only one function in this example, but you can have multiple

    function_name = tool_call.function.name
    function_to_call = available_functions[function_name]
    function_args = json.loads(tool_call.function.arguments)
    function_response = function_to_call(**function_args)
    if inspect.iscoroutinefunction(function_to_call):
        function_response = await function_response

    message_history.append(
        {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": function_response,
        }
    )  # extend conversation with function response


async def call_llm(message_history):
    print("calling llm", message_history)
    settings = {
        "model": os.getenv("OPENAI_CHAT_MODEL_CHEAP"),
        "tools": tools,
        "tool_choice": "auto",
    }

    response = await client.chat.completions.create(
        messages=message_history, 
        **settings
    )

    message = response.choices[0].message
    message_history.append(message)

    for tool_call in message.tool_calls or []:
        if tool_call.type == "function":
            await call_tool(tool_call, message_history)

    return message_history

def get(object, field):
    if hasattr(object, field):
        return getattr(object, field)
    elif hasattr(object, 'get'):
        return object.get(field)
    else:
        raise Exception(f"Object {object} does not have field {field}")

@tool
async def run_conversation(chat_history, question):
    global client
    client  = AsyncAzureOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        azure_endpoint = os.getenv("OPENAI_API_BASE"),
        api_version = os.getenv("OPENAI_API_VERSION")
    )

    messages = [{"role": "system", 
                 "content": "You are a helpful assistant that help the user with the help of some functions."}]
    for turn in chat_history:
        messages.append({"role": "user", "content": turn["inputs"]["question"]})
        messages.append({"role": "assistant", "content": turn["outputs"]["answer"]})  
    
    messages.append({"role": "user", "content": question})
    image = None

    cur_iter = 0

    while cur_iter < MAX_ITER:
        messages = await call_llm(messages)
        message = messages[-1]
        if get(message,'role')=="tool":
            if get(message,'name')=="create_a_picture": 
                image = message['content']
                message['content'] = "Attached is the picture you asked for."
        else:
            return dict(
                answer=message.content,
                image=image
            )

        cur_iter += 1


if __name__ == "__main__":
    chat_history = [dict(inputs={"question": "What is the weather like in New York?"},
                         outputs={"answer": "It is sunny in New York today."})]

    result = asyncio.run(run_conversation(chat_history,
                                          "Draw me a picture of the current weather in NYC?"))
    print(result)