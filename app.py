from flask import Flask, render_template, request
import json
import random

app = Flask(__name__)

def load_questions():
    with open('questions.json') as f:
        return json.load(f)

@app.route('/', methods=['GET'])
def quiz():
    # Load questions and select a random subset
    questions = load_questions()
    subset_size = 5 if len(questions) >= 5 else len(questions)
    quiz_questions = random.sample(questions, subset_size)
    return render_template('quiz.html', questions=quiz_questions)

@app.route('/submit', methods=['POST'])
def submit():
    responses = {}
    doubts = {}
    
    # Process responses for each form field.
    # For single-choice responses the field is named "response_<question_id>"
    # For multiple-choice, the field name is "response_<question_id>[]"
    for key in request.form:
        if key.startswith('response_'):
            # Extract the question id by stripping the prefix
            qid = key.split('response_')[1]
            # getlist() works for both single (as a list with one item) and multiple selections
            responses[qid] = request.form.getlist(key)
        elif key.startswith('doubt_'):
            qid = key.split('doubt_')[1]
            doubts[qid] = True

    # Render a simple results page with the collected responses.
    return render_template('results.html', responses=responses, doubts=doubts)

if __name__ == '__main__':
    app.run(debug=True)
