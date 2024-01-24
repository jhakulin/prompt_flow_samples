import json
import ast
import os
import inspect
import requests
from openai import AsyncAzureOpenAI
from urllib.parse import quote
from chainlit.playground.providers.openai import stringify_function_call
import chainlit as cl
import base64
import promptflow as pf

@cl.on_chat_start
def start_chat():
    print("starting chat")

    cl.user_session.set(
        "chat_history",
        [],
    )

    cl.user_session.set(
        "prompt_flow",
        os.path.join(os.path.dirname(__file__), 'functions_flow'),
    )

def show_images(image):
    # image is a dict of length 1
    # key is the type of image, value is the base64 encoded image or file path, depending on the type

    image_type = list(image.keys())[0]
    image_content = list(image.values())[0]
    if image_type.endswith(";base64"):
        decoded_image = base64.b64decode(image_content)
    elif image_type.endswith(";path"):
        prompt_flow = cl.user_session.get("prompt_flow")
        decoded_image = open(os.path.join(prompt_flow, image_content), "rb").read()
    else:
        raise Exception("Unknown image type: " + image_type)

    elements = [
        cl.Image(
            content=decoded_image,
            name="generated image",
            display="inline",
        )
    ]
    return elements

@cl.step(type="llm")
async def call_promptflow(chat_history, message):
    prompt_flow = cl.user_session.get("prompt_flow")
    client = pf.PFClient()
 
    response = await cl.make_async(client.test)(prompt_flow, 
                                                  inputs={"chat_history": chat_history,
                                                          "question": message.content})
    return response


@cl.on_message
async def run_conversation(message: cl.Message):
    print("running conversation")
    chat_history = cl.user_session.get("chat_history")
 
    response = await call_promptflow(chat_history, message)

    if response["image"]:
        elements = show_images(response["image"])
    else:
        elements = []  

    await cl.Message(content=response["answer"], 
                        author="Answer",
                        elements=elements).send()
    
    chat_history.append({"inputs": {"question": message.content}, 
                         "outputs": {"answer": response["answer"]}})

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)