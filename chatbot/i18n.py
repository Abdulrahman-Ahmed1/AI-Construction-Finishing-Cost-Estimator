"""Multilingual UI/question translations with online auto-translation fallback.
The app remains usable without a translation service by falling back to English.
"""
from functools import lru_cache

LANGUAGES = {
    "English": "en", "العربية": "ar", "Français": "fr", "Español": "es", "Deutsch": "de",
    "Italiano": "it", "Português": "pt", "Türkçe": "tr", "Русский": "ru", "中文": "zh-CN",
    "日本語": "ja", "한국어": "ko", "हिन्दी": "hi", "বাংলা": "bn", "اردو": "ur",
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
    "low": "Low", "medium": "Medium", "high": "High", "yes": "Yes", "no": "No",
    "pvc": "PVC", "ppr": "PPR",
}

@lru_cache(maxsize=512)
def translate_text(text: str, target: str) -> str:
    if target == "en": return text
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception:
        return text

def t(key: str, language: str = "en") -> str:
    text = COMMON.get(key, key)
    return translate_text(text, language)
