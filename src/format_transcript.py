import re
import json
import os


def parse_answer(transcript_json_path, output_dir="Evaluation_bot"):
    # The input 'transcript_json_path' should point to a JSON file
    # where the content to be parsed is under a key, e.g., "transcript_text" or "transcript_content"
    # This is based on the refactoring of combine_Q_and_A which might save plain text or JSON string.

    try:
        with open(transcript_json_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {transcript_json_path}: {e}")
        raise ValueError(f"Invalid JSON file: {transcript_json_path}") from e
    except FileNotFoundError:
        raise

    # Determine where the actual text to parse is located within the JSON
    # Based on combine_Q_and_A, it could be 'transcript_text' or the root object if it was valid JSON.
    text_to_parse = ""
    if isinstance(
        data, str
    ):  # If the loaded JSON is just a string (unlikely with json.load but good to check)
        text_to_parse = data
    elif (
        "transcript_text" in data
    ):  # If combine_Q_and_A saved it as {"transcript_text": "..."}
        text_to_parse = data["transcript_text"]
    elif (
        "transcript_content" in data
    ):  # If combine_Q_and_A saved it as {"transcript_content": "..."}
        text_to_parse = data["transcript_content"]
    elif isinstance(data, dict) and all(isinstance(k, str) for k in data.keys()):
        # This case is for when the response from Gemini was already a valid JSON string
        # and combine_Q_and_A successfully parsed and saved it.
        # The current parsing logic below assumes `text` is a single block of string.
        # If `data` itself is the structured Q&A, this parsing logic needs to change
        # or the data needs to be re-serialized to a string format this parser expects.
        # For now, if it's a dict, we'll assume it doesn't need this specific line-by-line parsing.
        # This part needs clarification based on actual output of combine_Q_and_A's Gemini call.
        # Let's assume for now combine_Q_and_A will always produce a JSON which contains a string that needs parsing.
        # If `data` is already the structured dict, we should return it directly or save it.
        # Given the original parser, it expects a flat string.
        # This is a tricky part: the original `parse_answer` expects a multi-line string.
        # The `combine_Q_and_A` response from Gemini is directly saved.
        # If Gemini's response *is* the multi-line string, then `text_to_parse = data` (if data is string)
        # or `text_to_parse = json.dumps(data)` (if data is dict and needs to be stringified for parsing)
        # Let's assume the 'response' from 'combine_Q_and_A' (which is 'text' here) is the actual string to parse.
        # The previous step in `combine_Q_and_A` saves the Gemini response. If that response is a JSON string,
        # it's parsed then re-dumped. If it's text, it's saved as `{"transcript_text": response}`.
        # So, `text` here will either be the parsed JSON (if Gemini returned JSON string) or `{"transcript_text": ...}`.
        if (
            isinstance(data, dict) and "Question 1" in data
        ):  # Heuristic: if it looks like already parsed data
            print(
                "Data seems to be already structured. Skipping line-by-line parsing in format_transcript."
            )
            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            base_name = os.path.splitext(os.path.basename(transcript_json_path))[0]
            output_filename = f"formatted_{base_name}.json"
            output_file_path = os.path.join(output_dir, output_filename)
            with open(output_file_path, "w") as f:
                json.dump(data, f, indent=4)
            return output_file_path
        else:  # Default to trying 'transcript_text' or fail
            text_to_parse = data.get("transcript_text", "")
            if not text_to_parse and isinstance(
                data, dict
            ):  # If it was a JSON dict but not the text field
                # This indicates a mismatch in expected structure from combine_Q_and_A output
                print(
                    f"Warning: No 'transcript_text' field in {transcript_json_path}, and data is not directly parsable as multi-line text by this function."
                )
                # Fallback: try to dump the whole thing as a string to parse. This is a guess.
                text_to_parse = json.dumps(data, indent=4)

    questions = {}
    lines = text_to_parse.strip().split("\n")
    current_question = None
    # Ensure questions is initialized, even if text_to_parse is empty
    questions = {}

    for line in lines:
        line = line.strip()  # Ensure leading/trailing whitespace is removed
        if line.startswith("**Question"):
            parts = line.split(" ")
            question_number = parts[1] if len(parts) > 1 else "Unknown"
            match = re.search(r"Total Marks: (\d+)", line)  # Original regex
            if not match:  # Try alternative regex if original fails
                match = re.search(r"\(Total Marks: (\d+)\)", line)

            marks = int(match.group(1)) if match else 0

            current_question_key = f"Question {question_number}"
            questions[current_question_key] = {
                "Total Marks": marks,
                "Question": None,  # Initialize as None
                "Student Answer": [],  # Initialize as empty list
            }

        elif (
            line.startswith("- **Question**:") and current_question_key
        ):  # Ensure current_question_key is set
            question_text = line.split("- **Question**:", 1)[1].strip()
            if (
                questions[current_question_key]["Question"] is None
            ):  # Only set if not already set
                questions[current_question_key]["Question"] = question_text
            else:  # Append if already set (e.g. multi-line question)
                questions[current_question_key]["Question"] += "\n" + question_text

        elif (
            line.startswith("- **Student Answer**:") and current_question_key
        ):  # Ensure current_question_key is set
            # This line itself is a header, the actual answer follows.
            # If the answer is on the same line, extract it:
            answer_part = line.split("- **Student Answer**:", 1)[1].strip()
            if answer_part:
                questions[current_question_key]["Student Answer"].append(answer_part)

        elif (
            current_question_key and line
        ):  # If it's a continuation of an answer or multi-line question part
            # This is the tricky part: is it part of Question or Answer?
            # Assuming if "Question" is not None, subsequent lines are part of "Student Answer"
            # until a new "**Question" marker.
            if questions[current_question_key]["Question"] is not None:
                questions[current_question_key]["Student Answer"].append(line)
            # else: # Or, if question text itself is multi-line and doesn't have the prefix
            #    if questions[current_question_key]["Question"] is None:
            #        questions[current_question_key]["Question"] = line # First line of question
            #    else:
            #        questions[current_question_key]["Question"] += "\n" + line

    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_transcript_name = os.path.splitext(os.path.basename(transcript_json_path))[0]
    output_filename = f"formatted_{base_transcript_name}.json"
    output_file_path = os.path.join(output_dir, output_filename)

    with open(output_file_path, "w") as f:
        json.dump(questions, f, indent=4)

    print(f"Formatted transcript saved in {output_file_path}")
    return output_file_path
