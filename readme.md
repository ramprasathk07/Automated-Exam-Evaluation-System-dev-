# Automated Exam Evaluation System with AI

This project provides an AI-powered system for automated exam evaluation, featuring a user-friendly web interface and a RESTful API for programmatic access. It streamlines the assessment process by leveraging large language models (LLMs) like Google's Gemini to provide comprehensive feedback and scoring for student answer sheets.

## Pitch

Tired of the manual grind of exam grading? This system offers a modern solution, allowing educators to upload question papers and student answer sheets (as PDFs), and receive detailed evaluations including scores, strengths, weaknesses, and constructive feedback. The new React-based UI makes interaction intuitive, while the Flask backend provides a robust API for integration and automation.

## Features

*   **React-based User Interface:** Modern, responsive, and user-friendly interface for managing evaluations.
*   **Flask API for Programmatic Access:**
    *   Upload question papers and answer sheets.
    *   Initiate document processing (PDF to text).
    *   Trigger AI-powered evaluation.
    *   Retrieve evaluation results.
*   **PDF Document Processing:** Converts PDF question papers and answer sheets into images for text extraction.
*   **AI Text Extraction:** Utilizes Gemini API to accurately extract text from images, aiming to preserve structure.
*   **Question and Answer Alignment:** AI-assisted alignment of questions from the paper with answers from the student's sheet.
*   **AI-Powered Evaluation:** Employs Google's Gemini model to assess student answers based on the provided questions and (implicitly) a rubric.
*   **Detailed Feedback Generation:** Produces comprehensive reports including:
    *   Overall evaluation (correct, partially correct, incorrect).
    *   Score breakdown (if applicable).
    *   Strengths and weaknesses of the answer.
    *   Spelling error count.
    *   Constructive feedback for improvement.
*   **Modular Pipeline:** The backend processes documents in stages: PDF to images, image to text, Q&A alignment, evaluation, and post-processing.

## Tech Stack

*   **Backend:**
    *   Python
    *   Flask (for the REST API)
    *   Google Gemini API (for AI-driven text extraction and evaluation)
    *   PyMuPDF (Fitz) (for PDF processing)
*   **Frontend:**
    *   React (JavaScript library for UI)
    *   HTML/CSS
*   **General:**
    *   JSON (for data interchange)

## Screenshots/GIFs

<!-- Add Screenshots/GIFs of the new UI and application flow here -->
*UI showing file upload, progress, and results display.*

## Prerequisites

*   Python 3.8+
*   Node.js 14.x+ and npm 6.x+ (or yarn)
*   Google Gemini API Key

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/automated-exam-evaluation-system.git # Replace with actual repository URL
cd automated-exam-evaluation-system
```

### 2. Backend Setup

*   **Create and Activate Python Virtual Environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

*   **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

*   **Configure API Keys:**
    *   The primary method for API key configuration is through a `configs/config.yaml` file at the project root. If this file is not present, the system will attempt to fall back to environment variables.
    *   Create a `configs` directory in the project root if it doesn't exist.
    *   Inside `configs`, create a `config.yaml` file with your Google Gemini API key:
        ```yaml
        GEMINI_API_KEY: "YOUR_GEMINI_API_KEY_HERE"
        # GROQ_API_KEY: "YOUR_GROQ_API_KEY_HERE" # If using Groq for legacy agent
        ```
    *   Alternatively, ensure the `GEMINI_API_KEY` environment variable is set in your system.

### 3. Frontend Setup

*   **Navigate to the Frontend Directory:**
    ```bash
    cd frontend
    ```

*   **Install Node.js Dependencies:**
    ```bash
    npm install
    # OR if you use yarn:
    # yarn install
    ```

## Usage / Running the Application

1.  **Start the Flask Backend Server:**
    *   Open a terminal in the project root directory.
    *   Ensure your Python virtual environment is activated.
    *   Run the Flask application:
        ```bash
        python src/app.py
        ```
    *   Alternatively, from within the `src` directory:
        ```bash
        flask run --port 5001
        ```
    *   The backend API will typically be running on `http://localhost:5001`.

2.  **Start the React Frontend Development Server:**
    *   Open another terminal.
    *   Navigate to the `frontend` directory.
    *   Run the React development server:
        ```bash
        npm start
        # OR if you use yarn:
        # yarn start
        ```
    *   This will usually open the application in your default web browser.

3.  **Access the UI:**
    *   Open your web browser and navigate to `http://localhost:3000` (or the port indicated by the `npm start` command).
    *   Use the interface to upload PDF documents and view evaluation results.

## API Endpoints

The backend provides the following API endpoints (running on `http://localhost:5001` by default):

### 1. Upload Files

*   **Endpoint:** `POST /api/upload`
*   **Description:** Uploads question paper and answer sheet PDFs.
*   **Request:** `multipart/form-data`
    *   `question_paper`: The question paper PDF file.
    *   `answer_sheet`: The answer sheet PDF file.
*   **Example Response (Success - 200):**
    ```json
    {
        "message": "Files uploaded successfully. Ready for processing.",
        "question_paper_filename": "question_paper_secure.pdf",
        "answer_sheet_filename": "answer_sheet_secure.pdf"
    }
    ```
