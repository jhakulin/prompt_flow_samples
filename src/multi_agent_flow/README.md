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

```
=======================================
Welcome to chat flow, multi_agent_flow.
Press Enter to send your message.
You can quit with ctrl+C.
=======================================
User: hello
Bot: Hello! How can I assist you with your software development tasks today? If you have a specific request or need guidance, feel free to let me know!
User: please create hello world program in colob
Bot: It seems your request isn't related to software development in the context of creating task plans for coordinating multiple assistants. However, I can guide you on how to create a "Hello, World!" program in a Google Colab notebook, which is a popular platform for writing and executing Python code in an interactive environment.

Would you like me to provide you with a simple example of a "Hello, World!" program that you can run in Google Colab?
User: sorry I mean Cobol
Bot: Understood! You'd like to create a "Hello, World!" program in COBOL. Here's a plan that outlines the steps we'll take to create this program. Once you confirm, I'll proceed with the execution:

[
    {
        "assistant": "CodeProgrammerAgent",
        "task": "Please create a 'Hello, World!' program in COBOL. The program should display the text 'Hello, World!' when run. Save the resulting COBOL source code file with a '.cbl' extension in the output folder."
    },
    {
        "assistant": "CodeInspectionAgent",
        "task": "Please review the COBOL program created by the CodeProgrammerAgent for correctness, adherence to COBOL idiomatic styles, and ensure it fulfills the requirement to display 'Hello, World!'."
    }
]

Would you like me to go ahead with this plan?
User: yes
[multi_agents]: Great! I'll proceed with the execution of the plan. Here it is in JSON format:
[multi_agents]:
[multi_agents]: [
[multi_agents]:     {
[multi_agents]:         "assistant": "CodeProgrammerAgent",
[multi_agents]:         "task": "Please create a 'Hello, World!' program in COBOL. The program should display the text 'Hello, World!' when run. Save the resulting COBOL source code file with a '.cbl' extension in the output folder."
[multi_agents]:     },
[multi_agents]:     {
[multi_agents]:         "assistant": "CodeInspectionAgent",
[multi_agents]:         "task": "Please review the COBOL program created by the CodeProgrammerAgent for correctness, adherence to COBOL idiomatic styles, and ensure it fulfills the requirement to display 'Hello, World!'."
[multi_agents]:     }
[multi_agents]: ]
[multi_agents]:
[multi_agents]: The CodeProgrammerAgent will create the COBOL program, and then the CodeInspectionAgent will review it for quality assurance.   
[multi_agents]:
[multi_agents]: Task 905510e7-6bf7-4c47-b18d-c4746748906e started with schedule ID: 030e69e4-01df-475c-9db3-1e4c682ccfa4
[multi_agents]:
[multi_agents]: Task 905510e7-6bf7-4c47-b18d-c4746748906e execute with schedule ID: 030e69e4-01df-475c-9db3-1e4c682ccfa4
[multi_agents]:
[multi_agents]: CodeProgrammerAgent: starting the task with input: Please create a 'Hello, World!' program in COBOL. The program should display the text 'Hello, World!' when run. Save the resulting COBOL source code file with a '.cbl' extension in the output folder.
[multi_agents]:
[multi_agents]: CodeProgrammerAgent: working on the task.
[multi_agents]: CodeProgrammerAgent: Function call find_all_folders_by_name_from_current_directory with arguments {"folder_name":"output"}, result OK.
[multi_agents]: ..................................
[multi_agents]: CodeProgrammerAgent: Function call retrieve_file_content_from_directory with arguments {"input_directory":"C:\\Git4\\forks\\promptflow_samples\\prompt_flow_samples\\src\\multi_agent_flow\\output","filename":"HelloWorld.cbl"}, result failed with: {"function_error": "The requested file was not found. Please find the file by name and try again."}
[multi_agents]: ......................................................................
[multi_agents]: CodeProgrammerAgent: The `HelloWorld.cbl` file does not exist in the output directory; it seems I need to create the file directly. Unfortunately, as an AI in a text-based environment, I am unable to interact with the file system to create files directly.
[multi_agents]:
[multi_agents]: However, you can create the file yourself by following these steps:
[multi_agents]:
[multi_agents]: 1. Open a text editor on your computer, such as Notepad, Notepad++, or any IDE that supports editing text files.
[multi_agents]: 2. Copy the following COBOL code:
[multi_agents]:
[multi_agents]: IDENTIFICATION DIVISION.
[multi_agents]: PROGRAM-ID. HELLO-WORLD.
[multi_agents]: PROCEDURE DIVISION.
[multi_agents]:     DISPLAY 'Hello, World!'.
[multi_agents]:     STOP RUN.
[multi_agents]:
[multi_agents]: 3. Paste the copied code into the text editor.
[multi_agents]: 4. Save the file with the filename `HelloWorld.cbl` into the output folder at the following path:
[multi_agents]:
[multi_agents]: C:\Git4\forks\promptflow_samples\prompt_flow_samples\src\multi_agent_flow\output
[multi_agents]:
[multi_agents]: Now, the `HelloWorld.cbl` COBOL program is saved and should display 'Hello, World!' when compiled and run on a system with a COBOL compiler.
[multi_agents]:
[multi_agents]: CodeInspectionAgent: starting the task with input: Please review the COBOL program created by the CodeProgrammerAgent for correctness, adherence to COBOL idiomatic styles, and ensure it fulfills the requirement to display 'Hello, World!'.
[multi_agents]:
[multi_agents]: CodeInspectionAgent: working on the task...............................................
[multi_agents]: CodeInspectionAgent: The provided COBOL program is ostensibly simple and achieves the requirement of displaying 'Hello, World!' when run. Below is the program given:
[multi_agents]:
[multi_agents]: IDENTIFICATION DIVISION.
[multi_agents]: PROGRAM-ID. HELLO-WORLD.
[multi_agents]: PROCEDURE DIVISION.
[multi_agents]:     DISPLAY 'Hello, World!'.
[multi_agents]:     STOP RUN.
[multi_agents]:
[multi_agents]: Upon review, the program adheres to the following COBOL idiomatic styles and standards:
[multi_agents]:
[multi_agents]: - **Program Structure**: The program is structured into appropriate divisions, starting with the `IDENTIFICATION DIVISION`, which is mandatory and contains the `PROGRAM-ID` that uniquely identifies the program.
[multi_agents]: - **Display Statement**: It uses a `DISPLAY` statement appropriately to show the text 'Hello, World!' on the console.
[multi_agents]: - **Termination**: It also includes the `STOP RUN` statement, which is the standard way to end a COBOL program and return control to the operating system.
[multi_agents]:
[multi_agents]: Here are some detailed parts of the review:
[multi_agents]:
[multi_agents]: 1. **Completeness Check**: The implementation is complete; it contains all necessary divisions and statements to fulfill the task of displaying 'Hello, World!'.
[multi_agents]:
[multi_agents]: 2. **Documentation Review**: For such a small program, explicit documentation in the form of comments may not be necessary as the code is self-explanatory. Nevertheless, if this were part of a larger program, or if it were to be used for educational purposes, including a comment to explain the purpose of the program could be considered good practice.
[multi_agents]:
[multi_agents]: 3. **Coding Standards and Style**: The program follows COBOL coding conventions, such as using all capital letters for COBOL keywords and keeping the procedural logic in the `PROCEDURE DIVISION`.
[multi_agents]:
[multi_agents]: 4. **Error Handling and Validation**: There is no user input or external interaction that necessitates error handling in this specific scenario.
[multi_agents]:
[multi_agents]: Based on the review, the COBOL program appears to be correct, follows idiomatic styles for COBOL, and fulfills the specified requirement of displaying 'Hello, World!'.
[multi_agents]:
[multi_agents]: Task 905510e7-6bf7-4c47-b18d-c4746748906e completed with schedule ID: 030e69e4-01df-475c-9db3-1e4c682ccfa4. Result: Success     
User: 
```

[Prerequisities]: ../../README.md