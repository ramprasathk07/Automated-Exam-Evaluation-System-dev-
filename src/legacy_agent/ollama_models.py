import os
import json

# import sys # Avoid sys.path modifications if possible
# import requests # Not used by GroqModel directly
from ..utils.get_keys import load_config  # Adjusted import, assuming utils is in src
from groq import Groq

# import google.generativeai as genai # This module is not primarily for Gemini

# Attempt to load config for GROQ_API_KEY. This should ideally be handled once at app startup.
# For a legacy module, this direct loading might be kept, but it's not best practice.
try:
    # Assuming load_config sets environment variables
    # The original sys.path manipulation was to find 'configs/config.yaml' relative to project root.
    # This will only work if this script is run from a context where 'parent_dir' (src) allows access
    # to the project root for 'configs/config.yaml'.
    # A better way for legacy code might be to specify an absolute path or make config path an arg.
    # For now, assume load_config can find 'configs/config.yaml' if PYTHONPATH is set to project root.

    # To make load_config potentially work if 'utils' is in 'src' and 'configs' is at project root:
    # project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    # config_path = os.path.join(project_root, 'configs/config.yaml')
    # load_config(config_path) # This assumes load_config can take a direct path

    # Simpler assumption: load_config relies on 'configs/config.yaml' being findable from CWD or via PYTHONPATH.
    # This part is tricky without knowing how load_config works or what CWD is.
    # The original code did:
    # current_dir = os.path.dirname(os.path.abspath(__file__)) # .../src/legacy_agent
    # parent_dir = os.path.dirname(current_dir) # .../src
    # sys.path.append(parent_dir) # Adds 'src' to path
    # from utils.get_keys import load_config
    # load_config('configs/config.yaml') # This would look for 'src/configs/config.yaml' - unlikely.
    # It should be load_config('../../configs/config.yaml') or similar if path relative to this file,
    # or an absolute path, or rely on PYTHONPATH.

    # Given it's legacy, let's assume load_config is expected to work by means outside this script's direct control
    # (e.g. PYTHONPATH being set to project root, and load_config uses 'configs/config.yaml')
    load_config("configs/config.yaml")
except Exception as e:
    print(f"Warning: Could not load config for GroqModel in ollama_models.py: {e}")
    print("Ensure GROQ_API_KEY is set in the environment if config loading fails.")


GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    print("Warning: GROQ_API_KEY not found in environment. GroqModel may not work.")
    # raise ValueError("GROQ_API_KEY not found.") # Or raise error

# Initialize Groq client globally or per instance. Global is simpler for this legacy file.
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("Warning: Groq client not initialized due to missing API key.")


# Removed the out-of-place Gemini example code block that was here.


class GroqModel:
    def __init__(self, model, system_prompt, temperature=0):
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        if not groq_client:
            raise RuntimeError("Groq client not initialized. Check API key and config.")
        self.client = groq_client  # Use the globally initialized client

    def evaluate_answer(self, question, student_answer, rubric):
        prompt = f"""
        You are an exam evaluator. Your task is to evaluate a student's answer based on the following question and grading rubric:

        Question: {question}
        Student Answer: {student_answer}
        Grading Rubric: {json.dumps(rubric)}

        Please provide a detailed evaluation report with the following sections:
        
        1. **Evaluation:** Whether the answer is "correct", "partially correct", or "incorrect" based on the rubric.
        2. **Score:** Award points for each of the following criteria:
            - Content Accuracy: {rubric['criteria']['content_accuracy']} points
            - Comprehension: {rubric['criteria']['comprehension']} points
            - Clarity: {rubric['criteria']['clarity']} points
        3. **Strengths:** Highlight specific strengths of the student's answer.
        4. **Weaknesses:** Highlight specific weaknesses or errors in the answer.
        5. **Spelling Errors:** Detect and report the number of spelling errors.
        6. **Constructive Feedback:** Provide suggestions on how the student can improve their answer for each evaluation criterion.
        """

        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
            temperature=self.temperature,
        )

        response = chat_completion.choices[0].message.content
        print(f"\n\nResponse from Groq model: {response}")
        evaluation_report = json.loads(response)

        with open("evaluation_report.json", "w") as outfile:
            json.dump(evaluation_report, outfile, indent=4)

        print("Evaluation report saved to evaluation_report.json")

        return evaluation_report


# Example usage
from ..prompts import get_prompt  # Adjusted import

