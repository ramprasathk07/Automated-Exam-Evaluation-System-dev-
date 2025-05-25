import os
import sys
from pathlib import Path
import json

# from utils.get_keys import load_config
# import google.generativeai as genai

# current_dir = Path(__file__).parent.resolve()
# parent_dir = current_dir.parent
# sys.path.append(str(parent_dir))
# load_config('configs/config.yaml')

# genai.configure(api_key=os.environ["GEMINI_API_KEY"]) # This will be handled in app.py


def extract_text_from_images(gemini_model_instance, genai_module, path, typ=None):
    """
    Extracts text from images in a given path using the provided Gemini model instance.

    Args:
        gemini_model_instance: The pre-configured Gemini GenerativeModel instance.
        genai_module: The google.generativeai module (for functions like upload_file).
        path: Directory containing .png images.
        typ: Type of document ('ans' for answer sheet, 'ques' for question paper).
    """
    data_to_save = {}
    for i in os.listdir(path):
        if i.endswith(".png"):
            image_path = os.path.join(path, i)
            # Use the genai_module for utility functions like upload_file
            uploaded_file = genai_module.upload_file(image_path)
            print(
                f"Uploaded file for text extraction: {uploaded_file.name} from {image_path}"
            )

            # Use the passed-in gemini_model_instance for content generation
            # No need to create a new model = genai.GenerativeModel("gemini-1.5-flash")

            prompt_text = ""
            if typ == "ans":
                prompt_text = f"""This is an Answer paper. Extract all readable text precisely, including any drawings, code snippets,and 
                        mathematical expressions as they are. If there are any drawings or illustrations, explain them in 2-3 lines 
                        with respect to the answer text associated with them. Ensure that programming languages and 
                        mathematical content are extracted verbatim and not altered."""
            else:  # 'ques'
                prompt_text = f"""This is a question paper. 
                        Extract all questions from this paper with the question number and the total marks 
                        allocated at the end of each question. If there are any images or tables present, 
                        describe them in 2-3 lines, mentioning their relevance to the questions. 
                        Ensure that the extracted information is structured and clear."""

            # Generate content using the provided model instance
            result = gemini_model_instance.generate_content(
                [uploaded_file, "\n\n", prompt_text]  # Use the uploaded file object
            )

            # It's good practice to remove uploaded files if they are temporary and not needed later
            # genai_module.delete_file(uploaded_file.name) # Consider adding this if appropriate

            data_to_save[i] = result.text

    output_file_path = f"{path}.json"
    # The erroneous block below was removed.
    # Erroneous block start:
    #                 [
    #                     myfile,
    #                     "\n\n",
    #                     f"""This is an Answer paper. Extract all readable text precisely, including any drawings, code snippets,and
    #                     mathematical expressions as they are. If there are any drawings or illustrations, explain them in 2-3 lines
    #                     with respect to the answer text associated with them. Ensure that programming languages and
    #                     mathematical content are extracted verbatim and not altered."""
    #                 ]
    #             )
    # Erroneous block end.

    with open(output_file_path, "w") as json_file:
        json.dump(data_to_save, json_file, indent=4)

    print(f"{path} Extraction Done and saved as {output_file_path}")
    return output_file_path
