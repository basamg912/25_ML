from flask import Flask, render_template, request, redirect, url_for
import os
import re
from dummy_model import classify_clothes

from ultralytics import YOLO
app = Flask(__name__)

PAGE_MAP = {
    '1/2 pants':    'bottom',
    'pants':        'bottom',
    'skirt':        'bottom',
    '1/2 shirts':   'top',
    'shirts':       'top',
    'hoodie':       'top',
    'outer':        'outer',
    'dres shoes':   'shoe',
    'shoes':        'shoe',
    'slipper':      'shoe',
    'women shoes':  'shoe'
}

cls_model = YOLO("/Users/basamg/KW_2025/ML/fine_tune_yolo.pt")
    

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

clothes_list = [
    {"filename" : "top1.jpg", "category" : "상의"},
    {"filename" : "pants1.jpg", "category" : "하의"},
]

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 페이지별 저장된 파일 리스트
category_items = {'top': [], 'bottom': [], 'outer': [], 'shoe': []}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 업로드 처리
        if 'file' in request.files and request.files['file'].filename:
            f = request.files['file']
            fp = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
            f.save(fp)
            raw_category = classify_clothes(fp, cls_model)
            page = PAGE_MAP.get(raw_category)
            if page in category_items:
                category_items[page].append(f.filename)
                return render_template('index.html',redirect_to=page)
            else:
                return redirect(url_for('index'))
        
        # 수동 수정 처리
        if 'category_override' in request.form:
            filename = request.form['filename']
            old_page = request.form['old_page']
            new_page = request.form['category_override']

            # 기존 카테고리에서 제거
            if old_page in category_items and filename in category_items[old_page]:
                category_items[old_page].remove(filename)
            # 새 카테고리에 추가
            if new_page in category_items:
                category_items[new_page].append(filename)

            # 수정 완료 팝업 & 새 페이지로 이동
            return redirect(url_for(new_page, corrected='1'))

    return render_template('index.html')

@app.route('/closet')
def closet():
    return render_template('closet.html', clothes=clothes_list)

@app.route('/top')
def top():
    return render_template('cloth/top.html',items=category_items['top'])
@app.route('/bottom')
def bottom():
    return render_template('cloth/bottom.html',items=category_items['bottom'])
@app.route('/outer')
def outer():
    return render_template('cloth/outer.html',items=category_items['outer'])
@app.route('/shoe')
def shoe():
    return render_template('cloth/shoe.html',items=category_items['shoe'])

if __name__ == "__main__":
    app.run(debug=True)

