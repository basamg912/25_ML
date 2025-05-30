def classify_clothes(filepath,cls_model):
    results = cls_model(filepath)
    res = results[0]
    if hasattr(res, 'probs') and res.probs is not None:
        probs = res.probs.cpu().numpy()
        cls_id = int(probs.argmax)
    else:
        cls_id = int(res.boxes.cls[0].cpu().numpy())
    return res.names[cls_id]
