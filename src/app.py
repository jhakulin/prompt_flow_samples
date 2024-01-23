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
    # image_dir = os.path.join(os.curdir, 'images')
    # if not os.path.isdir(image_dir):
    #     os.mkdir(image_dir)

    cl.user_session.set(
        "chat_history",
        [],
    )


def show_images(base64_image):
    decoded_image = base64.b64decode(base64_image)
    elements = [
        cl.Image(
            content=decoded_image,
            name="generated image",
            display="inline",
        )
    ]
    return elements


@cl.on_message
async def run_conversation(message: cl.Message):
    print("running conversation")
    chat_history = cl.user_session.get("chat_history")

    prompt_flow = os.path.join(os.path.dirname(__file__), 'functions_flow')

    client = pf.PFClient()
    test_function = client.test
 
    response = await cl.make_async(test_function)(prompt_flow, 
                                                  inputs={"chat_history": chat_history,
                                                          "question": message.content})

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
    # import phoenix as px
    # session = px.launch_app(port=5000)

    # from phoenix.trace.exporter import HttpExporter
    # from phoenix.trace.openai.instrumentor import OpenAIInstrumentor
    # from phoenix.trace.tracer import Tracer

    # tracer = Tracer(exporter=HttpExporter())
    # OpenAIInstrumentor(tracer).instrument()

    from chainlit.cli import run_chainlit
    run_chainlit(__file__)