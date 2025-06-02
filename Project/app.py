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
            if raw_category =='unknown':
                return render_template('index.html', show_retry=True)    
            page = PAGE_MAP.get(raw_category)
            if page in category_items:
                category_items[page].append({"filename":f.filename,"raw":raw_category})
                #outfit 추천해주는 모델로 상하의 추천해주기
                outfit = {
                    "top" : "recommend Top . jpg",
                    "bottom" : "reccomend Bottomg . jpg",
                    "shoe" : "recommend shoe"
                }
                return render_template('index.html',redirect_to=page, outfit = outfit)
            else:
                return redirect(url_for('index'))
                
        
        # 수동 수정 처리
        if 'category_override' in request.form:
            filename = request.form['filename']
            old_page = request.form['old_page']
            new_page = request.form['category_override']
            raw = request.form['raw']

            # 기존 카테고리에서 제거
            category_items[old_page] = [
                it for it in category_items[old_page]
                if it['filename'] != filename
            ]
            # 새 카테고리에 추가
            raw = request.form.get('raw', filename.split('.')[0])  # 대체 로직
            category_items[new_page].append({'filename': filename, 'raw': raw})

            # 수정 완료 팝업 & 새 페이지로 이동
            return redirect(url_for(new_page, corrected='1'))

    return render_template('index.html')

@app.route('/closet', methods=['GET','POST'])
def closet():
    return render_template('closet.html', clothes=category_items)

@app.route('/recommend')
def recommend():
    top = [it['filename'] for it in category_items['top']]
    bottom = [it['filename'] for it in category_items['bottom']]
    shoe = [it['filename'] for it in category_items['shoe']]
    outer = [it['filename'] for it in category_items['outer']]
    # 여기서 코디 추천 프로그램으로 top_img, bottom_img, shoe_img 계산해서 넘겨주면 된다.
    print(top)
    if not top or not bottom:
        return render_template('recommend.html', top = None, bottom= None, shoe=None, outer=None)
    top_img = top[0]
    bottom_img = bottom[0]
    if shoe:
        shoe_img = shoe[0]    
        if outer:
            outer_img = outer[0] # 만약 날씨가 춥다면 outer 까지 출력
            return render_template('recommend.html', top=top_img, bottom= bottom_img, shoe=shoe_img, outer = outer_img)
        else:
            return render_template('recommend.html', top=top_img, bottom= bottom_img, shoe=shoe_img)
    else:
        return render_template('recommend.html', top=top_img, bottom= bottom_img, shoe=None, outer = None)
@app.route('/top', methods=['GET','POST'])
def top():
    if request.method == "POST" and 'delete_filename' in request.form:
        filename = request.form['delete_filename']
        category = request.form['delete_category'].strip()
        category_items[category] = [
            it for it in category_items[category] 
            if it['filename'] != filename
            ]
        print(category)
        return redirect(url_for(('top')))
    return render_template('cloth/top.html',items=category_items['top'])
@app.route('/bottom', methods=['GET','POST'])
def bottom():
    if request.method == "POST" and 'delete_filename' in request.form:
        filename = request.form['delete_filename']
        category = request.form['delete_category'].strip()
        category_items[category] = [
            it for it in category_items[category] 
            if it['filename'] != filename
            ]
        print(category)
        return redirect(url_for(('bottom')))
    return render_template('cloth/bottom.html',items=category_items['bottom'])
@app.route('/outer', methods=['GET','POST'])
def outer():
    if request.method == "POST" and 'delete_filename' in request.form:
        filename = request.form['delete_filename']
        category = request.form['delete_category'].strip()
        category_items[category] = [
            it for it in category_items[category] 
            if it['filename'] != filename
            ]
        print(category)
        return redirect(url_for(('outer')))
    return render_template('cloth/outer.html',items=category_items['outer'])
@app.route('/shoe', methods=['GET','POST'])
def shoe():
    if request.method == "POST" and 'delete_filename' in request.form:
        filename = request.form['delete_filename']
        category = request.form['delete_category'].strip()
        category_items[category] = [
            it for it in category_items[category] 
            if it['filename'] != filename
            ]
        print(category)
        return redirect(url_for(('shoe')))
    return render_template('cloth/shoe.html',items=category_items['shoe'])
if __name__ == "__main__":
    app.run(debug=True)

