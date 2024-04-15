# Sample: Multi-Agent Code Task Orchestration

This sample demonstrates how to orchestrate multi-agent task execution using a conversation thread-based communication
between 2 agents for code programming and inspection and task planner agent working with user to create a plan
for the required SW coding tasks.

## Prerequisites

Install `azure_ai_assistant-0.2.12a1-py3-none-any.whl` library from https://github.com/Azure-Samples/azureai-assistant-tool/releases/tag/v0.2.12-alpha
This is required for multi_agent_flow.py

## Configure the sample

Sample consists of following agents and their roles:
- TaskPlannerAgent
  - Creates plan (tasks) using users input and knowledge about CodeProgrammerAgent and CodeInspectionAgent assistant instances to achieve the required SW engineering work.
  - Uses own conversation thread with user
- CodeProgrammerAgent
  - Configured to handle SW programming related tasks
  - Uses functions to access files for reading and writing
  - Uses shared conversation thread with CodeInspectionAgent
- CodeInspectionAgent
  - Configured to handle SW inspection related tasks
  - Uses functions to access files for reading
  - Uses shared conversation thread with CodeProgrammerAgent
- FileCreatorAgent
  - Configured to take CodeProgrammerAgent output as input and write code block contents to a file

### Configure the Agents

TaskPlannerAgent get the details about CodeProgrammerAgent and CodeInspectionAgent by file references in the yaml configuration.
NOTE: Check the file references paths are configured correctly for your environment, the file_references field in yaml config files 
require absolute path.
- IMPORTANT: If you are not seeing `CodeProgrammerAgent` or `CodeInspectionAgent` in the task list assistant provided, then it means your file
references are not correct in TaskPlannerAgent yaml configuration.

## Run the sample

### In PromptFlow VS Code Extension
1. Open flow.dag.yaml in Visual Editor
2. On top middle of the extension, see play button image, click it and select "Run with standard mode" or "Run with interactive mode"
3. Execution should look like in the example run below

## Example run

Currently there is challenge to get chat history shared between turns as seen below

```
=======================================
Welcome to chat flow, multi_agent_flow.
Press Enter to send your message.
You can quit with ctrl+C.
=======================================
User: hello
Bot: Hello! How can I assist you with your software development tasks today? If you have a specific request or need guidance, feel free to let me know!
User: create basic cli application for chat between user and assistant in C++
Bot: To create a basic CLI (Command Line Interface) application for chat between a user and an assistant in C++, we will need to perform the following tasks:

1. **Design the CLI Interface**: Define how the user will interact with the application, including input prompts and output messages.
2. **Implement Message Handling**: Create functions to handle sending and receiving messages.
3. **Implement the Chat Logic**: Develop the logic for the assistant's responses.
4. **Setup the Main Loop**: Create the main application loop that will handle user input and provide responses.
5. **Code Review and Inspection**: Ensure the code is idiomatic, follows best practices, and is well-documented.
6. **Compile and Test**: Compile the application and perform basic tests to ensure it works as expected.

Here's a plan to coordinate the assistants to complete this task:

[
    {
        "assistant": "CodeProgrammerAgent",
        "task": "Design and implement a basic CLI interface for a chat application in C++. The interface should prompt the user for input and display responses from the assistant. Include functions for sending and receiving messages, and a simple logic for the assistant's responses. Ensure the code is well-documented and follows C++ idiomatic practices."
    },
    {
        "assistant": "CodeInspectionAgent",
        "task": "Review the C++ code for the CLI chat application provided by the CodeProgrammerAgent. Verify that the code is complete, follows idiomatic C++ practices, has proper error handling, input validation, and is well-documented. Provide feedback for any necessary improvements."
    },
    {
        "assistant": "CodeProgrammerAgent",
        "task": "Implement the feedback provided by the CodeInspectionAgent to ensure the C++ CLI chat application is of high quality, adheres to best practices, and is well-documented. Compile and test the application to ensure it works as expected."
    }
]

Before proceeding with this plan, we need to confirm with the user:

"Here's the plan based on your request to create a basic CLI application for chat between a user and an assistant in C++. Would you like me to go ahead with this?"
User: please proceed
Bot: It appears that there is no specific software development task provided in your request. To assist you effectively, I need a clear task related to software development. Could you please provide me with the details of the software development task you need help with?
User: 
```

[Prerequisities]: ../../README.md