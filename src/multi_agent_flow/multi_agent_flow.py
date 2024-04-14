from promptflow.core import tool
from promptflow.tracing import trace
from azure.ai.assistant.management.async_assistant_client import AsyncAssistantClient
from azure.ai.assistant.management.async_chat_assistant_client import AsyncChatAssistantClient
from azure.ai.assistant.management.async_assistant_client_callbacks import AsyncAssistantClientCallbacks
from azure.ai.assistant.management.ai_client_factory import AsyncAIClientType
from azure.ai.assistant.management.async_conversation_thread_client import AsyncConversationThreadClient
from azure.ai.assistant.management.async_task_manager import AsyncTaskManager, AsyncMultiTask
from azure.ai.assistant.management.async_task_manager_callbacks import AsyncTaskManagerCallbacks

from typing import Dict, List
import json, re
import asyncio


class MultiAgentOrchestrator(AsyncTaskManagerCallbacks, AsyncAssistantClientCallbacks):
    """
    Orchestrates the multi-agent task execution.
    """
    def __init__(self, messages: List[str] = []):
        self.task_completion_events = {}
        self._assistants: Dict[str, AsyncAssistantClient] = {}
        self.conversation_thread_client = AsyncConversationThreadClient.get_instance(AsyncAIClientType.AZURE_OPEN_AI)
        self.condition = asyncio.Condition()
        self.task_started = False
        self.messages = messages
        super().__init__()

    async def on_task_started(self, task: AsyncMultiTask, schedule_id):
        print(f"\nTask {task.id} started with schedule ID: {schedule_id}")
        async with self.condition:
            self.task_completion_events[schedule_id] = asyncio.Event()
            self.task_started = True
            self.condition.notify_all()
            self.thread_name = await self.conversation_thread_client.create_conversation_thread()

    async def on_task_execute(self, task: AsyncMultiTask, schedule_id):
        print(f"\nTask {task.id} execute with schedule ID: {schedule_id}")
        for request in task.requests:
            assistant_name = request["assistant"]
            assistant_client = self._assistants[assistant_name]
            await self.conversation_thread_client.create_conversation_thread_message(request["task"], thread_name=self.thread_name)
            await assistant_client.process_messages(thread_name=self.thread_name)

    async def on_task_completed(self, task: AsyncMultiTask, schedule_id, result):
        print(f"\nTask {task.id} completed with schedule ID: {schedule_id}. Result: {result}")
        event = self.task_completion_events.get(schedule_id)
        if event:
            event.set()
        self.task_started = False

    async def on_task_failed(self, task: AsyncMultiTask, schedule_id, error):
        print(f"\nTask {task.id} failed with schedule ID: {schedule_id}. Error: {error}")
        event = self.task_completion_events.get(schedule_id)
        if event:
            event.set()
        self.task_started = False

    @trace
    async def on_run_start(self, assistant_name, run_identifier, run_start_time, user_input):
        if assistant_name == "CodeProgrammerAgent" or assistant_name == "CodeInspectionAgent":
            print(f"\n{assistant_name}: starting the task with input: {user_input}")
        elif assistant_name == "FileCreatorAgent":
            print(f"\n{assistant_name}: analyzing the CodeProgrammerAgent output for file creation")

    async def on_run_update(self, assistant_name, run_identifier, run_status, thread_name, is_first_message=False, message=None):
        if run_status == "in_progress" and is_first_message:
            print(f"\n{assistant_name}: working on the task", end="", flush=True)
        elif run_status == "in_progress":
            print(".", end="", flush=True)

    @trace
    async def on_run_end(self, assistant_name, run_identifier, run_end_time, thread_name, response=None):
        if response:
            print(f"{assistant_name}: {response}")
        else:
            conversation = await self.conversation_thread_client.retrieve_conversation(thread_name)
            message = conversation.get_last_text_message(assistant_name)
            self.messages.append(message.content)
            print(f"\n{message}")
            if assistant_name == "CodeProgrammerAgent":
                # Extract the JSON code block from the response by using the FileCreatorAgent
                await self._assistants["FileCreatorAgent"].process_messages(user_request=message.content)

    @trace
    async def on_function_call_processed(self, assistant_name, run_identifier, function_name, arguments, response = None):
        if "error" in response:
            print(f"\n{assistant_name}: Function call {function_name} with arguments {arguments}, result failed with: {response}")
        else:
            print(f"\n{assistant_name}: Function call {function_name} with arguments {arguments}, result OK.")

    async def wait_for_all_tasks(self):
        async with self.condition:
            while not self.task_started:
                await self.condition.wait()
            for event in self.task_completion_events.values():
                await event.wait()

    @property
    def assistants(self):
        return self._assistants
    
    @assistants.setter
    def assistants(self, value):
        self._assistants = value


