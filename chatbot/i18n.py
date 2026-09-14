from __future__ import annotations


LANGUAGES = {
    "English": "en",
    "العربية": "ar",
}


TRANSLATIONS = {
    "en": {
        "welcome": (
            "Welcome to Smart Finishing AI. "
            "I will ask you a few questions about your apartment "
            "and estimate the finishing cost."
        ),
        "area": "What is the apartment area in square meters?",
        "rooms": "How many bedrooms are there?",
        "bathrooms": "How many bathrooms are there?",
        "master_bathrooms": "How many of these bathrooms are master bathrooms?",
        "balconies": "How many balconies are there?",
        "receptions": "How many reception/living areas are there?",
        "level": "What overall finishing level do you want: Low, Medium, or High?",
        "ceilings": "What ceiling quality do you want: Low, Medium, or High?",
        "doors": "What door quality do you want: Low, Medium, or High?",
        "electrical_basic": (
            "What basic electrical quality do you want: "
            "Low, Medium, or High?"
        ),
        "electrical_finishing": (
            "What electrical finishing quality do you want: "
            "Low, Medium, or High?"
        ),
        "flooring": "What flooring quality do you want: Low, Medium, or High?",
        "paints": "What paint quality do you want: Low, Medium, or High?",
        "plumbing_quality": (
            "What plumbing quality do you want: Low, Medium, or High?"
        ),
        "sanitary": (
            "What sanitary-ware quality do you want: "
            "Low, Medium, or High?"
        ),
        "ceiling_upgrade": (
            "Do you want a decorative reception ceiling upgrade?"
        ),
        "chandelier": "Do you want a reception chandelier?",
        "master_upgrade": (
            "Do you want a master-bathroom shower/cabin upgrade?"
        ),
        "plumbing_system": "Which plumbing system do you prefer: PVC or PPR?",
        "thinking": "Calculating your estimate...",
        "total": "Estimated total finishing cost",
        "range": "Estimated prediction range",
        "breakdown": "Cost breakdown",
        "included": "What is included",
        "disclaimer": (
            "This estimate is based on packaged product-price data "
            "and scenario-generated training data. "
            "It is an estimate, not a contractor quotation."
        ),
        "restart": "Start a new estimate",
        "error": "I couldn't understand that answer. Please try again.",
        "continue": "Continue",
        "choose_language": "Choose your language",
        "language_description": (
            "Please select your preferred language before starting "
            "the assistant."
        ),
        "language": "Language",
        "settings": "Settings",
        "change_language": "Change Language",
        "type_answer": "Type your answer...",
        "currency": "EGP",
        "currency_name": "EGP",
        "category_ceilings": "Ceilings",
        "category_doors": "Doors",
        "category_electrical_basic": "Basic Electrical",
        "category_electrical_finishing": "Electrical Finishing",
        "category_flooring": "Flooring",
        "category_paints": "Paints",
        "category_plumbing": "Plumbing",
        "category_sanitary": "Sanitary Ware",
        "category_reception_ceiling": "Reception Ceiling",
        "category_reception_chandelier": "Reception Chandelier",
        "category_master_bathroom": "Master Bathroom",
        "unit_piece": "piece",
        "unit_pieces": "pieces",
        "unit_unit": "unit",
        "unit_units": "units",
        "unit_meter": "meter",
        "unit_meters": "meters",
        "unit_liter": "liter",
        "unit_liters": "liters",
        "unit_box": "box",
        "unit_boxes": "boxes",
        "unit_set": "set",
        "unit_sets": "sets",
        "allocation_method": (
            "The cost was allocated using product-price data "
            "and the training scenarios used by the model."
        ),
        "master_bathrooms_error": (
            "Master bathrooms cannot exceed total bathrooms."
        ),
        "bathrooms_error": (
            "Total bathrooms cannot be less than master bathrooms."
        ),
    },
    "ar": {
        "welcome": (
            "مرحبًا بك في Smart Finishing AI. "
            "سأطرح عليك بعض الأسئلة عن شقتك "
            "ثم أقدر لك تكلفة التشطيب."
        ),
        "area": "ما مساحة الشقة بالمتر المربع؟",
        "rooms": "كم عدد غرف النوم؟",
        "bathrooms": "كم عدد الحمامات؟",
        "master_bathrooms": "كم عدد الحمامات الرئيسية (الماستر)؟",
        "balconies": "كم عدد البلكونات؟",
        "receptions": "كم عدد مناطق الريسبشن أو المعيشة؟",
        "level": (
            "ما مستوى التشطيب الذي تريده بشكل عام: "
            "منخفض، متوسط، أم مرتفع؟"
        ),
        "ceilings": (
            "ما جودة الأسقف التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "doors": (
            "ما جودة الأبواب التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "electrical_basic": (
            "ما جودة الكهرباء الأساسية التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "electrical_finishing": (
            "ما جودة الكهرباء النهائية التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "flooring": (
            "ما جودة الأرضيات التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "paints": (
            "ما جودة الدهانات التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "plumbing_quality": (
            "ما جودة السباكة التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "sanitary": (
            "ما جودة الأدوات الصحية التي تريدها: "
            "منخفضة، متوسطة، أم مرتفعة؟"
        ),
        "ceiling_upgrade": (
            "هل تريد تطويرًا ديكوريًا لسقف الريسبشن؟"
        ),
        "chandelier": "هل تريد إضافة نجفة للريسبشن؟",
        "master_upgrade": (
            "هل تريد تطوير حمام الماستر بإضافة شاور أو كابينة؟"
        ),
        "plumbing_system": "أي نظام سباكة تفضل: PVC أم PPR؟",
        "thinking": "جاري حساب التكلفة التقديرية...",
        "total": "إجمالي تكلفة التشطيب التقديرية",
        "range": "نطاق التكلفة التقديري",
        "breakdown": "تفصيل التكلفة",
        "included": "المكونات والتجهيزات المشمولة",
        "disclaimer": (
            "هذا التقدير مبني على بيانات أسعار المنتجات "
            "وبيانات التدريب المستخدمة في النموذج. "
            "وهو تقدير تقريبي وليس عرض سعر من مقاول."
        ),
        "restart": "بدء تقدير جديد",
        "error": "لم أتمكن من فهم هذه الإجابة. حاول مرة أخرى.",
        "continue": "متابعة",
        "choose_language": "اختر اللغة",
        "language_description": (
            "يرجى اختيار اللغة المفضلة قبل بدء المساعد."
        ),
        "language": "اللغة",
        "settings": "الإعدادات",
        "change_language": "تغيير اللغة",
        "type_answer": "اكتب إجابتك...",
        "currency": "جنيه",
        "currency_name": "جنيه مصري",
        "category_ceilings": "الأسقف",
        "category_doors": "الأبواب",
        "category_electrical_basic": "الكهرباء الأساسية",
        "category_electrical_finishing": "الكهرباء النهائية",
        "category_flooring": "الأرضيات",
        "category_paints": "الدهانات",
        "category_plumbing": "السباكة",
        "category_sanitary": "الأدوات الصحية",
        "category_reception_ceiling": "سقف الريسبشن",
        "category_reception_chandelier": "نجفة الريسبشن",
        "category_master_bathroom": "حمام الماستر",
        "unit_piece": "قطعة",
        "unit_pieces": "قطع",
        "unit_unit": "وحدة",
        "unit_units": "وحدات",
        "unit_meter": "متر",
        "unit_meters": "متر",
        "unit_liter": "لتر",
        "unit_liters": "لتر",
        "unit_box": "علبة",
        "unit_boxes": "علب",
        "unit_set": "طقم",
        "unit_sets": "أطقم",
        "allocation_method": (
            "تم توزيع التكلفة التقديرية باستخدام "
            "بيانات أسعار المنتجات وبيانات التدريب "
            "المستخدمة في النموذج."
        ),
        "master_bathrooms_error": (
            "عدد حمامات الماستر لا يمكن أن يتجاوز "
            "إجمالي عدد الحمامات."
        ),
        "bathrooms_error": (
            "إجمالي عدد الحمامات لا يمكن أن يكون أقل "
            "من عدد حمامات الماستر."
        ),
    },
}


