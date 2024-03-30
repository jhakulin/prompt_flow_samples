# Image and Weather chat

Hi, this is a chat client to play around with functions to understand how they work in OpenAI.

This chat has 2 functions configured:
1. A function to get the current weather in a given location
2. A function that creates a picture based on a description given by the user

Try simple queries like:
- what is the weather like in beijing?
- paint me a picture of a deer in a hoodie.

Then try more complex queries like:
- paint a picture of the current weather conditions as they present themselves at this time in Hamburg


And inspect the traces at `http://localhost:<your-port>/v1.0/ui/traces/#`


### Function details:
```json
[
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
```

