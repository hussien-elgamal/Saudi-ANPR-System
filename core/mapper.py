import re

class SaudiPlateMapper:
    def __init__(self):
        # القاموس الرسمي للمرور السعودي
        self.mapping = {
            'A': 'أ', 'B': 'ب', 'J': 'ح', 'D': 'د', 'R': 'ر',
            'S': 'س', 'X': 'ص', 'T': 'ط', 'E': 'ع', 'G': 'ق',
            'K': 'ك', 'L': 'ل', 'M': 'م', 'N': 'ن', 'H': 'هـ',
            'U': 'و', 'V': 'ى'
        }

    def format_text(self, text):
        # تنظيف النص
        clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        letters_list = []
        numbers_list = []
        
        # فصل الحروف عن الأرقام
        for char in clean_text:
            if char.isalpha():
                letters_list.append(char)
            elif char.isdigit():
                numbers_list.append(char)
        
        # --- الفلتر الذكي للحروف (التعديل الجديد) ---
        # اللوحات السعودية 3 حروف فقط.
        # لو لقينا أكتر من 3، ناخد آخر 3 (لأنهم الأوضح والأساسيين)
        if len(letters_list) > 3:
            letters_list = letters_list[-3:]
            
        # --- الفلتر الذكي للأرقام ---
        # اللوحات السعودية بحد أقصى 4 أرقام
        if len(numbers_list) > 4:
            numbers_list = numbers_list[-4:]
            
        # الترجمة للعربية
        arabic_letters = [self.mapping.get(char, char) for char in letters_list]
        
        # التجميع النهائي
        str_numbers = "".join(numbers_list)
        str_arabic = " ".join(arabic_letters)
        
        return {
            "full_plate_ar": f"{str_arabic} {str_numbers}",
            "letters": str_arabic,
            "numbers": str_numbers,
            "raw_english": clean_text
        }