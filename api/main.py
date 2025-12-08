from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import sys
import os
import shutil
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ocr_engine import ANPRSystem
# استدعاء المدير الجديد
from core.data_manager import load_daily_file, check_is_wanted, log_to_file

app = FastAPI(title="Saudi ANPR - Daily System")

# تفعيل الملفات الثابتة (عشان الصور والـ CSS لو فيه)
app.mount("/static", StaticFiles(directory="static"), name="static")

# الصفحة الرئيسية (تعرض الموقع)
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# تحميل الموديل مرة واحدة
model_path = os.path.join("weights", "best.pt")
anpr_system = ANPRSystem(model_path=model_path)

# 1️⃣ API لرفع الملف اليومي (يستخدمه الضابط في بداية اليوم)
@app.post("/upload_list/")
async def upload_daily_list(file: UploadFile = File(...)):
    # حفظ الملف مؤقتاً
    temp_filename = f"temp_{file.filename}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # تحميل البيانات للذاكرة
    success, info = load_daily_file(temp_filename)
    
    # حذف الملف المؤقت (خلاص البيانات بقت في الرامات)
    os.remove(temp_filename)
    
    if success:
        return {"status": "success", "message": f"تم تفعيل القائمة اليومية: {info} سيارة"}
    else:
        return {"status": "error", "message": f"فشل تحميل الملف: {info}"}

# 2️⃣ API الكشف (يستخدمه الموبايل لايف)
@app.post("/detect/")
async def detect_plate(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # كشف اللوحة
    results = anpr_system.predict(image)

    if not results:
        return {"status": "failed", "message": "No plate detected"}
    
    processed_plates = []
    
    for plate in results:
        plate_text = plate['full_plate_ar']
        
        # 🔍 البحث في القائمة اليومية
        is_wanted = check_is_wanted(plate_text)
        
        plate['is_wanted'] = is_wanted
        
        # 🚨 لو مطلوبة: سجلها فوراً في ملف التقرير
        if is_wanted:
            log_to_file(plate_text, plate['confidence'])
            plate['alert_msg'] = "مطلوبة أمنياً"
            
        processed_plates.append(plate)
    
    return {
        "status": "success",
        "plates": processed_plates
    }