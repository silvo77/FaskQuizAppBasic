from flask import Flask, render_template, request
import json
import random

app = Flask(__name__)

def load_questions():
    with open('questions.json') as f:
        return json.load(f)

@app.route('/', methods=['GET'])
def quiz():
    # Load all questions and pick a random subset.
    questions = load_questions()
    subset_size = 5 if len(questions) >= 5 else len(questions)
    quiz_questions = random.sample(questions, subset_size)
    return render_template('quiz.html', questions=quiz_questions)

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve the quiz data (the subset of questions used) from a hidden field.
    quiz_data = json.loads(request.form.get('quiz_data'))
    results = []
    doubts = []
    
    # Process each question from the quiz data.
    for i, q in enumerate(quiz_data):
        qid = str(q["id"])
        # Retrieve the user answer; getlist() works for both radio buttons and checkboxes.
        user_answer = request.form.getlist("response_" + qid)
        answer_text = ", ".join(user_answer) if user_answer else "No Answer"
        correct_text = ", ".join(q["correct_answers"])
        
        # Build a result dictionary with all needed fields.
        result = {
            "number": i + 1,
            "id": qid,
            "question": q["question"],
            "user_answer": answer_text,
            "correct_answer": correct_text
        }
        results.append(result)
        
        # Check if the doubt checkbox was marked for this question.
        if request.form.get("doubt_" + qid) is not None:
            doubts.append(result)
    
    # Pass both full results and the subset with doubts to the results template.
    return render_template('results.html', results=results, doubts=doubts)

if __name__ == '__main__':
    app.run(debug=True)
