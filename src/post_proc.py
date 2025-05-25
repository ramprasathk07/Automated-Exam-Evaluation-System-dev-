# import json

# def format_evaluation_reports(raw_data):
#     formatted = {}
#     for question_key, data in raw_data.items():
#         report = data['evaluation_report']
        
#         # Extract key information
#         lines = report.split('\n')
#         question = 'N/A'
#         answer = 'N/A'
#         evaluation = 'N/A'
#         total_score = 'N/A'
#         strengths = []
#         weaknesses = []
#         current_section = None

#         for line in lines:
#             line = line.strip()
#             if line.startswith('**Question:'):
#                 question = line.split('**Question:')[1].strip()
#             elif line.startswith('**Student Answer:'):
#                 answer = line.split('**Student Answer:')[1].strip()
#             elif line.startswith('**1. Evaluation:'):
#                 evaluation = line.split('**1. Evaluation:')[1].strip()
#             elif 'Total' in line and ':' in line:
#                 total_score = line.split(':')[1].strip()
#             elif '**3. Strengths:**' in line:
#                 current_section = strengths
#             elif '**4. Weaknesses:**' in line:
#                 current_section = weaknesses
#             elif current_section is not None and line.startswith('*'):
#                 current_section.append(line)

#         # Format the data
#         formatted[question_key] = {
#             'Question': question,
#             'Student Answer': answer,
#             'Evaluation': evaluation,
#             'Total Score': total_score,
#             'Strengths': strengths,
#             'Weaknesses': weaknesses
#         }
    
#     return formatted

# # Load the JSON data
# with open('evaluation_reports_gemini.json', 'r') as f:
#     raw_data = json.load(f)

# # Format the data
# formatted_data = format_evaluation_reports(raw_data)

# # Print the formatted data
# print(json.dumps(formatted_data, indent=4))

# # Save the formatted data to a new JSON file
# with open('evaluation_reports_gemini_formatted.json', 'w') as f:
#     json.dump(formatted_data, f, indent=4)


import json
import re

def format_evaluation_reports(raw_data):
    formatted = {}
    for question_key, data in raw_data.items():
        report = data['evaluation_report']

        lines = report.split('\n')
        question = 'N/A'
        answer = 'N/A'
        evaluation = 'N/A'
        total_score = 'N/A'
        strengths = []
        weaknesses = []
        current_section = None

        question_match = re.search(r'\*\*Question:?\*\*(.*?)(?=\*\*|\n\n)', report, re.DOTALL)
        answer_match = re.search(r'\*\*Student Answer:?\*\*(.*?)(?=\*\*|\n\n)', report, re.DOTALL)

        if question_match:
            question = question_match.group(1).strip()
        if answer_match:
            answer = answer_match.group(1).strip()

        for line in lines:
            line = line.strip()
            if line.startswith('**1. Evaluation:'):
                evaluation = line.split('**1. Evaluation:')[1].strip()
            elif 'Total' in line and ':' in line:
                total_score = line.split(':')[1].strip()
            elif '**3. Strengths:**' in line:
                current_section = strengths
            elif '**4. Weaknesses:**' in line:
                current_section = weaknesses
            elif current_section is not None and line.startswith('*'):
                current_section.append(line)

        formatted[question_key] = {
            'Question': question,
            'Student Answer': answer,
            'Evaluation': evaluation,
            'Total Score': total_score,
            'Strengths': strengths,
            'Weaknesses': weaknesses
        }
    
    return formatted

def post_processing(path):
    print(f"\nPost Processing:{path}\n")
    with open("Evaluation_bot\evaluation_reports_gemini.json", 'r') as f:
        raw_data = json.load(f)

    formatted_data = format_evaluation_reports(raw_data)
    print(json.dumps(formatted_data, indent=4))

    for key, value in formatted_data.items():
        if value['Question'] == 'N/A' or value['Student Answer'] == 'N/A':
            print(f"Warning: Missing question or answer for {key}")
       
    outfile = 'Evaluation_bot/evaluation_reports_gemini_formatted.json'
    with open(outfile, 'w') as f:
        json.dump(formatted_data, f, indent=4)

    return outfile