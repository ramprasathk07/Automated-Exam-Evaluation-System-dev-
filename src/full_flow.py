import sys,os
from pathlib import Path
import google.generativeai as genai

from utils.get_keys import load_config
from pdf_to_imgs import pdf_to_images
from extract_from_images import extract_text_from_images
from combine_ques_ans import combine_Q_and_A
from format_transcript import parse_answer
from post_proc import post_processing
from Evaluation_bot import Assistant

current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))
load_config('configs/config.yaml')

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

answer_sheet_path = 'data/Answer_sheet.pdf'
question_sheet_path = 'data/question_paper.pdf'

answer_sheet_outpath = pdf_to_images(answer_sheet_path)
question_sheet_outpath = pdf_to_images(question_sheet_path)

answer_result_path = extract_text_from_images(genai,answer_sheet_outpath,'ans')
question_result_path = extract_text_from_images(genai,question_sheet_outpath)

transcript = combine_Q_and_A(genai,
                             answer_json=answer_result_path,
                             question_json=question_result_path)

formatted_trascript = parse_answer(transcript)

transcript = Assistant(formatted_trascript)
formatted_trascript = post_processing(transcript)
