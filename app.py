import csv
from flask import Flask, render_template, request
import json
import random

app = Flask(__name__)

def load_questions():
    with open('questions.json') as f:
        return json.load(f)

def nl2br(value):
    """Convert newline characters to <br> tags."""
    return value.replace('\n', '<br>')

# Register the custom filter
app.jinja_env.filters['nl2br'] = nl2br

@app.route('/', methods=['GET'])
def quiz():
    questions = load_questions()
    subset_size = 5 if len(questions) >= 5 else len(questions)
    quiz_questions = random.sample(questions, subset_size)
    return render_template('quiz.html', questions=quiz_questions)

@app.route('/submit', methods=['POST'])
def submit():
    quiz_data = json.loads(request.form.get('quiz_data'))
    results = []
    doubts = []
    incorrect_answers = []
    score = 0
    
    for i, q in enumerate(quiz_data):
        qid = str(q["id"])
        user_answer = request.form.getlist("response_" + qid)
        answer_text = ", ".join(user_answer) if user_answer else "No Answer"
        correct_text = ", ".join(q["correct_answers"])
        
        is_correct = set(user_answer) == set(q["correct_answers"])
        if is_correct:
            score += 1
        else:
            incorrect_answers.append({
                "number": i + 1,
                "id": qid,
                "question": q["question"],
                "user_answer": answer_text,
                "correct_answer": correct_text
            })
        
        result = {
            "number": i + 1,
            "id": qid,
            "question": q["question"],
            "user_answer": answer_text,
            "correct_answer": correct_text
        }
        results.append(result)
        
        if request.form.get("doubt_" + qid) is not None:
            doubts.append(result)
    
    total_questions = len(quiz_data)
    return render_template('results.html', score=score, total_questions=total_questions, incorrect_answers=incorrect_answers, doubts=doubts)

@app.route('/save_results', methods=['POST'])
def save_results():
    incorrect_answers_string = request.form.get('incorrect_answers')
    json_acceptable_string = incorrect_answers_string.replace("'", "\"")
    print(f'incorrect_answers {json_acceptable_string}')
    incorrect_answers = json.loads(json_acceptable_string)
    
    
    if incorrect_answers:
        with open('my_errors.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for answer in incorrect_answers:
                writer.writerow([answer['number'],answer['id'],answer['user_answer'],answer['correct_answer'],answer['question']])
    return 'Results saved successfully!'

if __name__ == '__main__':
    app.run(debug=True)
