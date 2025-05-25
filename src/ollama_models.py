import os
import json
import sys
import requests
from utils.get_keys import load_config

# Adjust file paths as necessary
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from groq import Groq
# Load the API key from config
load_config('configs/config.yaml')

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

import os
import json
import sys
import requests
from utils.get_keys import load_config

# Adjust file paths as necessary
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from groq import Groq

# Load the API key from config
load_config('configs/config.yaml')


"""
Install the Google AI Python SDK

$ pip install google-generativeai
"""

import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

class GroqModel:
    def __init__(self, model, system_prompt, temperature=0):
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.client = client

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
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            temperature=self.temperature
        )

        response = chat_completion.choices[0].message.content
        print(f"\n\nResponse from Groq model: {response}")
        evaluation_report = json.loads(response)

        with open('evaluation_report.json', 'w') as outfile:
            json.dump(evaluation_report, outfile, indent=4)
        
        print("Evaluation report saved to evaluation_report.json")

        return evaluation_report

# Example usage
from prompts import get_prompt

agent_system_prompt_template = get_prompt(max_marks=10)

model = GroqModel(
    model="llama3-70b-8192",
    system_prompt=agent_system_prompt_template,
    temperature=0
)

question = "Explain the process of photosynthesis in plants."
student_answer = "Photosynthesis is how plants make waste management and does need food for living. are use sunlight, cold, and carbon dioxide to create glucose and oxygen."
rubric = {
    "max_points": 10,
    "criteria": {
        "content_accuracy": 5,
        "comprehension": 3,
        "clarity": 2
    }
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
