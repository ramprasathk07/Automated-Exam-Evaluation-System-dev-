import json
# current_dir = Path(__file__).parent.resolve()
# parent_dir = current_dir.parent
# sys.path.append(str(parent_dir))

# load_config('configs/config.yaml')
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def combine_Q_and_A(genai,question_json,answer_json):

    model = genai.GenerativeModel("gemini-1.5-flash")
    def get_json(path):
        with open(path, "r") as file:
            input_data = json.load(file)
        return input_data

    question_paper = get_json(question_json)
    answer_sheet = get_json(answer_json)

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

    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(prompt).text

    output_file_path = "Evaluation_bot/ques_and_ans_transcript.json"
    with open(output_file_path, "w") as json_file:
        json.dump(response, json_file, indent=4)

    print(f"Results saved in {output_file_path}")
    return output_file_path