*   **Example Response (Error - 400):**
    ```json
    {
        "error": "Missing question_paper or answer_sheet in the request"
    }
    ```

### 2. Process Documents (PDF to Text)

*   **Endpoint:** `POST /api/process_documents`
*   **Description:** Converts the uploaded PDFs to images and then extracts text from these images using Gemini.
*   **Request Body (JSON):**
    ```json
    {
        "question_paper_filename": "question_paper_secure.pdf",
        "answer_sheet_filename": "answer_sheet_secure.pdf"
    }
    ```
*   **Example Response (Success - 200):**
    ```json
    {
        "message": "Documents processed successfully",
        "question_paper_images_path": "Evaluation_bot/question_paper_secure",
        "answer_sheet_images_path": "Evaluation_bot/answer_sheet_secure",
        "question_paper_json_path": "Evaluation_bot/question_paper_secure.json",
        "answer_sheet_json_path": "Evaluation_bot/answer_sheet_secure.json"
    }
    ```
*   **Example Response (Error - 404):**
    ```json
    {
        "error": "One or both uploaded files not found on server. Upload again."
    }
    ```

### 3. Perform Evaluation

*   **Endpoint:** `POST /api/evaluate`
*   **Description:** Takes the paths of the processed JSON files (containing extracted text), orchestrates the AI evaluation pipeline (Q&A alignment, AI assessment, post-processing).
*   **Request Body (JSON):**
    ```json
    {
        "question_paper_json_path": "Evaluation_bot/question_paper_secure.json",
        "answer_sheet_json_path": "Evaluation_bot/answer_sheet_secure.json"
    }
    ```
*   **Example Response (Success - 200):**
    ```json
    {
        "message": "Evaluation pipeline completed successfully.",
        "final_report_path": "Evaluation_bot/question_paper_secure_evaluation_files/final_processed_evaluation_report_gemini.json",
        "intermediate_steps": {
            "combined_transcript": "Evaluation_bot/question_paper_secure_evaluation_files/transcript_question_paper_secure.json",
            "formatted_transcript": "Evaluation_bot/question_paper_secure_evaluation_files/formatted_transcript_question_paper_secure.json",
            "raw_evaluation_report": "Evaluation_bot/question_paper_secure_evaluation_files/evaluation_report_gemini.json"
        }
    }
    ```
*   **Example Response (Error - 400/404/500):**
    ```json
    {
        "error": "Specific error message here (e.g., Missing JSON file paths...)"
    }
    ```

### 4. Retrieve Evaluation Results

*   **Endpoint:** `GET /api/results/<job_id>`
*   **Description:** Retrieves the final evaluation report.
    *   **Note:** Currently, `job_id` is ignored, and the endpoint returns the *last successfully generated report* in the server session.
*   **Example Response (Success - 200):**
    ```json
    {
        "Question 1": {
            "evaluation": "correct",
            "score_breakdown": { /* ... */ },
            "total_score_calculated": 10.0,
            "strengths": "Clear understanding of the core concepts.",
            "weaknesses": "Minor grammatical errors.",
            "spelling_errors": 2,
            "constructive_feedback": "Proofread for grammar. Overall good answer."
        }
        // ... more questions
    }
    ```
*   **Example Response (Error - 404, No report available):**
    ```json
    {
        "message": "No evaluation results available yet. Please run an evaluation first."
    }
    ```

## Project Structure

```
├── configs/                  # Configuration files (e.g., config.yaml for API keys)
├── data/                     # Sample PDF data (e.g., Answer_sheet.pdf, question_paper.pdf)
├── examples/                 # Standalone example/demo scripts
│   ├── extraction_from_pdf.py
│   └── gemini_demo.py
├── frontend/                 # React User Interface
│   ├── public/
│   └── src/
├── requirements.txt          # Python backend dependencies
├── readme.md                 # This file
├── src/                      # Backend Python source code
│   ├── app.py                # Flask application (API endpoints, main orchestration)
│   ├── pdf_to_imgs.py        # PDF to image conversion
│   ├── extract_from_images.py # Text extraction from images
│   ├── combine_ques_ans.py   # Aligning questions and answers
│   ├── format_transcript.py  # Formatting combined transcript
│   ├── Evaluation_bot.py     # Core AI evaluation logic
│   ├── post_proc.py          # Post-processing of evaluation reports
│   ├── prompts.py            # Prompts (primarily for legacy agent)
│   ├── legacy_agent/         # Older agent-based framework (not part of main API)
│   │   ├── agent.py
│   │   └── ollama_models.py
│   └── utils/                # Utility scripts (e.g., get_keys.py)
├── Evaluation_bot/           # Default output directory for generated files (images, JSONs, reports)
└── uploads/                  # Default directory for uploaded PDF files by the API
```

## Contributing

Contributions are welcome! Feel free to open issues, submit pull requests, or suggest improvements. Please follow standard coding practices and ensure changes are well-tested.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details (if one exists, otherwise assume MIT).

## Acknowledgements

*   Google Gemini API ([https://ai.google.dev/gemini-api](https://ai.google.dev/gemini-api))
*   PyMuPDF (Fitz)
*   Flask
*   React

## Disclaimer

This project is for educational and experimental purposes. Use it responsibly and ethically. Evaluation results are AI-generated and may require human oversight for critical assessments.
```
