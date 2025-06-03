from PIL import Image, ImageOps
import numpy as np
import colorsys

def classify_clothes(filepath,cls_model):
    pre_img = Image.open(filepath)
    pre_img = ImageOps.exif_transpose(pre_img)
    results = cls_model(pre_img)
    res = results[0]
    if hasattr(res, 'probs') and res.probs is not None:
        probs = res.probs.cpu().numpy()
        cls_id = int(probs.argmax)
        return res.names[cls_id]
    if len(res.boxes.cls)>0:
        xy = res.boxes.xyxy[0].tolist()
        image = Image.open(filepath)
        x1,y1,x2,y2 = map(int,xy)
        cropped = pre_img.crop((x1,y1,x2,y2))
        cls_names = cls_model.model.names
        cls_name = cls_names[res.boxes.cls[0].item()]
        print(cls_name)
        return cropped,cls_name
    else:
        return "unknown"
    
def detect_color(image):
    image = image.resize((100, 100))
    np_img = np.array(image)

    h, w, _ = np_img.shape
    h1, h2 = int(h * 0.3), int(h * 0.7)
    w1, w2 = int(w * 0.3), int(w * 0.7)
    center_pixels = np_img[h1:h2, w1:w2].reshape(-1, 3)

    hsv_pixels = np.array([
        colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        for r, g, b in center_pixels
    ])

    h_vals = [h for h, s, v in hsv_pixels if s > 0.2 and v > 0.2]
    avg_h = np.mean(h_vals) if h_vals else 0.0
    avg_s = np.mean([s for h, s, v in hsv_pixels])
    avg_v = np.mean([v for h, s, v in hsv_pixels])

    h_deg = avg_h * 360

    # 무채색 분리
    if avg_s < 0.25 and avg_v > 0.7:
        return "white"
    elif avg_s < 0.2 and avg_v < 0.4:
        return "black"
    elif avg_s < 0.25:
        return "gray"

    # 색상 분류
    if 180 <= h_deg <= 250 and avg_s > 0.3 and avg_v < 0.4:
        return "navy"
    elif 200 <= h_deg <= 250 and avg_v >= 0.5:
        return "blue"
    elif 190 <= h_deg < 210 and avg_v > 0.7:
        return "skyblue"
    elif 30 <= h_deg <= 45 and avg_s < 0.5 and avg_v > 0.7:
        return "beige"
    elif 10 <= h_deg <= 25 and avg_s > 0.4 and avg_v < 0.6:
        return "brown"
    elif 55 <= h_deg <= 85 and avg_s < 0.5 and 0.4 <= avg_v <= 0.75:
        return "khaki"
    elif 290 <= h_deg <= 340:
        return "pink"
    elif 40 <= h_deg <= 65:
        return "yellow"
    elif 85 <= h_deg <= 160:
        return "green"

    return "unknown"
