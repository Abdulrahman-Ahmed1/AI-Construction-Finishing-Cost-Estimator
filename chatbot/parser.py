"""Language-agnostic-ish input parsing for the Streamlit questionnaire.
Free-form numeric answers work in any language; common yes/no and quality words
are normalized across several languages, with English fallback.
"""
import re

YES = {"yes","y","true","1","oui","si","sí","ja","да","是","是的","نعم","أيوه","ايوه","اه","أه","نعم","evet","sim","হ্যাঁ","हाँ","ہاں","네"}
NO = {"no","n","false","0","non","nein","нет","否","لا","لأ","للا","hayır","não","না","नहीं","نہیں","아니요"}
QUALITY = {
    "low": "Low", "basic": "Low", "economy": "Low", "منخفض": "Low", "اقتصادي": "Low", "faible": "Low", "niedrig": "Low",
    "medium": "Medium", "mid": "Medium", "متوسط": "Medium", "moyen": "Medium", "mittel": "Medium",
    "high": "High", "premium": "High", "عالي": "High", "مرتفع": "High", "élevé": "High", "hoch": "High",
}
PLUMBING = {
    "pvc pipes": "PVC Pipes", "pvc": "PVC Pipes", "بلاستيك": "PVC Pipes", "pvc أنابيب": "PVC Pipes",
    "ppr pipes": "PPR Pipes", "ppr": "PPR Pipes", "حراري": "PPR Pipes", "ppr أنابيب": "PPR Pipes",
}

def _norm(x):
    return re.sub(r"\s+", " ", str(x).strip().lower())

def parse_answer(text: str, kind: str):
    s = _norm(text)
    if kind == "number":
        m = re.search(r"[-+]?\d+(?:[.,]\d+)?", s)
        if not m:
            raise ValueError("Please enter a number.")
        return float(m.group(0).replace(",", "."))
    if kind == "int":
        m = re.search(r"\d+", s)
        if not m:
            raise ValueError("Please enter a whole number.")
        return int(m.group(0))
    if kind == "yesno":
        if s in YES or any(w in s.split() for w in YES if len(w) > 2): return True
        if s in NO or any(w in s.split() for w in NO if len(w) > 2): return False
        raise ValueError("Please answer yes/no.")
    if kind == "quality":
        if s in QUALITY: return QUALITY[s]
        for key, value in QUALITY.items():
            if key in s: return value
        raise ValueError("Please choose Low, Medium, or High.")
    if kind == "plumbing":
        if s in PLUMBING: return PLUMBING[s]
        if "ppr" in s: return "PPR Pipes"
        if "pvc" in s: return "PVC Pipes"
        raise ValueError("Please choose PVC or PPR pipes.")
    return text.strip()
