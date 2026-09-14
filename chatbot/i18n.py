from functools import lru_cache

LANGUAGES = {
    "English": "en",
    "العربية": "ar",
}

COMMON = {
    "welcome": "Welcome to Smart Finishing AI. I will ask a few questions about your apartment and estimate the finishing cost.",
    "area": "What is the apartment area in square meters?",
    "rooms": "How many bedrooms are there?",
    "bathrooms": "How many bathrooms are there?",
    "master_bathrooms": "How many of these bathrooms are master bathrooms?",
    "balconies": "How many balconies are there?",
    "receptions": "How many reception/living areas are there?",
    "level": "What overall finishing level do you want: Low, Medium, or High?",
    "ceilings": "What ceiling quality do you want: Low, Medium, or High?",
    "doors": "What door quality do you want: Low, Medium, or High?",
    "electrical_basic": "What basic electrical quality do you want: Low, Medium, or High?",
    "electrical_finishing": "What electrical finishing quality do you want: Low, Medium, or High?",
    "flooring": "What flooring quality do you want: Low, Medium, or High?",
    "paints": "What paint quality do you want: Low, Medium, or High?",
    "plumbing_quality": "What plumbing quality do you want: Low, Medium, or High?",
    "sanitary": "What sanitary-ware quality do you want: Low, Medium, or High?",
    "ceiling_upgrade": "Do you want a decorative reception ceiling upgrade?",
    "chandelier": "Do you want a reception chandelier?",
    "master_upgrade": "Do you want a master-bathroom shower/cabin upgrade?",
    "plumbing_system": "Which plumbing system do you prefer: PVC or PPR?",
    "thinking": "Calculating your estimate...",
    "total": "Estimated total finishing cost",
    "range": "Empirical prediction range",
    "breakdown": "Cost breakdown",
    "included": "What is included",
    "disclaimer": "This estimate is based on the packaged product-price data and scenario-generated training data. It is an estimate, not a contractor quotation.",
    "restart": "Start a new estimate",
    "error": "I couldn't understand that answer. Please try again.",
}

ARABIC = {
    "welcome": "مرحبًا بك في Smart Finishing AI. سأطرح عليك بعض الأسئلة عن شقتك ثم أقدر لك تكلفة التشطيب.",
    "area": "ما مساحة الشقة بالمتر المربع؟",
    "rooms": "كم عدد غرف النوم؟",
    "bathrooms": "كم عدد الحمامات؟",
    "master_bathrooms": "كم عدد الحمامات الرئيسية (الماستر)؟",
    "balconies": "كم عدد البلكونات؟",
    "receptions": "كم عدد مناطق الريسبشن أو المعيشة؟",
    "level": "ما مستوى التشطيب الذي تريده بشكل عام: منخفض، متوسط، أم مرتفع؟",
    "ceilings": "ما جودة الأسقف التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "doors": "ما جودة الأبواب التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "electrical_basic": "ما جودة الكهرباء الأساسية التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "electrical_finishing": "ما جودة الكهرباء النهائية التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "flooring": "ما جودة الأرضيات التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "paints": "ما جودة الدهانات التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "plumbing_quality": "ما جودة السباكة التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "sanitary": "ما جودة الأدوات الصحية التي تريدها: منخفضة، متوسطة، أم مرتفعة؟",
    "ceiling_upgrade": "هل تريد تطويرًا ديكوريًا لسقف الريسبشن؟",
    "chandelier": "هل تريد إضافة نجفة للريسبشن؟",
    "master_upgrade": "هل تريد تطوير حمام الماستر بإضافة شاور أو كابينة؟",
    "plumbing_system": "أي نظام سباكة تفضل: PVC أم PPR؟",
    "thinking": "جاري حساب التكلفة التقديرية...",
    "total": "إجمالي تكلفة التشطيب التقديرية",
    "range": "نطاق التوقع التقديري",
    "breakdown": "تفصيل التكلفة",
    "included": "المكونات والتجهيزات المشمولة",
    "disclaimer": "هذا التقدير مبني على بيانات أسعار المنتجات وبيانات التدريب المستخدمة في النموذج. وهو تقدير تقريبي وليس عرض سعر من مقاول.",
    "restart": "بدء تقدير جديد",
    "error": "لم أتمكن من فهم هذه الإجابة. حاول مرة أخرى.",
}


@lru_cache(maxsize=512)
def translate_text(text: str, target: str) -> str:
    if target == "en":
        return text

    if target == "ar":
        for key, value in COMMON.items():
            if value == text:
                return ARABIC.get(key, text)

    return text


def t(key: str, language: str = "en") -> str:
    if language == "ar":
        return ARABIC.get(
            key,
            COMMON.get(key, key)
        )

    return COMMON.get(key, key)
