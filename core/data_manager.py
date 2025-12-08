import pandas as pd
import os
from datetime import datetime

# متغير في الرامات لحفظ القائمة اليومية (لسرعة البحث)
DAILY_WANTED_PLATES = set()

# اسم ملف السجل اليومي (النتيجة)
LOG_FILE = "daily_detections.csv"

def load_daily_file(file_path):
    """
    قراءة ملف الإكسيل/CSV اليومي وتخزين اللوحات المطلوبة في الذاكرة
    """
    global DAILY_WANTED_PLATES
    DAILY_WANTED_PLATES.clear() # مسح بيانات الأمس
    
    try:
        # قراءة الملف سواء كان excel أو csv
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # ⚠️ هام: افترضنا أن عمود اللوحات اسمه "Plate" أو هو أول عمود
        # سنقوم بتنظيف البيانات وحفظها
        # يتم تحويل كل القيم لنص وإزالة المسافات
        first_column = df.iloc[:, 0].astype(str).str.replace(" ", "")
        
        for plate in first_column:
            DAILY_WANTED_PLATES.add(plate)
            
        print(f"✅ تم تحميل القائمة اليومية: {len(DAILY_WANTED_PLATES)} سيارة مطلوبة.")
        return True, len(DAILY_WANTED_PLATES)
        
    except Exception as e:
        print(f"❌ خطأ في قراءة الملف: {e}")
        return False, str(e)

def check_is_wanted(plate_text):
    """البحث في القائمة اليومية"""
    # تنظيف اللوحة المكتشفة من المسافات للمقارنة
    clean_plate = plate_text.replace(" ", "")
    
    if clean_plate in DAILY_WANTED_PLATES:
        return True
    return False

def log_to_file(plate_text, confidence):
    """
    تسجيل السيارة المطلوبة في ملف نصي (شكل جدول)
    """
    # لو الملف مش موجود، نكتب العناوين (Header)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8-sig") as f:
            f.write("Time,Plate Number,Confidence,Status\n")
    
    # تسجيل البيانات
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8-sig") as f:
        f.write(f"{now},{plate_text},{confidence},WANTED 🚨\n")
    
    print(f"📝 تم تسجيل الحالة في الملف: {plate_text}")