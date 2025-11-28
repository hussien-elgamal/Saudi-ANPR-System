from ultralytics import YOLO
from paddleocr import PaddleOCR
import cv2
import numpy as np
from .mapper import SaudiPlateMapper

class ANPRSystem:
    def __init__(self, model_path='weights/best.pt'):
        print("⏳ Loading YOLO (GPU) & PaddleOCR (CPU)...")
        
        # 1. تحميل YOLO
        self.detector = YOLO(model_path)
        
        # 2. تحميل OCR (CPU Stable Version)
        # ⚠️ التعديل هنا: نمرر الإعدادات الخاصة أثناء التحميل
        self.ocr = PaddleOCR(
            use_angle_cls=True, 
            lang='en', 
            show_log=False, 
            use_gpu=False,
            unclip_ratio=1.8,     # توسيع الصندوق للحروف المائلة
            det_db_thresh=0.3     # حساسية أعلى للنصوص الباهتة
        )
        
        self.mapper = SaudiPlateMapper()
        print("✅ System Ready (High Speed Mode)!")

    def enhance_image(self, img):
        """
        معالجة الصورة للتغلب على الحركة (Motion Blur)
        """
        # تحويل لرمادي
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # فلتر CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # فلتر الشحذ (Sharpening)
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)

    def predict(self, image_array):
        # الكشف السريع
        results = self.detector(
            image_array, 
            verbose=False, 
            device=0, 
            conf=0.15, 
            half=True, 
            imgsz=640
        )
        
        detected_plates = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                h, w, _ = image_array.shape
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                plate_crop = image_array[y1:y2, x1:x2]
                
                if plate_crop.size == 0: continue

                # تحسين الصورة
                plate_crop_enhanced = self.enhance_image(plate_crop)

                # قراءة النص (OCR)
                # ⚠️ التعديل هنا: حذفنا unclip_ratio من هنا لأنه موجود فوق
                ocr_result = self.ocr.ocr(plate_crop_enhanced, cls=True, det=True, rec=True)
                
                if ocr_result and ocr_result[0]:
                    raw_text = "".join([line[1][0] for line in ocr_result[0]])
                    conf = box.conf[0].item()

                    formatted_data = self.mapper.format_text(raw_text)
                    
                    if formatted_data:
                        formatted_data['confidence'] = round(conf, 2)
                        formatted_data['bbox'] = [x1, y1, x2, y2]
                        detected_plates.append(formatted_data)

        return detected_plates