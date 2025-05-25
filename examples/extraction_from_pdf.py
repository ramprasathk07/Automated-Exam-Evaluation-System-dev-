import os
import sys
from pathlib import Path
# Assuming 'utils' is in a 'src' directory at the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.get_keys import load_config # Adjusted import
import google.generativeai as genai

# current_dir = Path(__file__).parent.resolve()
# parent_dir = current_dir.parent # This would be project root
# sys.path.append(str(parent_dir))

try:
    load_config('configs/config.yaml') # Assumes 'configs' is at project root
except Exception as e:
    print(f"Warning: Failed to load config 'configs/config.yaml'. Ensure it exists at project root or API keys are set in env. Error: {e}")

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class AIModelEvaluator:
    def __init__(self, temperature=0):
        self.temperature = temperature
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def upload_pdf(self, pdf_path):
        """Uploads a PDF file to Gemini service."""
        try:
            return genai.upload_file(pdf_path)
        except Exception as e:
            print(f"Error uploading PDF {pdf_path}: {e}")
            return None

    def evaluate_pdf_pair(self, answer_sheet_path, question_paper_path):
        """Evaluates the content of two PDFs using Gemini AI."""
        answer_pdf = self.upload_pdf(answer_sheet_path)
        question_pdf = self.upload_pdf(question_paper_path)

        if not answer_pdf or not question_pdf:
            print("Failed to upload one or both PDFs.")
            return None

        input_prompt = [
            "Extract all questions from the question paper and align them with the student answers from the answer sheet.",
            f"Provide question numbers and total marks for each question.\n\n"
            f"Answer Sheet: {answer_pdf}\n\nQuestion Paper: {question_pdf}"
        ]

        try:
            response = self.model.generate_content(input_prompt)
            return response.text
        except Exception as e:
            print(f"An error occurred during generation: {e}")
            return None

if __name__ == "__main__":
    evaluator = AIModelEvaluator()
    answer_sheet = "Answer_sheet.pdf"
    question_paper = "question_paper.pdf"
    result = evaluator.evaluate_pdf_pair(answer_sheet, question_paper)
    print("Evaluation Result:\n", result)