@trace
def load_assistant_config(assistant_name: str) -> Dict:
    """
    Loads the YAML configuration for a given assistant.
    """
    try:
        with open(f"config/{assistant_name}_assistant_config.yaml", "r") as file:
            return file.read()
    except Exception as e:
        print(f"Error loading assistant configuration for {assistant_name}: {e}")
        return None


@trace
async def initialize_assistants(assistant_names: List[str], orchestrator: MultiAgentOrchestrator) -> Dict[str, AsyncAssistantClient]:
    """
    Initializes all assistants based on their names and configuration files.
    """
    assistants = {}
    for assistant_name in assistant_names:
        config = load_assistant_config(assistant_name)
        if config:
            if assistant_name == "TaskPlannerAgent" or assistant_name == "FileCreatorAgent":
                assistants[assistant_name] = await AsyncChatAssistantClient.from_yaml(config, callbacks=orchestrator)
            else:
                assistants[assistant_name] = await AsyncAssistantClient.from_yaml(config, callbacks=orchestrator)
    orchestrator.assistants = assistants
    return assistants


def extract_json_code_block(text):
    """
    Extracts and returns the content of the first JSON code block found in the given text.
    If no JSON code block markers are found, returns the original input text.
    """
    pattern = r"```json\n([\s\S]*?)\n```"
    match = re.search(pattern, text)
    return match.group(1) if match else text


def contains_plan(text):
    """
    Checks if the text contains the word "plan" (case-insensitive).
    """
    # if the text contains json code block, return True, otherwise return False
    return "```json" in text


@tool
async def run_multi_agents(chat_history : list, user_request : str):
    assistant_names = ["CodeProgrammerAgent", "CodeInspectionAgent", "TaskPlannerAgent", "FileCreatorAgent"]
    messages = []
    orchestrator = MultiAgentOrchestrator(messages=messages)
    assistants = await initialize_assistants(assistant_names, orchestrator)
    task_manager = AsyncTaskManager(orchestrator)

    conversation_thread_client = AsyncConversationThreadClient.get_instance(AsyncAIClientType.AZURE_OPEN_AI)
    planner_thread = await conversation_thread_client.create_conversation_thread()

    await conversation_thread_client.create_conversation_thread_message(user_request, planner_thread)
    await assistants["TaskPlannerAgent"].process_messages(thread_name=planner_thread)

    try:
        # Extract the JSON code block from the response for task scheduling
        conversation = await conversation_thread_client.retrieve_conversation(planner_thread)
        response = conversation.get_last_text_message("TaskPlannerAgent")

        if contains_plan(response.content):
            tasks = json.loads(extract_json_code_block(response.content))
        else:
            return dict(result=[response.content])
    except json.JSONDecodeError:
        return dict(result=["Error parsing task scheduling response."])

    multi_task = AsyncMultiTask(tasks)
    await task_manager.schedule_task(multi_task)
    await orchestrator.wait_for_all_tasks()
    await conversation_thread_client.close()

    return dict(result=messages)


if __name__ == "__main__":
    from promptflow.tracing import start_trace
    start_trace()

    result = asyncio.run(run_multi_agents(chat_history = [], user_request="Please create basic CLI application about chat between user and assistant using java programming language"))
    print(result)