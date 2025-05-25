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

# genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def extract_text_from_images(genai,path,typ=None):
    data_to_save = {}
    for i in os.listdir(path):
        if i.endswith('.png'):
            j = os.path.join(path,i)
            myfile = genai.upload_file(j)
            print(f"{myfile=}")

            model = genai.GenerativeModel("gemini-1.5-flash")

            if typ == 'ans':
                result = model.generate_content(
                    [
                        myfile, 
                        "\n\n", 
                        f"""This is an Answer paper. Extract all readable text precisely, including any drawings, code snippets,and 
                        mathematical expressions as they are. If there are any drawings or illustrations, explain them in 2-3 lines 
                        with respect to the answer text associated with them. Ensure that programming languages and 
                        mathematical content are extracted verbatim and not altered."""
                    ]
                )
            else:
                
                result = model.generate_content(
                    [
                        myfile, 
                        "\n\n", 
                        f"""This is a question paper. 
                        Extract all questions from this paper with the question number and the total marks 
                        allocated at the end of each question. If there are any images or tables present, 
                        describe them in 2-3 lines, mentioning their relevance to the questions. 
                        Ensure that the extracted information is structured and clear."""
                    ]
                )

            data_to_save[i] = result.text

    output_file_path = f"{path}.json"

    with open(output_file_path, "w") as json_file:
        json.dump(data_to_save, json_file, indent=4)

    print(f"{path} Extraction Done and saved as {output_file_path}")
    return output_file_path
