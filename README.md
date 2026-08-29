# AI Outfit Recommendation System

**Clothing Detection & Outfit Compatibility Prediction**

YOLO와 Flask를 처음 활용하여 구현한 **의류 검출 및 코디 추천 웹 애플리케이션**이다. 사용자가 자신의 옷 이미지를 업로드하면 의류 아이템을 검출하고, 상의와 하의의 조합별 궁합을 예측하여 적합한 코디를 추천한다.

추천 모델을 학습하기 위해 **Musinsa**에서 의류 및 코디 데이터를 크롤링했으며, 이미지 특징 추출에는 **ResNet50**, 의류 검출에는 **YOLOv8**을 사용했다.

> 현재 버전에서는 날씨 기반 추천 기능은 구현되지 않았다.

## Pipeline

```text
User Clothing Images
        ↓
     Flask GUI
        ↓
    YOLOv8 Detection
        ↓
  Clothing Cropping
        ↓
  Feature Extraction
      (ResNet50)
        ↓
 Top / Bottom Embeddings
    2048 + 2048 dim
        ↓
    Concatenation
       4096 dim
        ↓
      MLP Classifier
        ↓
 Good Codi / Bad Codi
        ↓
  Outfit Recommendation
```

## Model Architecture

추천 모델은 **ResNet50 기반의 Siamese-style architecture**를 사용한다.

상의와 하의 이미지를 각각 동일한 ResNet50 feature extractor에 입력하여 2048차원 임베딩을 추출한다.

```text
Top Image
    │
    ▼
ResNet50
    │
    ▼
2048-d Embedding
    │
    ├──────────────┐
    │              │
    │        Concatenate
    │              │
Bottom Image       ▼
    │           4096-d
    ▼              │
ResNet50           ▼
    │          MLP Classifier
    ▼              │
2048-d             ▼
              Good / Bad Codi
```

최종적으로 두 의류 아이템의 임베딩을 concatenate하여 4096차원의 벡터를 만들고, MLP classifier가 두 아이템의 궁합을 **`Good Codi`** 또는 **`Bad Codi`**로 분류한다.

Model weights:

```text
cody_recommend(second_train).pth
```

## Recommendation

사용자의 옷장에서 검출된 상의와 하의의 가능한 모든 조합을 생성한다.

각 조합을 `ImageRelationClassifier`에 입력하여 코디 궁합을 예측하고, 예측 결과를 바탕으로 적합한 조합을 추천한다.

```text
User Closet
    │
    ├── Top 1 ──┐
    ├── Top 2 ──┼── Outfit Pairs
    └── ...     │
                ├── Top 1 + Bottom 1
                ├── Top 1 + Bottom 2
                ├── Top 2 + Bottom 1
                └── ...
                       ↓
              ImageRelationClassifier
                       ↓
                Compatibility Score
                       ↓
                Recommended Outfit
```

## Key Components

### 1. Flask Web Application

Flask를 이용하여 사용자가 의류 이미지를 업로드하고 추천 결과를 확인할 수 있는 간단한 GUI 웹 애플리케이션을 구현했다.

### 2. Clothing Detection — YOLOv8

업로드된 이미지에서 의류 아이템을 검출하고 각 아이템을 개별 이미지로 crop한다.

### 3. Feature Extraction — ResNet50

검출된 의류 이미지를 ResNet50에 입력하여 각각 **2048-dimensional visual embedding**으로 변환한다.

### 4. Outfit Compatibility — MLP

상의와 하의의 임베딩을 결합한 4096-dimensional feature를 MLP classifier에 입력하여 코디 궁합을 예측한다.

### 5. Dataset

**Musinsa**에서 의류 및 코디 데이터를 크롤링하여 추천 모델 학습에 활용했다.

## Tech Stack

| Component            | Technology            |
| -------------------- | --------------------- |
| Web Application      | Flask                 |
| Object Detection     | YOLOv8                |
| Feature Extraction   | ResNet50              |
| Recommendation Model | MLP                   |
| Dataset              | Musinsa Crawling Data |
| Model Framework      | PyTorch               |
| Environment          | Conda                 |

## How to Run

### 1. Clone

```bash
git clone https://github.com/basamg912/Clothing-Detection-and-Outfit-Recommendation-System.git
cd Clothing-Detection-and-Outfit-Recommendation-System
```

### 2. Create Conda Environment

```bash
conda env create -f environment.yml
conda activate cody
```

### 3. Run Application

```bash
python app.py
```

### 4. Open Browser

Open the following address in your browser:

```text
http://localhost:5000
```
