from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import sys
import os

# إضافة المجلد الرئيسي للمسار لرؤية الموديولات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ocr_engine import ANPRSystem

app = FastAPI(title="Saudi ANPR API")

# متغير عالمي للنظام
anpr_system = None

@app.on_event("startup")
def startup_event():
    global anpr_system
    # تأكد أن ملف best.pt موجود داخل مجلد weights
    model_path = os.path.join("weights", "best.pt")
    if os.path.exists(model_path):
        anpr_system = ANPRSystem(model_path=model_path)
    else:
        print(f"❌ Error: Model not found at {model_path}")

@app.get("/")
def home():
    return {"message": "Saudi ANPR API is Running 🚀"}

@app.post("/detect/")
async def detect_plate(file: UploadFile = File(...)):
    if anpr_system is None:
        return {"status": "error", "message": "Model not loaded properly"}

    # قراءة الصورة
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # التوقع
    results = anpr_system.predict(image)

    if not results:
        return {"status": "failed", "message": "No plate detected"}
    
    return {
        "status": "success",
        "plates": results
    }
