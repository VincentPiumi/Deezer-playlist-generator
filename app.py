from flask import Flask, render_template, request
from flask_frozen import Freezer

app = Flask(__name__)
freezer = Freezer(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validate', methods=['POST'])
def validate_input():
    user_input = request.form['user_input']
    # Add validation logic here
    if user_input.isnumeric():
        return f"{user_input} is a number!"
    else:
        return f"{user_input} is not a number."

if __name__ == '__main__':
    freezer.freeze()
