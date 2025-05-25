import os
import json

# import sys # Not strictly needed if utils.get_keys is not used or path is handled by caller
# import requests # Not used in the provided snippet of Assistant or AIModelEvaluator
# from utils.get_keys import load_config # Assuming config is handled by app.py

# current_dir = os.path.dirname(os.path.abspath(__file__)) # Not needed for direct import
# parent_dir = os.path.dirname(current_dir) # Not needed for direct import
# sys.path.append(parent_dir) # Not needed for direct import

# load_config('configs/config.yaml') # Configuration will be handled by app.py

# from groq import Groq # Groq client will be passed if used
# client = Groq(api_key=os.environ.get("GROQ_API_KEY")) # Client init will be in app.py

# import google.generativeai as genai # genai will be passed as an object
# genai.configure(api_key=os.environ["GEMINI_API_KEY"]) # Configuration will be in app.py

# Default generation config, can be customized if needed when model is created in app.py
DEFAULT_GENERATION_CONFIG = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",  # Expecting JSON, so this might need to be "application/json"
}

# gemini_model = genai.GenerativeModel( # Model object will be passed to AIModelEvaluator
#     model_name="gemini-1.5-pro",
#     generation_config=generation_config,
# )


class AIModelEvaluator:
    def __init__(
        self,
        client,
        model_type="gemini",
        system_prompt="You are a helpful AI assistant.",
        temperature=0.7,
    ):
        """
        Initializes the evaluator.
        client: The pre-configured AI client (e.g., Gemini GenaiModel or Groq client).
        model_type: String, "gemini" or "groq" (or others).
        """
        self.client = client
        self.model_type = model_type
        self.system_prompt = system_prompt  # System prompt can be part of the client (e.g. Gemini) or used in API call
        self.temperature = temperature

    def evaluate_answer(self, question, student_answer, max_marks):
        # The prompt expects the model to return a JSON string.
        # For Gemini, ensure response_mime_type="application/json" is set in generation_config if possible,
        # or instruct the model clearly to output JSON.
        rubric = {
            "max_points": max_marks,
            "criteria": {
                "content_accuracy": max_marks * 0.5,
                "comprehension": max_marks * 0.3,
                "clarity": max_marks * 0.2,
            },
        }

        # Construct the evaluation prompt
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
                    {"role": "user", "content": prompt},
                ],
                model=self.model_type,
                temperature=self.temperature,
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

        return evaluation_report

    def evaluate_from_json(self, json_data):
        reports = {}
        for key, value in json_data.items():
            question = value["Question"]
            student_answer = " ".join(value["Student Answer"])
            max_marks = value["Total Marks"]

            print(f"Evaluating {key} with max marks: {max_marks}...")

            report = self.evaluate_answer(question, student_answer, max_marks)
            reports[key] = report

        outfile = f"Evaluation_bot/evaluation_reports_{self.model_type}.json"
        with open(outfile, "w") as outfile:
            json.dump(reports, outfile, indent=4)

        print(f"Evaluation reports saved to evaluation_reports_{self.model_type}.json")
        return outfile


def Assistant(path):
    gemini_evaluator = AIModelEvaluator(model_type="gemini", temperature=1)

    with open(path, "r") as f:
        input_json = json.load(f)

    outfile = gemini_evaluator.evaluate_from_json(input_json)
    return outfile
