import json
import os

# current_dir = Path(__file__).parent.resolve() # Not needed for direct import
# parent_dir = current_dir.parent # Not needed for direct import
# sys.path.append(str(parent_dir)) # Not needed for direct import

# load_config('configs/config.yaml') # Handled by app.py or not needed
# genai.configure(api_key=os.environ["GEMINI_API_KEY"]) # genai object is passed in configured


def combine_q_and_a( # Renamed to snake_case
    gemini_model_instance,
    question_json_path,
    answer_json_path,
    output_dir="Evaluation_bot",
):
    """
    Combines questions and answers using the provided Gemini model instance.

    Args:
        gemini_model_instance: The pre-configured Gemini GenerativeModel instance.
        question_json_path: Path to the JSON file containing extracted questions.
        answer_json_path: Path to the JSON file containing extracted answers.
        output_dir: Directory to save the combined transcript.
    """
    # model = genai.GenerativeModel("gemini-1.5-flash") # Use passed-in instance

    def get_json(file_path):
        with open(file_path, "r") as file:
            input_data = json.load(file)
        return input_data

    question_paper = get_json(question_json_path)
    answer_sheet = get_json(answer_json_path)

    prompt = f"""
    You are an assistant evaluator. Your task is to evaluate a student's answer based on the following information:

    1. **Question Paper**: {json.dumps(question_paper, indent=4)}
    2. **Student Answer Sheet**: {json.dumps(answer_sheet, indent=4)}

    **Instructions**:
    - Align each question from the Question Paper with the corresponding answer from the Student Answer Sheet based on their identifiers (PART ID and Question ID).
    - Your output should follow this format:

        **Question {{Question ID}}** (Total Marks: {{Allocated Marks}}):
        - **Question**: {{Question Text}}
        - **Student Answer**: {{Student's Answer}}

    **Additional Notes**:
    - If a question does not have a corresponding answer, please indicate that clearly.
    - Ensure that the information is structured and easy to read.

    Please provide the aligned output based on the provided data.
    """

    # Use the passed-in gemini_model_instance
    chat_session = gemini_model_instance.start_chat(history=[])
    response = chat_session.send_message(prompt).text  # This response is a string

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create a more unique filename if possible, or use a fixed one for now
    # For example, based on input filenames (if they are unique enough)
    base_q_name = os.path.splitext(os.path.basename(question_json_path))[0]
    output_filename = f"transcript_{base_q_name}.json"
    output_file_path = os.path.join(output_dir, output_filename)

    # The response.text is already a string, which might be JSON-formatted text or just text.
    # If it's intended to be a JSON object that needs to be saved, it should be parsed first.
    # Assuming response.text is the actual content (string) to be saved, not a JSON object itself needing dump.
    # If response.text IS a JSON string that needs to be saved *as a JSON string field within another JSON*:
    # with open(output_file_path, "w") as json_file:
    #     json.dump({"transcript_content": response}, json_file, indent=4)
    # But the original code dumps `response` directly, which implies `response` (the string) is the JSON content.
    # Let's assume response.text is a string that *is* the JSON content.
    try:
        # Attempt to parse the response to ensure it's valid JSON, then re-serialize with indent
        parsed_response = json.loads(response)
        with open(output_file_path, "w") as json_file:
            json.dump(parsed_response, json_file, indent=4)
    except json.JSONDecodeError:
        # If it's not valid JSON, save it as plain text or handle error
        # For now, let's save it as a simple JSON with a text field if it's not JSON
        print(
            f"Warning: Response from Gemini in combine_q_and_a was not valid JSON. Saving as text in JSON."
        )
        with open(output_file_path, "w") as json_file:
            json.dump({"transcript_text": response}, json_file, indent=4)

    print(f"Combined Q&A transcript saved in {output_file_path}")
    return output_file_path
