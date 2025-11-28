import os

# --- محتويات الملفات ---

requirements_content = """fastapi
uvicorn
ultralytics
paddlepaddle-gpu
paddleocr
opencv-python-headless
python-multipart
numpy
"""

mapper_content = """import re

class SaudiPlateMapper:
    def __init__(self):
        # القاموس الرسمي للمرور السعودي: تحويل اللاتيني إلى العربي
        self.mapping = {
            'A': 'أ', 'B': 'ب', 'J': 'ح', 'D': 'د', 'R': 'ر',
            'S': 'س', 'X': 'ص', 'T': 'ط', 'E': 'ع', 'G': 'ق',
            'K': 'ك', 'L': 'ل', 'M': 'م', 'N': 'ن', 'H': 'هـ',
            'U': 'و', 'V': 'ى'
        }

    def format_text(self, text):
        # تنظيف النص: إبقاء الحروف والأرقام الإنجليزية فقط
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        arabic_part = []
        number_part = []
        
        for char in clean_text:
            if char.isalpha():
                # تحويل الحرف
                arabic_part.append(self.mapping.get(char, char))
            elif char.isdigit():
                number_part.append(char)
        
        # تجميع النص العربي والأرقام
        str_arabic = " ".join(arabic_part)
        str_numbers = "".join(number_part)
        
        return {
            "full_plate_ar": f"{str_arabic} {str_numbers}",
            "letters": str_arabic,
            "numbers": str_numbers,
            "raw_english": clean_text
        }
"""

ocr_engine_content = """from ultralytics import YOLO
from paddleocr import PaddleOCR
import numpy as np
from .mapper import SaudiPlateMapper

class ANPRSystem:
    def __init__(self, model_path='weights/best.pt'):
        print("⏳ Loading YOLO & PaddleOCR Models...")
        # تحميل YOLO للكشف
        self.detector = YOLO(model_path)
        # تحميل OCR باللغة الإنجليزية للدقة العالية
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        # تحميل قاموس التحويل
        self.mapper = SaudiPlateMapper()
        print("✅ System Ready!")

    def predict(self, image_array):
        # الكشف عن اللوحة
        results = self.detector(image_array, verbose=False, device=0) # device=0 للـ GPU
        detected_plates = []

        for result in results:
            for box in result.boxes:
                # 1. قص الصورة
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plate_crop = image_array[y1:y2, x1:x2]

                # 2. قراءة النص (OCR)
                # det=True, rec=True, cls=True (لتصحيح الزوايا)
                ocr_result = self.ocr.ocr(plate_crop, cls=True)
                
                if ocr_result and ocr_result[0]:
                    # دمج النصوص المقروءة
                    raw_text = "".join([line[1][0] for line in ocr_result[0]])
                    conf = box.conf[0].item()

                    # 3. التحويل للعربية
                    formatted_data = self.mapper.format_text(raw_text)
                    
                    formatted_data['confidence'] = round(conf, 2)
                    formatted_data['bbox'] = [x1, y1, x2, y2]
                    
                    detected_plates.append(formatted_data)

        return detected_plates
"""

api_main_content = """from fastapi import FastAPI, File, UploadFile
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
    nparr = np.frombuffer(contents, np.fromuint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # التوقع
    results = anpr_system.predict(image)

    if not results:
        return {"status": "failed", "message": "No plate detected"}
    
    return {
        "status": "success",
        "plates": results
    }
"""

# --- دالة إنشاء الملفات ---

def create_structure():
    # تعريف هيكلية الملفات والمجلدات
    structure = {
        "requirements.txt": requirements_content,
        "core/__init__.py": "",  # ملف فارغ
        "core/mapper.py": mapper_content,
        "core/ocr_engine.py": ocr_engine_content,
        "api/__init__.py": "",   # ملف فارغ
        "api/main.py": api_main_content,
        "weights/PLACE_YOUR_BEST_PT_HERE.txt": "Put your best.pt file in this folder."
    }

    print("🚀 Starting project generation...")

    for path, content in structure.items():
        # إنشاء المجلدات إذا لم تكن موجودة
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        # كتابة الملف
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✅ Created: {path}")

    print("\n🎉 Project Structure Created Successfully!")
    print("---------------------------------------")
    print("Next Steps:")
    print("1. Copy your 'best.pt' file into the 'weights' folder.")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: uvicorn api.main:app --reload")

if __name__ == "__main__":
    create_structure()