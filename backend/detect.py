import torch
from PIL import Image
import io   
import base64

def load_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.to(device)
    print(f"🚀 YOLO model loaded on: {device}")
    if torch.cuda.is_available():
        print(f"🎮 GPU: {torch.cuda.get_device_name(0)}")
    return model

model = load_model()

def detect_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    results = model(img)
    detections = results.pandas().xyxy[0].to_dict(orient="records")
    return detections