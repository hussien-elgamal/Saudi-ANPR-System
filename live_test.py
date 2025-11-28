import cv2
import requests
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

# ---------------- إعدادات النظام ----------------
API_URL = "http://127.0.0.1:8000/detect/"
# مسار خط Arial (يدعم العربية وموجود في الويندوز)
FONT_PATH = "C:/Windows/Fonts/arial.ttf" 
CONFIDENCE_THRESHOLD = 0.30  # عرض النتائج التي دقتها أعلى من 30% فقط

def draw_plate_info(img, text_ar, text_en, conf, x, y):
    """
    دالة لرسم النص العربي والإنجليزي فوق اللوحة
    """
    # تحويل الصورة من OpenCV (BGR) إلى PIL (RGB) للكتابة بالعربي
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    
    try:
        font_ar = ImageFont.truetype(FONT_PATH, 40) # خط العربي
        font_en = ImageFont.truetype(FONT_PATH, 20) # خط الإنجليزي
    except:
        font_ar = ImageFont.load_default()
        font_en = ImageFont.load_default()

    # معالجة النص العربي (عشان الحروف تشبك في بعض)
    reshaped_text = arabic_reshaper.reshape(text_ar)
    bidi_text = get_display(reshaped_text)
    
    # رسم خلفية سوداء شفافة خلف النص للقراءة بوضوح
    # الإحداثيات (x, y) هي الركن العلوي الأيسر للوحة
    # بنرسم المربع فوق اللوحة بشوية
    box_x1, box_y1 = x, y - 90
    box_x2, box_y2 = x + 250, y - 5
    
    if box_y1 < 0: # لو اللوحة في سقف الشاشة، نرسم تحتها
        box_y1, box_y2 = y + 50, y + 140

    draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(0, 0, 0, 180)) 

    # كتابة النص العربي
    draw.text((box_x1 + 10, box_y1 + 5), bidi_text, font=font_ar, fill=(0, 255, 0)) # أخضر
    
    # كتابة النص الإنجليزي والدقة
    info_text = f"Raw: {text_en} ({int(conf*100)}%)"
    draw.text((box_x1 + 10, box_y1 + 55), info_text, font=font_en, fill=(200, 200, 200)) # رمادي

    # إعادة الصورة لـ OpenCV
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# ---------------- بداية التشغيل ----------------
cap = cv2.VideoCapture(0)
# ضبط الجودة لـ HD (توازن ممتاز بين السرعة والدقة)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("🚀 النظام يعمل... وجه الكاميرا للوحات السيارات (اضغط q للخروج)")

while True:
    ret, frame = cap.read()
    if not ret: break

    h, w, _ = frame.shape
    
    # --- 1. القص الذكي (Smart Zoom) ---
    # نركز فقط على المنطقة الوسطى (60% من الشاشة) ونبعتها للسيرفر
    # ده بيخلي اللوحات البعيدة تظهر أكبر وأوضح للموديل
    crop_val = 0.6
    dx, dy = int(w * crop_val // 2), int(h * crop_val // 2)
    cx, cy = w // 2, h // 2
    
    start_x, start_y = cx - dx, cy - dy
    end_x, end_y = cx + dx, cy + dy
    
    # الصورة اللي بتتبعت للسيرفر
    cropped_frame = frame[start_y:end_y, start_x:end_x]
    
    # رسم مربع أزرق يوضح المنطقة اللي السيرفر بيشوفها
    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)

    try:
        # --- 2. إرسال الصورة للسيرفر ---
        _, img_encoded = cv2.imencode('.jpg', cropped_frame)
        response = requests.post(API_URL, files={"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")})
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                
                # --- 3. معالجة الرد (دعم تعدد اللوحات) ---
                for plate in data['plates']:
                    conf = plate.get('confidence', 0)
                    
                    if conf > CONFIDENCE_THRESHOLD:
                        full_ar = plate['full_plate_ar']
                        raw_en = plate['raw_english']
                        bbox = plate.get('bbox', [0,0,0,0])

                        # تحويل الإحداثيات:
                        # الإحداثيات جاية بالنسبة للصورة المقصوصة، لازم نرجعها للصورة الأصلية
                        # عن طريق إضافة نقطة البداية (start_x, start_y)
                        x1 = int(bbox[0]) + start_x
                        y1 = int(bbox[1]) + start_y
                        x2 = int(bbox[2]) + start_x
                        y2 = int(bbox[3]) + start_y

                        # رسم مربع أخضر حول اللوحة المكتشفة
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)

                        # كتابة البيانات فوق اللوحة
                        frame = draw_plate_info(frame, full_ar, raw_en, conf, x1, y1)
                        
                        print(f"✅ سيارة مكتشفة: {full_ar}")

    except Exception as e:
        # تجاهل الأخطاء اللحظية (عشان اللايف ميفصلش لو حصل Network glitch)
        pass 

    # عرض الفيديو النهائي
    cv2.imshow("Saudi ANPR - Final Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()