CATEGORY_KEYS = {
    "Ceilings": "category_ceilings",
    "Ceiling": "category_ceilings",
    "Doors": "category_doors",
    "Door": "category_doors",
    "Electrical Basic": "category_electrical_basic",
    "Basic Electrical": "category_electrical_basic",
    "Electrical Finishing": "category_electrical_finishing",
    "Finishing Electrical": "category_electrical_finishing",
    "Flooring": "category_flooring",
    "Floors": "category_flooring",
    "Paints": "category_paints",
    "Paint": "category_paints",
    "Plumbing": "category_plumbing",
    "Sanitary": "category_sanitary",
    "Sanitary Ware": "category_sanitary",
    "Reception Ceiling": "category_reception_ceiling",
    "Reception Chandelier": "category_reception_chandelier",
    "Master Bathroom": "category_master_bathroom",
    "Master Bathroom Upgrade": "category_master_bathroom",
}


UNIT_KEYS = {
    "piece": "unit_piece",
    "pieces": "unit_pieces",
    "unit": "unit_unit",
    "units": "unit_units",
    "meter": "unit_meter",
    "meters": "unit_meters",
    "liter": "unit_liter",
    "liters": "unit_liters",
    "box": "unit_box",
    "boxes": "unit_boxes",
    "set": "unit_set",
    "sets": "unit_sets",
}


def t(key: str, language: str = "en") -> str:
    language = language if language in TRANSLATIONS else "en"

    return TRANSLATIONS[language].get(
        key,
        TRANSLATIONS["en"].get(key, key)
    )


def translate_category(
    category: str,
    language: str = "en"
) -> str:

    key = CATEGORY_KEYS.get(category)

    if key is None:
        return category

    return t(
        key,
        language
    )


def translate_unit(
    unit: str,
    language: str = "en"
) -> str:

    key = UNIT_KEYS.get(
        str(unit).lower()
    )

    if key is None:
        return unit

    return t(
        key,
        language
    )
