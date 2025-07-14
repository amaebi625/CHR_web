# inference_single.py
import torch
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from .faster_rcnn import get_faster_rcnn_model
import os

def run_inference_on_image(image: Image.Image, model_path: str = "config/faster_rcnn.pth", score_threshold: float = 0.7):
    """
    对上传图像进行推理并绘图标注检测框（仅显示编号，字号更大）。
    
    Returns:
        result_img: PIL.Image with red/orange boxes and large number labels
        total_count: int, all predicted boxes
        kept_count: int, boxes with score > threshold
        kept_scores: list of float, scores > threshold (顺序与编号一致)
    """
    transform = transforms.Compose([transforms.ToTensor()])
    image_tensor = transform(image).unsqueeze(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = get_faster_rcnn_model(num_classes=2)
    model.load_state_dict(torch.load(model_path, map_location=device)['model_state_dict'])
    model.to(device)
    model.eval()

    with torch.no_grad():
        output = model(image_tensor.to(device))[0]

    boxes = output["boxes"].cpu().numpy()
    scores = output["scores"].cpu().numpy()

    result_img = image.copy()
    draw = ImageDraw.Draw(result_img)

    kept_scores = []
    kept_boxes = []
    total_count = len(scores)

    for i, score in enumerate(scores):
        if score >= score_threshold:
            kept_scores.append(float(score))
            kept_boxes.append(boxes[i])


    for idx, (box, score) in enumerate(zip(kept_boxes, kept_scores)):
        x1, y1, x2, y2 = box
        color = "red" if score > 0.9 else "orange"
        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
        draw.text((x1, y1 - 50), f"{idx + 1}", fill=color, font_size=40)

    kept_count = len(kept_scores)
    return result_img, total_count, kept_count, kept_scores
