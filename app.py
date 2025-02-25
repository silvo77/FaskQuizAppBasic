import csv
from flask import Flask, render_template, request,redirect,url_for
import json
import random
import ast
import os

app = Flask(__name__)

def load_questions(jsonfile):
    with open(jsonfile, encoding="utf8") as f:
        return json.load(f)

def nl2br(value):
    """Convert newline characters to <br> tags."""
    return value.replace('\n', '<br>')

# Register the custom filter
app.jinja_env.filters['nl2br'] = nl2br

@app.route('/', methods=['GET', 'POST'])
def configure_quiz():
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    if request.method == 'POST':
        jsonfile = request.form.get('json_file')
        max_questions = int(request.form.get('max_questions'))
        selection_type = request.form.get('selection_type')
        search_text = request.form.get('search_text', '').lower()
        return redirect(url_for('quiz', jsonfile=jsonfile, max_questions=max_questions, selection_type=selection_type, search_text=search_text))
    return render_template('index.html', json_files=json_files)


@app.route('/quiz', methods=['GET'])
def quiz():
    jsonfile = request.args.get('jsonfile', 'questions.json')
    questions = load_questions(jsonfile)
    max_questions = int(request.args.get('max_questions', 5))
    selection_type = request.args.get('selection_type', 'random')
    search_text = request.args.get('search_text', '').lower()

    if selection_type == 'text' and search_text:
        filtered_questions = [q for q in questions if search_text in q['question'].lower() or any(search_text in ans.lower() for ans in q['options'].values())]
    elif selection_type == 'list' and search_text:
        ids_list = search_text.split(',')
        ids_list = [id.strip() for id in ids_list]
        filtered_questions = [q for q in questions if str(q['id']) in ids_list]
    else:
        filtered_questions = questions

    subset_size = min(max_questions, len(filtered_questions))
    quiz_questions = random.sample(filtered_questions, subset_size) if subset_size > 0 else []

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
        explanation = q.get("explanation")
        
        is_correct = set(user_answer) == set(q["correct_answers"])
        if is_correct:
            score += 1
        else:
            incorrect_answers.append({
                "number": i + 1,
                "id": qid,
                "question": q["question"],
                "user_answer": answer_text,
                "correct_answer": correct_text,
                "explanation": explanation
            })
        
        result = {
            "number": i + 1,
            "id": qid,
            "question": q["question"],
            "user_answer": answer_text,
            "correct_answer": correct_text,
            "explanation": explanation
        }
        results.append(result)
        
        if request.form.get("doubt_" + qid) is not None:
            doubts.append(result)
    
    total_questions = len(quiz_data)
    return render_template('results.html', score=score, total_questions=total_questions, incorrect_answers=incorrect_answers, doubts=doubts)

@app.route('/save_results', methods=['POST'])
def save_results():
    incorrect_answers_string = request.form.get('incorrect_answers')
    incorrect_answers_list = ast.literal_eval(incorrect_answers_string)
    
    
    if len(incorrect_answers_list)>0:
        with open('my_errors.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            for answer in incorrect_answers_list:
                writer.writerow([answer['id'],answer['user_answer'],answer['correct_answer'],answer['question']])
    return 'Results saved successfully!'

if __name__ == '__main__':
    app.run(debug=True)
