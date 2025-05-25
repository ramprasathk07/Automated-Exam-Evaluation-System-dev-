# Automated Exam Evaluation System

This project provides an automated exam evaluation system powered by large language models (LLMs) and AI tools. It aims to streamline the assessment process by providing comprehensive feedback and accurate scoring for student answers.

## Features

- **Document Processing:**  Converts PDFs (question papers and answer sheets) to images for text extraction.
- **Image Text Extraction:** Uses Gemini AI API to extract text from images, preserving formatting and structure.
- **Question and Answer Alignment:** Processes the extracted text to align questions with answers.
- **AI Evaluation:**  Assesses student answers using a chosen LLM (Gemini or Groq) based on a grading rubric.
- **Feedback Generation:**  Generates detailed feedback, including strengths, weaknesses, spelling errors, and suggestions for improvement.
- **Tools:**  Provides a toolbox for further analysis:
    - Spelling checker
    - Score calculator
    - Plagiarism checker
- **Agent:**  The core logic, deciding which tool to use for evaluation.

## Installation

1. **Install Python:** Ensure you have Python 3.x installed.
2. **Create Virtual Environment:**  It's highly recommended to use a virtual environment for managing dependencies.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Activate the environment
    ```
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. **API Keys:**  Obtain API keys for Gemini and Groq from their respective platforms.
2. **Create a Config File:**  Create a `configs/config.yaml` file with the following structure:

   ```yaml
   GEMINI_API_KEY: your_gemini_api_key
   GROQ_API_KEY: your_groq_api_key
   ```

## Usage

1. **Prepare Documents:** Provide the question paper and answer sheet as PDFs.
2. **Run the Script:** Execute the `full_flow.py` script:
    ```bash
    python full_flow.py
    ```
3. **Review Results:**  The formatted evaluation report will be saved in `evaluation_reports_gemini_formatted.json`.

## Example

1. Place a PDF file named `Answer_sheet.pdf` and `question_paper.pdf` in the `data` directory.
2. Run the script: `python full_flow.py`
3. The script will process the PDFs, extract text, and generate a formatted evaluation report in the `evaluation_reports_gemini_formatted.json` file.

## Contributing

Contributions are welcome! Feel free to open issues, submit pull requests, or suggest improvements. 

## License

This project is licensed under the MIT License.

## Acknowledgements

- Gemini AI API ([https://ai.google.dev/gemini-api](https://ai.google.dev/gemini-api))
- Groq ([https://groq.com/](https://groq.com/))

## Disclaimer

This project is for educational and experimental purposes only. Use it responsibly and ethically. 
