def classify_clothes(filepath):
    # 파일명에 따라 임의 분류(예시)
    if "top" in filepath:
        return "상의"
    elif "pants" in filepath:
        return "하의"
    else:
        return "기타"
