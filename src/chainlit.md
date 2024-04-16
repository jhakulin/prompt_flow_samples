# Multi-Agent Code Task Orchestration Sample

This sample demonstrates how to orchestrate multi-agent task execution using a conversation thread-based communication
between 2 agents for code programming and inspection and task planner agent working with user to create a plan
for the required SW coding tasks.

## Prerequisites

Install `azure_ai_assistant-0.2.12a1-py3-none-any.whl` library from https://github.com/Azure-Samples/azureai-assistant-tool/releases/tag/v0.2.12-alpha.

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

