import sys, os
from pathlib import Path
import google.generativeai as genai

from utils.get_keys import load_config
from pdf_to_imgs import pdf_to_images
from extract_from_images import extract_text_from_images
from combine_ques_ans import combine_q_and_a # Updated import name
from format_transcript import parse_answer
from post_proc import post_processing

# from Evaluation_bot import Assistant # Old name
from Evaluation_bot import run_evaluation  # New name

current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Attempt to load configuration, handle if utils or config is not found for standalone run
try:
    load_config("configs/config.yaml")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print(
            "Error: GEMINI_API_KEY not found in environment variables after loading config."
        )
        print(
            "Please ensure configs/config.yaml is present and defines GEMINI_API_KEY or set it in your environment."
        )
        sys.exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
except FileNotFoundError:
    print(
        "Warning: configs/config.yaml not found. Attempting to use GEMINI_API_KEY from environment directly."
    )
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print(
            "Please set the GEMINI_API_KEY environment variable or provide configs/config.yaml."
        )
        sys.exit(1)
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error loading configuration or initializing Gemini: {e}")
    sys.exit(1)


# Create a Gemini Model Instance for full_flow.py
# Similar to get_gemini_model() in app.py
cli_gemini_model_instance = None
try:
    cli_gemini_model_instance = genai.GenerativeModel(
        model_name="gemini-1.5-pro",  # Or "gemini-1.5-flash" if preferred for CLI
        generation_config={
            "temperature": 0.7,  # Example temperature
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",  # Important for evaluation consistency
        },
    )
    print("Gemini model instance for CLI flow created successfully.")
except Exception as e:
    print(f"Error creating Gemini model instance for CLI flow: {e}")
    sys.exit(1)

# Define a base output directory for this flow's outputs
# This helps keep files organized, similar to app.py
cli_output_base_dir = "Evaluation_bot_cli_output"
if not os.path.exists(cli_output_base_dir):
    os.makedirs(cli_output_base_dir)

answer_sheet_pdf_path = (
    "data/Answer_sheet.pdf"  # Relative to project root if data is there
)
question_sheet_pdf_path = "data/question_paper.pdf"  # Relative to project root

# Check if data files exist
if not os.path.exists(answer_sheet_pdf_path):
    print(f"Error: Answer sheet PDF not found at {answer_sheet_pdf_path}")
    sys.exit(1)
if not os.path.exists(question_sheet_pdf_path):
    print(f"Error: Question paper PDF not found at {question_sheet_pdf_path}")
    sys.exit(1)

# --- Stage 1: PDF to Images ---
print(f"Processing PDFs to images...")
# pdf_to_images now creates its output inside "Evaluation_bot/<pdf_name>"
# We might want to make the base "Evaluation_bot" part of cli_output_base_dir too
# For now, let's assume pdf_to_images creates its own "Evaluation_bot" subfolder relative to where script is run
# or we modify pdf_to_images to also take an output_base_dir
qp_image_folder = pdf_to_images(
    question_sheet_pdf_path
)  # Returns path like "Evaluation_bot/question_paper"
ans_image_folder = pdf_to_images(
    answer_sheet_pdf_path
)  # Returns path like "Evaluation_bot/Answer_sheet"
print(f"Question paper images in: {qp_image_folder}")
print(f"Answer sheet images in: {ans_image_folder}")


# --- Stage 2: Images to Text JSON ---
print(f"Extracting text from images...")
qp_json_path = extract_text_from_images(
    gemini_model_instance=cli_gemini_model_instance,
    genai_module=genai,  # Pass the genai module
    path=qp_image_folder,
    typ="ques",
)
ans_json_path = extract_text_from_images(
    gemini_model_instance=cli_gemini_model_instance,
    genai_module=genai,
    path=ans_image_folder,
    typ="ans",
)
print(f"Question paper text JSON: {qp_json_path}")
print(f"Answer sheet text JSON: {ans_json_path}")

# --- Stage 3: Combine Q&A JSONs to Transcript ---
# combine_q_and_a also saves its output in its own "Evaluation_bot" default dir or one specified.
# Let's use our cli_output_base_dir for its output.
print(f"Combining Q&A JSONs...")
combined_transcript_path = combine_q_and_a( # Updated function call
    gemini_model_instance=cli_gemini_model_instance,
    question_json_path=qp_json_path,
    answer_json_path=ans_json_path,
    output_dir=cli_output_base_dir,  # Save transcript in our dedicated CLI output folder
)
print(f"Combined transcript JSON: {combined_transcript_path}")

# --- Stage 4: Parse/Format Transcript ---
# parse_answer also saves its output. Let's use cli_output_base_dir.
print(f"Formatting transcript...")
formatted_transcript_path = parse_answer(
    transcript_json_path=combined_transcript_path, output_dir=cli_output_base_dir
)
print(f"Formatted transcript JSON: {formatted_transcript_path}")

# --- Stage 5: AI Evaluation ---
# run_evaluation also saves its output. Let's use cli_output_base_dir.
print(f"Running AI evaluation...")
evaluation_report_path = run_evaluation(
    genai_model=cli_gemini_model_instance,
    formatted_transcript_path=formatted_transcript_path,
    output_dir=cli_output_base_dir,
)
print(f"Evaluation report JSON: {evaluation_report_path}")

# --- Stage 6: Post-processing Evaluation Report ---
# post_processing also saves its output. Let's use cli_output_base_dir.
print(f"Post-processing evaluation report...")
final_report_path = post_processing(
    evaluation_report_path=evaluation_report_path, output_dir=cli_output_base_dir
)
print(f"Final processed report JSON: {final_report_path}")

print("\n--- CLI Full Flow Completed ---")
print(
    f"All output files should be in subdirectories of: {os.path.abspath(cli_output_base_dir)}"
)
print(
    f"And image folders in: {os.path.abspath(qp_image_folder)} and {os.path.abspath(ans_image_folder)}"
)

# Old calls:
# transcript = combine_Q_and_A(genai,
#                              answer_json=answer_result_path,
#                              question_json=question_result_path)
# formatted_trascript = parse_answer(transcript)
# transcript = Assistant(formatted_trascript)
# formatted_trascript = post_processing(transcript)
