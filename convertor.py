import json
import re
import logging

def save_to_file(filename, text):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        logging.info(f"File saved: {filename}")
    except Exception as e:
        logging.error(f"Failed to save file {filename}: {e}")


def convert_to_json_format(input_file, qb_id, created_by):
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    questions = re.split(r'\n---\n', content)
    logging.info(f"Total questions split: {len(questions)}")
    json_questions = []

    for i, question in enumerate(questions, 1):
        logging.info(f"Processing question {i}")
        
        try:
            # Extract question text and code block, removing the trailing asterisks
            question_match = re.search(r'Q\d+\.\s*(.*?)(?:\*\*)?(?=\n```|\n1\)|\Z)', question, re.DOTALL)
            if not question_match:
                logging.warning(f"Question {i}: No match for question text")
                continue
            question_text = question_match.group(1).strip()

            # Extract code snippet
            code_match = re.search(r'```(?:java|javascript|html|typescript|cpp|csharp|js|css|sql|yaml|bash)\n(.*?)```', question, re.DOTALL)
            code_block = code_match.group(1).strip() if code_match else ""

            # Combine question text and code block
            question_data = f"<p>{question_text}</p>"
            if code_block:
                question_data += f"$$$examly{code_block}"

            # Extract options (ensure exactly four)
            options = re.findall(r'\d+\)\s*(.*?)(?=\n\d+\)|\nCorrect answer:|\Z)', question, re.DOTALL)
            options = [opt.strip() for opt in options if opt.strip()]

            # If more than 4 options, remove the first one
            if len(options) > 4:
                logging.warning(f"Question {i}: More than 4 options found. Removing the first option.")
                options.pop(0)  # Remove the first option

            # Ensure exactly 4 options remain
            if len(options) != 4:
                logging.warning(f"Question {i}: Incorrect number of options ({len(options)}). Skipping question.")
                continue  # Skip this question if there are not exactly 4 options

            # Extract correct answer
            correct_answer_match = re.search(r'Correct answer:\s*(\d+)', question)
            if not correct_answer_match:
                logging.warning(f"Question {i}: No correct answer found")
                continue
            correct_answer_index = int(correct_answer_match.group(1)) - 1

            # Ensure correct answer index is within range
            if correct_answer_index < 0 or correct_answer_index >= len(options):
                logging.warning(f"Question {i}: Correct answer index out of range. Index: {correct_answer_index}, Options: {len(options)}")
                continue

            difficulty = re.search(r'Difficulty:\s*(\w+)', question)
            difficulty = difficulty.group(1) if difficulty else "Easy"

            tags_match = re.search(r'Tags:\s*(.*)', question)
            tags = [tag.strip() for tag in tags_match.group(1).split(',')] if tags_match else []

            json_question = {
                "question_type": "mcq_single_correct",
                "question_data": question_data,
                "options": [{"text": opt, "media": ""} for opt in options],
                "answer": {
                    "args": [options[correct_answer_index]],
                    "partial": []
                },
                "subject_id": None,
                "topic_id": None,
                "sub_topic_id": None,
                "blooms_taxonomy": None,
                "course_outcome": None,
                "program_outcome": None,
                "hint": [],
                "answer_explanation": {
                    "args": []
                },
                "manual_difficulty": difficulty,
                "question_editor_type": 3 if code_block else 1,
                "linked_concepts": "",
                "tags": tags,
                "question_media": [],
                "createdBy": created_by
            }
            if qb_id:
                json_question["qb_id"] = qb_id
            json_questions.append(json_question)
            logging.info(f"Successfully processed question {i}")
        except Exception as e:
            logging.error(f"Error processing question {i}: {str(e)}")
            logging.debug(f"Question content: {question}")
            continue

    logging.info(f"\nTotal questions successfully processed: {len(json_questions)}")
    return json_questions

def save_unique_mcqs(mcqs, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(mcqs, f, ensure_ascii=False, indent=2)
