# import os
# import sys
# # current_dir = os.path.dirname(os.path.abspath(__file__))
# # parent_dir = os.path.dirname(current_dir)
# # sys.path.append(parent_dir)

# from termcolor import colored
# from prompts import agent_system_prompt_template
# # from openai_models import OpenAIModel
# from ollama_models import GroqModel
# from toolbox import ExamEvaluatorToolBox


# class Agent:
#     def __init__(self, tools, model_service, model_name, stop=None):
#         """
#         Initializes the agent with a list of tools and a model.

#         Parameters:
#         tools (list): List of tool functions.
#         model_service (class): The model service class with a generate_text method.
#         model_name (str): The name of the model to use.
#         """
#         self.tools = tools
#         self.model_service = model_service
#         self.model_name = model_name
#         self.stop = stop

#     def prepare_tools(self):
#         """
#         Stores the tools in the toolbox and returns their descriptions.

#         Returns:
#         str: Descriptions of the tools stored in the toolbox.
#         """
#         toolbox = ExamEvaluatorToolBox()
#         toolbox.store(self.tools)
#         tool_descriptions = toolbox.tools()
#         return tool_descriptions

#     def think(self, prompt):
#         """
#         Runs the generate_text method on the model using the system prompt template and tool descriptions.

#         Parameters:
#         prompt (str): The user query to generate a response for.

#         Returns:
#         dict: The response from the model as a dictionary.
#         """
#         tool_descriptions = self.prepare_tools()
#         print(tool_descriptions)
#         agent_system_prompt = agent_system_prompt_template.format(tool_descriptions=tool_descriptions)

#         # Create an instance of the model service with the system prompt

#         if self.model_service == GroqModel:
#             model_instance = self.model_service(
#                 model=self.model_name,
#                 system_prompt=agent_system_prompt,
#                 temperature=0,
#                 stop=self.stop
#             )
#         else:
#             model_instance = self.model_service(
#                 model=self.model_name,
#                 system_prompt=agent_system_prompt,
#                 temperature=0
#             )

#         # Generate and return the response dictionary
#         agent_response_dict = model_instance.generate_text(prompt)
#         return agent_response_dict

#     def work(self, prompt):
#         """
#         Parses the dictionary returned from think and executes the appropriate tool.

#         Parameters:
#         prompt (str): The user query to generate a response for.

#         Returns:
#         The response from executing the appropriate tool or the tool_input if no matching tool is found.
#         """
#         agent_response_dict = self.think(prompt)
#         tool_choice = agent_response_dict.get("tool_choice")
#         tool_input = agent_response_dict.get("tool_input")

#         for tool in self.tools:
#             if tool.__name__ == tool_choice:
#                 response = tool(tool_input)

#                 print(colored(response, 'cyan'))
#                 return
#                 # return tool(tool_input)

#         print(colored(tool_input, 'cyan'))

#         return

# # Example usage
# if __name__ == "__main__":
#     from correction_tools import check_spelling
#     tools = [check_spelling]

#     # Uncoment below to run with OpenAI
#     # model_service = OpenAIModel
#     # model_name = 'gpt-3.5-turbo'
#     # stop = None

#     # Uncomment below to run with Ollama
#     model_service = GroqModel
#     model_name = 'llama3:instruct'
#     stop = "<|eot_id|>"

#     agent = Agent(tools=tools, model_service=model_service, model_name=model_name, stop=stop)

#     while True:
#         prompt = input("Ask me anything: ")
#         if prompt.lower() == "exit":
#             break

#         agent.work(prompt)

import os
import sys
import json
from termcolor import colored
from ..prompts import agent_system_prompt_template  # Adjusted import
from .ollama_models import GroqModel  # Adjusted import
from ..toolbox import (
    ExamEvaluatorToolBox,
)  # Adjusted import, assuming toolbox is in src


