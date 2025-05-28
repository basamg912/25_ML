from flask import Flask, render_template, request, redirect, url_for
import os
from dummy_model import classify_clothes

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

clothes_list = [
    {"filename" : "top1.jpg", "category" : "상의"},
    {"filename" : "pants1.jpg", "category" : "하의"},
]

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            category = classify_clothes(filepath)
            # 더미 코디 추천
            outfit = {"top": "티셔츠.jpg", "bottom": "청바지.jpg"}
            return render_template('index.html', filename=file.filename, category=category, outfit=outfit)
    return render_template('index.html')

@app.route('/closet')
def closet():
    return render_template('closet.html', clothes=clothes_list)

@app.route('/top')
def top():
    return render_template('cloth/top.html')
if __name__ == "__main__":
    app.run(debug=True)
