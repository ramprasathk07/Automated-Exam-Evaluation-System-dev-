import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import google.generativeai as genai

# Import your refactored functions
from pdf_to_imgs import pdf_to_images
from extract_from_images import extract_text_from_images

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config["DEBUG"] = True  # Development mode
# PORT environment variable will be used if set, otherwise default to 5001
FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT", 5001)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Configure Gemini API
# IMPORTANT: Ensure GEMINI_API_KEY environment variable is set
try:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        print("WARNING: GEMINI_API_KEY environment variable not set.")
        # You might want to raise an error or have a fallback if the API key is critical
    else:
        genai.configure(api_key=gemini_api_key)
except Exception as e:
    print(f"Error configuring Gemini API: {e}")


@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from Flask!"})


@app.route("/api/upload", methods=["POST"])
def upload_files():
    if "question_paper" not in request.files or "answer_sheet" not in request.files:
        return (
            jsonify({"error": "Missing question_paper or answer_sheet in the request"}),
            400,
        )

    question_paper = request.files["question_paper"]
    answer_sheet = request.files["answer_sheet"]

    if question_paper.filename == "" or answer_sheet.filename == "":
        return jsonify({"error": "One or both files have no selected file name"}), 400

    if question_paper and answer_sheet:
        question_paper_filename = secure_filename(question_paper.filename)
        answer_sheet_filename = secure_filename(answer_sheet.filename)

        question_paper_path = os.path.join(
            app.config["UPLOAD_FOLDER"], question_paper_filename
        )
        answer_sheet_path = os.path.join(
            app.config["UPLOAD_FOLDER"], answer_sheet_filename
        )

        try:
            question_paper.save(question_paper_path)
            answer_sheet.save(answer_sheet_path)

            # After successful upload, proceed to process the documents
            # This assumes the next step is to call process_documents with these paths
            # For now, just return success and paths
            return (
                jsonify(
                    {
                        "message": "Files uploaded successfully. Ready for processing.",
                        "question_paper_filename": question_paper_filename,  # Return filename for constructing path later
                        "answer_sheet_filename": answer_sheet_filename,  # Return filename for constructing path later
                        # "question_paper_path": question_paper_path, # These paths are server-side
                        # "answer_sheet_path": answer_sheet_path
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": f"Failed to save files: {str(e)}"}), 500

    return jsonify({"error": "Unknown error during file upload"}), 500


@app.route("/api/process_documents", methods=["POST"])
def process_documents_route():
    data = request.get_json()
    question_paper_filename = data.get("question_paper_filename")
    answer_sheet_filename = data.get("answer_sheet_filename")

    if not question_paper_filename or not answer_sheet_filename:
        return (
            jsonify({"error": "Missing filenames for question paper or answer sheet"}),
            400,
        )

    question_paper_path = os.path.join(
        app.config["UPLOAD_FOLDER"], question_paper_filename
    )
    answer_sheet_path = os.path.join(app.config["UPLOAD_FOLDER"], answer_sheet_filename)

    if not os.path.exists(question_paper_path) or not os.path.exists(answer_sheet_path):
        return (
            jsonify(
                {
                    "error": "One or both uploaded files not found on server. Upload again."
                }
            ),
            404,
        )

    if not genai.Key:  # Check if genai was configured (basic check)
        return jsonify({"error": "Gemini API not configured on server."}), 500

    gemini_model_instance = get_gemini_model()  # Get the shared instance
    if not gemini_model_instance:
        return (
            jsonify(
                {
                    "error": "Gemini API not configured or model could not be initialized."
                }
            ),
            500,
        )

    try:
        processing_results = _run_document_processing_pipeline(
            question_paper_path,
            answer_sheet_path,
            gemini_model_instance,
            genai,  # Pass the genai module
        )
        return jsonify(processing_results), 200
    except FileNotFoundError as fnfe:
        return jsonify({"error": f"File not found during processing: {str(fnfe)}"}), 404
    except Exception as e:
        print(f"Error in /api/process_documents: {str(e)}")
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                {"error": f"An error occurred during document processing: {str(e)}"}
            ),
            500,
        )


def _run_document_processing_pipeline(
    question_paper_path, answer_sheet_path, gemini_model_instance, genai_module
):
    """Helper function to run the document processing pipeline."""
    # 1. Convert PDFs to images
    qp_img_output_folder = pdf_to_images(question_paper_path)
    ans_img_output_folder = pdf_to_images(answer_sheet_path)

    # 2. Extract text from images using Gemini
    qp_json_path = extract_text_from_images(
        gemini_model_instance=gemini_model_instance,
        genai_module=genai_module,
        path=qp_img_output_folder,
        typ="ques",
    )
    ans_json_path = extract_text_from_images(
        gemini_model_instance=gemini_model_instance,
        genai_module=genai_module,
        path=ans_img_output_folder,
        typ="ans",
    )
    return {
        "message": "Documents processed successfully",
        "question_paper_images_path": qp_img_output_folder,
        "answer_sheet_images_path": ans_img_output_folder,
        "question_paper_json_path": qp_json_path,
        "answer_sheet_json_path": ans_json_path,
    }


# --- Evaluation Orchestration ---
from combine_ques_ans import combine_q_and_a # Updated import name
from format_transcript import parse_answer
from Evaluation_bot import run_evaluation  # Refactored Assistant
from post_proc import post_processing

# Global variable to store the path of the last generated final report (for simplicity)
# In a real app, use a database or proper job management.
LAST_FINAL_REPORT_PATH = None
GEMINI_MODEL_INSTANCE = None  # To store the initialized gemini model


def get_gemini_model():
    global GEMINI_MODEL_INSTANCE
    if GEMINI_MODEL_INSTANCE is None:
        if genai.Key:  # Check if genai was configured
            GEMINI_MODEL_INSTANCE = genai.GenerativeModel(
                model_name="gemini-1.5-pro",  # Or your preferred model
                generation_config={  # Ensure this requests JSON if possible
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",  # IMPORTANT for AIModelEvaluator
                },
            )
        else:
            print("ERROR: Gemini API not configured, cannot create model instance.")
            return None
    return GEMINI_MODEL_INSTANCE


@app.route("/api/evaluate", methods=["POST"])
def evaluate_documents_route():
    global LAST_FINAL_REPORT_PATH
    data = request.get_json()

    # Paths from the /api/process_documents output
    question_json_path = data.get("question_paper_json_path")
    answer_json_path = data.get("answer_sheet_json_path")

    if not question_json_path or not answer_json_path:
        return (
            jsonify(
                {"error": "Missing JSON file paths for question paper or answer sheet"}
            ),
            400,
        )

    if not os.path.exists(question_json_path) or not os.path.exists(answer_json_path):
        return (
            jsonify({"error": "One or both processed JSON files not found on server."}),
            404,
        )

    gemini_model_instance = get_gemini_model()
    if not gemini_model_instance:
        return (
            jsonify(
                {
                    "error": "Gemini API not configured or model could not be initialized."
                }
            ),
            500,
        )

    try:
        evaluation_results = _run_full_evaluation_pipeline(
            question_json_path, answer_json_path, gemini_model_instance
        )
        LAST_FINAL_REPORT_PATH = evaluation_results[
            "final_report_path"
        ]  # Store for /api/results
        return jsonify(evaluation_results), 200
    except FileNotFoundError as fnfe:
        return jsonify({"error": f"File not found during evaluation: {str(fnfe)}"}), 404
    except ValueError as ve:
        return jsonify({"error": f"Data error during evaluation: {str(ve)}"}), 400
    except Exception as e:
        print(f"Error in /api/evaluate: {str(e)}")
        import traceback

        traceback.print_exc()
        return (
            jsonify(
                {"error": f"An unexpected error occurred during evaluation: {str(e)}"}
            ),
            500,
        )


def _run_full_evaluation_pipeline(
    question_json_path, answer_json_path, gemini_model_instance
):
    """Helper function to run the full evaluation pipeline."""
    # Define a base output directory for this evaluation run
    base_output_name = os.path.splitext(os.path.basename(question_json_path))[
        0
    ].replace("_ques_data", "")
    evaluation_run_output_dir = os.path.join(
        "Evaluation_bot", base_output_name + "_evaluation_files"
    )
    if not os.path.exists(evaluation_run_output_dir):
        os.makedirs(evaluation_run_output_dir)

    print(f"Starting evaluation pipeline for {base_output_name}...")

    # 1. Combine Question and Answer JSONs into a transcript
    print(f"Step 1: Combining Q&A for {question_json_path} and {answer_json_path}")
    combined_transcript_path = combine_q_and_a( # Updated function call
        gemini_model_instance=gemini_model_instance,
        question_json_path=question_json_path,
        answer_json_path=answer_json_path,
        output_dir=evaluation_run_output_dir,
    )
    print(f"Combined transcript at: {combined_transcript_path}")

    # 2. Parse/Format the combined transcript
    print(f"Step 2: Formatting transcript {combined_transcript_path}")
    formatted_transcript_path = parse_answer(
        transcript_json_path=combined_transcript_path,
        output_dir=evaluation_run_output_dir,
    )
    print(f"Formatted transcript at: {formatted_transcript_path}")

    # 3. Run AI Evaluation
    print(f"Step 3: Running AI evaluation for {formatted_transcript_path}")
    evaluation_report_path = run_evaluation(
        genai_model=gemini_model_instance,
        formatted_transcript_path=formatted_transcript_path,
        output_dir=evaluation_run_output_dir,
    )
    print(f"Evaluation report at: {evaluation_report_path}")

    # 4. Post-process the evaluation report
    print(f"Step 4: Post-processing report {evaluation_report_path}")
    final_report_path = post_processing(
        evaluation_report_path=evaluation_report_path,
        output_dir=evaluation_run_output_dir,
    )
    print(f"Final report at: {final_report_path}")

    return {
        "message": "Evaluation pipeline completed successfully.",
        "final_report_path": final_report_path,
        "intermediate_steps": {
            "combined_transcript": combined_transcript_path,
            "formatted_transcript": formatted_transcript_path,
            "raw_evaluation_report": evaluation_report_path,
        },
    }


@app.route("/api/results/<job_id>", methods=["GET"])
def get_results_route(job_id):
    # For this task, job_id is ignored, and we return the last generated report.
    # In a real application, job_id would be used to fetch specific results from a DB.
    global LAST_FINAL_REPORT_PATH

    print(f"API: Request for results with job_id: {job_id} (currently ignored).")
    print(f"API: Last known report path: {LAST_FINAL_REPORT_PATH}")

    if LAST_FINAL_REPORT_PATH and os.path.exists(LAST_FINAL_REPORT_PATH):
        try:
            with open(LAST_FINAL_REPORT_PATH, "r") as f:
                results_data = json.load(f)
            return jsonify(results_data), 200
        except Exception as e:
            print(
                f"Error reading or serving results file {LAST_FINAL_REPORT_PATH}: {e}"
            )
            return jsonify({"error": f"Failed to read results file: {str(e)}"}), 500
    elif LAST_FINAL_REPORT_PATH:  # Path exists but file doesn't
        return (
            jsonify(
                {
                    "error": "The last evaluation result file seems to be missing.",
                    "path_searched": LAST_FINAL_REPORT_PATH,
                }
            ),
            404,
        )
    else:
        return (
            jsonify(
                {
                    "message": "No evaluation results available yet. Please run an evaluation first."
                }
            ),
            404,
        )


if __name__ == "__main__":
    # Note: When using `flask run`, it uses FLASK_RUN_PORT and FLASK_DEBUG.
    # This __main__ block is for direct `python src/app.py` execution.
    app.run(host="0.0.0.0", port=int(FLASK_RUN_PORT))