class Agent:
    def __init__(self, tools, model_service, model_name, stop=None):
        """
        Initializes the agent with a list of tools and a model.

        Parameters:
        tools (list): List of tool functions.
        model_service (class): The model service class with a generate_text method.
        model_name (str): The name of the model to use.
        """
        self.tools = tools
        self.model_service = model_service
        self.model_name = model_name
        self.stop = stop

    def prepare_tools(self):
        """
        Stores the tools in the toolbox and returns their descriptions.

        Returns:
        str: Descriptions of the tools stored in the toolbox.
        """
        toolbox = ExamEvaluatorToolBox()
        toolbox.store(self.tools)
        tool_descriptions = toolbox.tools()
        return tool_descriptions

    def think(self, prompt, question, answer):
        # Generate the response from the model
        tool_descriptions = self.prepare_tools()
        agent_system_prompt = agent_system_prompt_template.format(
            tool_descriptions=tool_descriptions, question=question, answer=answer
        )

        model_instance = self.model_service(
            model=self.model_name,
            system_prompt=agent_system_prompt,
            temperature=0,
            stop=self.stop,
        )

        agent_response_dict = model_instance.generate_text(prompt)
        print(
            {
                "tool_choice": agent_response_dict.get("tool_choice", "no tool"),
                "tool_input": agent_response_dict.get("tool_input", ""),
                "marks_awarded": agent_response_dict.get(
                    "marks_awarded", {"evaluation": "", "score": 0, "feedback": ""}
                ),
            }
        )
        # Make sure to fill in defaults if any key is missing
        return {
            "tool_choice": agent_response_dict.get("tool_choice", "no tool"),
            "tool_input": agent_response_dict.get("tool_input", ""),
            "marks_awarded": agent_response_dict.get(
                "marks_awarded", {"evaluation": "", "score": 0, "feedback": ""}
            ),
        }

    def work(self, question, answer):
        """
        Parses the dictionary returned from think and executes the appropriate tool.

        Parameters:
        question (str): The student's question.
        answer (str): The student's answer.

        Returns:
        dict: The final result with the evaluation and score.
        """
        # Combine the student's question and answer into a prompt
        prompt = f"Student's question: {question}\nStudent's answer: {answer}"
        agent_response_dict = self.think(prompt, question, answer)

        tool_choice = agent_response_dict.get("tool_choice")
        tool_input = agent_response_dict.get("tool_input")
        marks_awarded = agent_response_dict.get("marks_awarded")
        print(f"tool_choice:{tool_choice}")
        # Execute the chosen tool
        for tool in self.tools:
            if tool.__name__ == tool_choice:
                tool_response = tool(tool_input)
                marks_awarded["evaluation"] = tool_response
                break

        # Return the final evaluation and score
        return marks_awarded


# Example usage
if __name__ == "__main__":
    # If running as a script, sys.path might need adjustment to find parent 'src' modules
    # For example, by adding project root to sys.path
    # This is tricky for scripts inside packages if they rely on sibling packages not in PYTHONPATH.
    # However, for now, let's assume it's run as part of a larger context where src is accessible
    # or these tools are also moved/self-contained.
    try:
        from ..correction_tools import (
            check_spelling,
            calculate_score,
            evaluate_answer,
            check_plagiarism,
        )  # Adjusted import
    except ImportError:
        # Fallback for direct script execution if ..correction_tools is not found
        # This implies correction_tools.py might be in src/ or src/legacy_agent/
        # If it's in src/, the above relative import is correct when agent.py is treated as part of a package.
        # If it's also legacy and moved to src/legacy_agent, then from .correction_tools import ...
        # For now, sticking to the assumption it's in src/
        print(
            "Warning: Could not import correction_tools using relative import from src. Ensure PYTHONPATH is set correctly if running as script."
        )
        # As a last resort for the __main__ block, if it's meant to be runnable standalone:
        current_dir_for_main = os.path.dirname(os.path.abspath(__file__))
        src_dir_for_main = os.path.dirname(current_dir_for_main)
        if src_dir_for_main not in sys.path:
            sys.path.append(src_dir_for_main)
        from correction_tools import (
            check_spelling,
            calculate_score,
            evaluate_answer,
            check_plagiarism,
        )

    tools = [evaluate_answer]

    # Uncomment below to run with GroqModel
    model_service = GroqModel
    model_name = "llama3-8b-8192"
    stop = "<|eot_id|>"

    agent = Agent(
        tools=tools, model_service=model_service, model_name=model_name, stop=stop
    )

    while True:
        question = input("Enter the student's question: ")
        answer = input("Enter the student's answer: ")

        if question.lower() == "exit" or answer.lower() == "exit":
            break

        result = agent.work(question, answer)
        print(colored(json.dumps(result, indent=4), "cyan"))
