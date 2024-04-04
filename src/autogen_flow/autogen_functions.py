import json
import os
import inspect
import requests
from openai import AsyncAzureOpenAI
from urllib.parse import quote
from promptflow.core import tool
from promptflow.contracts.multimedia import Image
import asyncio
import base64
from promptflow.tracing import trace
import json
import autogen
from openai import AzureOpenAI

from pydantic import BaseModel, Field
from typing_extensions import Annotated
from autogen.cache import Cache

@trace
def get_current_weather(location: str) -> str:
    """Get the current weather in a given location"""
    print(f"getting current weather in {location}")
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

@trace
def create_a_picture(prompt: str) -> bytes:
    """
    Creates a picture based on a description given by the user and returns the picture data as base64 encoded string. 
    """
    print("creating a picture using DALL-E")
    print("prompt", prompt)
    print("api_version", os.getenv("OPENAI_API_VERSION"))
    print("api_version from client", client._api_version)

    result = client.images.generate(
        model=os.getenv("OPENAI_DALLE_MODEL"), # the name of your DALL-E 3 deployment
        prompt=prompt,
        style='natural',
        n=1
    )

    json_response = json.loads(result.model_dump_json())

    image_url = json_response["data"][0]["url"]  # extract image URL from response
    print(image_url)
    # generated_image = requests.get(image_url).content  # download the image
    # base64 encode generated_image
    # return base64.b64encode(generated_image).decode("utf-8")
    # return generated_image
    return image_url



@trace
def function_caller(config_list: dict, message: str):
    llm_config = {
        "config_list": config_list,
        "timeout": 120,
    }
    weather_config = {
        "config_list": config_list,
        "timeout": 120,
    }
    image_config = {
        "config_list": config_list,
        "timeout": 120,
    }

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        system_message="In the end, provide a summary of the conversation and conclude the chat by saying TERMINATE.",
    )

    weather_agent = autogen.AssistantAgent(
        name="Weather_Agent",
        system_message="For weather information tasks " 
            "only use the functions you have been provided with. "
            "Reply TERMINATE when the task is done.",
        llm_config=weather_config,
    )

    autogen.agentchat.register_function(
        get_current_weather,
        caller=weather_agent,
        executor=user_proxy,
        description="Weather information provider for the current weather anywhere in the world.",
    )

    image_creation_agent = autogen.AssistantAgent(
        name="Image_Creation_Agent",
        system_message="For image creation tasks, " 
            "only use the functions you have been provided with. "
            "Reply TERMINATE when the task is done.",
        llm_config=image_config,
    )

    autogen.agentchat.register_function(
        create_a_picture,
        caller=image_creation_agent,
        executor=user_proxy,
        description="A service that can create a picture based on a description given by the user. "
            "You need to be extremely detailed in your description -- this service can only draw what you " 
            "tell it and will not be able to assume anything. " 
            "As a result, the service will return a URL that you can use to view the image.",
    )

    print("Weather:", weather_agent.llm_config["tools"])
    print("Image:  ", image_creation_agent.llm_config["tools"])

    groupchat = autogen.GroupChat(
        agents=[user_proxy, weather_agent, image_creation_agent],
        messages=[]
    )

    manager = autogen.GroupChatManager(
        name="Manager",
        groupchat=groupchat,
        llm_config=llm_config,
    )

    res = user_proxy.initiate_chat(
        manager, 
        message=message, 
        summary_method="reflection_with_llm"
    )

    # print("Messages:", groupchat.messages)
    messages = groupchat.messages.copy()
    messages.reverse()
    for message in messages:
        print("-" * 80)
        print(message)
        if message["content"] and not message["content"].upper() == "TERMINATE":
            return dict(messages=groupchat.messages, answer=message["content"])
    return None

@tool
def function_agent_conversation(chat_history: list, question: str):
    global client
    client  = AzureOpenAI(
        api_key = os.getenv("OPENAI_API_KEY"),
        azure_endpoint = os.getenv("OPENAI_API_BASE"),
        api_version = os.getenv("OPENAI_API_VERSION")
    )
    config_list = [
                   {
                        "model": os.environ.get("OPENAI_CHAT_MODEL"),
                        "api_key": os.environ.get("OPENAI_API_KEY"),
                        "api_type": "azure",
                        "base_url": os.environ.get("OPENAI_API_BASE"),
                        "api_version": "2023-03-15-preview",
                    }
                   ]
    
    
    result = function_caller(config_list, question)
    return dict(answer=result["answer"],
                image=None,
                messages=result["messages"])

if __name__ == "__main__":
    reply = function_agent_conversation("paint me a picture of the current weather conditions in San Diego?")
    print(reply)

