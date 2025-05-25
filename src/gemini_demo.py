import os
import json
import sys
import requests
from utils.get_keys import load_config

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

load_config('configs/config.yaml')

from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

gemini_model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

class AIModelEvaluator:
    def __init__(self, model_type="groq", system_prompt=None, temperature=0):
        self.model_type = model_type
        self.system_prompt = system_prompt
        self.temperature = temperature
        if model_type == "groq":
            self.client = client
        elif model_type == "gemini":
            self.client = gemini_model

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

        if self.model_type == "groq":
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_type,
                temperature=self.temperature
            )
            response = chat_completion.choices[0].message.content

        elif self.model_type == "gemini":
            chat_session = self.client.start_chat(history=[])
            response = chat_session.send_message(prompt).text

        print(f"\n\nResponse from {self.model_type} model: {response}")

        try:
            evaluation_report = json.loads(response)
        except json.JSONDecodeError:
            evaluation_report = {"evaluation_report": response}
        
        # Save the evaluation report as a JSON file
        # with open(f'evaluation_report_{self.model_type}.json', 'w') as outfile:
        #     json.dump(evaluation_report, outfile, indent=4)

        broken_response = response.split("\n")
        evaluation_report = {"evaluation_report": broken_response}
        
        with open(f'evaluation_report.json', 'w') as outfile:
            json.dump(evaluation_report, outfile, indent=4)
        
        print(f"Evaluation report saved to evaluation_report_{self.model_type}.json")
        return evaluation_report

if __name__ == "__main__":
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

    from prompts import get_prompt
    agent_system_prompt_template = get_prompt(max_marks=10)

    # Initialize the evaluator for Groq
    # groq_evaluator = AIModelEvaluator(
    #     model_type="groq",
    #     system_prompt=agent_system_prompt_template,
    #     temperature=0
    # )

    gemini_evaluator = AIModelEvaluator(
        model_type="gemini",
        temperature=1 
    )

    gemini_evaluation = gemini_evaluator.evaluate_answer(question, student_answer, rubric)

    # print("\nGroq Evaluation:\n", groq_evaluation)
    print("\nGemini Evaluation:\n", gemini_evaluation)
