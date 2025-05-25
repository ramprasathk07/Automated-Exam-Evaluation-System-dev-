import re
import json 

def parse_answer(path):
    with open(path,'r') as f:
        text = json.load(f)

    questions = {}
    lines = text.strip().split('\n')
    current_question = None

    for line in lines:
        if line.startswith("**Question"):
            parts = line.split(' ')
            question_number = parts[1]  
            match = re.search(r'Total Marks: (\d+)', line)
            marks = int(match.group(1)) if match else 0 

            current_question = f"Question {question_number}"
            questions[current_question] = {
                "Total Marks": marks,
                "Question": None,
                "Student Answer": []
            }

        elif line.startswith("- **Question**:"):
            question_text = line.split("**Question**: ", 1)[1]
            questions[current_question]["Question"] = question_text

        elif line.startswith("- **Student Answer**:"):
            continue

        elif current_question and line.strip():
            questions[current_question]["Student Answer"].append(line.strip())

    outpath = "Evaluation_bot/formatted_transcript.json"
    with open(outpath,'w') as f:
        json.dump(questions,f)
        
    return outpath