# Ensure agent_system_prompt_template is loaded only if get_prompt succeeds
prompt_template_text = get_prompt(max_marks=10)
if prompt_template_text is None:
    # Fallback or error if prompt is not loaded, as GroqModel example relies on it
    print(
        "Error: Could not load prompt template for GroqModel example. Using a generic prompt."
    )
    # Provide a very basic fallback if needed for the example to run at all
    agent_system_prompt_template = "You are a helpful assistant."
else:
    agent_system_prompt_template = prompt_template_text


# This example usage block should ideally be in an if __name__ == "__main__":
# For now, it runs when the module is imported if not guarded.
# Assuming it's for demonstration or testing within this legacy module.

# Check if groq_client is available before trying to use it in example
if groq_client:
    model = GroqModel(
        model="llama3-70b-8192",
        system_prompt=agent_system_prompt_template,
        temperature=0,
    )

    question = "Explain the process of photosynthesis in plants."
    student_answer = "Photosynthesis is how plants make waste management and does need food for living. are use sunlight, cold, and carbon dioxide to create glucose and oxygen."
    rubric = {
        "max_points": 10,
        "criteria": {"content_accuracy": 5, "comprehension": 3, "clarity": 2},
    }

    try:
        evaluation = model.evaluate_answer(question, student_answer, rubric)
        print(evaluation)
    except Exception as e:
        print(f"Error during GroqModel example evaluation: {e}")
else:
    print("Skipping GroqModel example usage as client is not initialized.")

model = GroqModel(
    model="llama3-70b-8192", system_prompt=agent_system_prompt_template, temperature=0
)

question = "Explain the process of photosynthesis in plants."
student_answer = "Photosynthesis is how plants make waste management and does need food for living. are use sunlight, cold, and carbon dioxide to create glucose and oxygen."
rubric = {
    "max_points": 10,
    "criteria": {"content_accuracy": 5, "comprehension": 3, "clarity": 2},
}

evaluation = model.evaluate_answer(question, student_answer, rubric)

print(evaluation)

# import os
# import json
# from groq import Groq

# # Initialize the Groq client with the API key from the environment
# client = Groq(
#     api_key=os.environ.get("GROQ_API_KEY")
# )

# class GroqModel:
#     def __init__(self, model, system_prompt, temperature=0):
#         self.client = client
#         self.model = model
#         self.system_prompt = system_prompt
#         self.temperature = temperature

#     def evaluate_answer(self, question, student_answer, rubric):
#         # Construct the prompt with the question, answer, and rubric
#         prompt = f"""
#             Question: {question}
#             Student Answer: {student_answer}
#             Grading Rubric: {json.dumps(rubric)}

#             Please evaluate the student's answer based on the question and grading rubric.
#             Provide a JSON response with the following structure:
#             {{
#                 "evaluation": "correct" or "partially correct" or "incorrect",
#                 "score": (points awarded based on rubric),
#                 "feedback": (detailed feedback explaining the evaluation),
#                 "spelling_errors": (number of spelling mistakes detected)
#             }}
#         """

#         # Call the model to generate a completion based on the constructed prompt
#         chat_completion = self.client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": self.system_prompt},
#                 {"role": "user", "content": prompt}
#             ],
#             model=self.model,
#             temperature=self.temperature
#         )

#         # Extract the response from the model
#         response = chat_completion.choices[0].message.content
#         print(f"\n\nResponse from Groq model: {response}")

#         return json.loads(response)  # Return the response as a Python dictionary

# # Example usage
# from prompts import get_prompt

# # Load the system prompt template
# agent_system_prompt_template = get_prompt(max_marks=10)

# # Initialize the model
# model = GroqModel(
#     model="llama3-70b-8192",
#     system_prompt=agent_system_prompt_template,
#     temperature=0
# )

# # Example question, student answer, and rubric for evaluation
# question = "Explain the process of photosynthesis in plants."
# student_answer = "Photosynthesis is how plants make waste management and does need food for living. are use sunlight, cold, and carbon dioxide to create glucose and oxygen."
# rubric = {
#     "max_points": 10,
#     "criteria": {
#         "content_accuracy": 5,
#         "comprehension": 3,
#         "clarity": 2
#     }
# }

# # Evaluate the student's answer
# evaluation = model.evaluate_answer(question, student_answer, rubric)
# print(evaluation)
