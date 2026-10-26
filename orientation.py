import re
from thefuzz import fuzz
from models import OrientationKB


def normalize_common_typos(text):
    """
    Normalizes frequent student typographical errors for key campus terminology.
    """
    clean = text.lower().strip()
    typos = {
        r"\bclerance\b": "clearance",
        r"\bclearence\b": "clearance",
        r"\bclarence\b": "clearance",
        r"\brequirments?\b": "requirements",
        r"\brequrements?\b": "requirements",
        r"\bhostle\b": "hostel",
        r"\bhostal\b": "hostel",
        r"\btimetabel\b": "timetable",
        r"\bregsitration\b": "registration",
        r"\bregistraion\b": "registration",
        r"\bacceptence\b": "acceptance",
        r"\bmatribulation\b": "matriculation",
        r"\bmatricultion\b": "matriculation",
        r"\baccomodation\b": "accommodation",
        r"\bacomodation\b": "accommodation"
    }
    for pat, rep in typos.items():
        clean = re.sub(pat, rep, clean)
    return clean


def answer_orientation(question, threshold=65):
    """
    Finds the best matching orientation answer using hybrid fuzzy string matching,
    typo normalization, and semantic category prioritization.
    """
    q = normalize_common_typos(question)
    best_entry = None
    best_score = 0

    has_medical_keyword = bool(re.search(r"\b(medical|health|clinic|doctor|hospital|x-?ray)\b", q))
    is_deadline_query = bool(re.search(r"\b(when|deadline|end|ends|ending|close|closes|closing|date|last day|duration|how long)\b", q))
    is_requirements_query = bool(re.search(r"\b(how|requirement|requirements|document|documents|file|files|step|steps|what do i need|process)\b", q))

    # Fast semantic signal verification to reject out-of-domain queries
    has_orientation_signal = bool(re.search(
        r"\b("
        r"clearance|clerance|clearence|"
        r"fees?|charges?|tuition|acceptance|remita|rrr|invoice|bank|"
        r"hostel|hostle|bedspace|bed\s+space|booting|porter|room|"
        r"id\s+card|identity\s+card|student\s+card|"
        r"library|nal|borrower|cbt|thumbprint|biometric|"
        r"course\s+reg|register\s+courses?|course\s+form|adviser|hod|"
        r"general\s+studies|gsp|gs\s+courses?|"
        r"wi-?fi|eduroam|internet|clionet|"
        r"medicals?|clinic|hospital|health\s+centre|doctor|x-?ray|"
        r"cgpa|gpa|grading|grade\s+points?|first\s+class|second\s+class|degree\s+class"
        r")\b",
        q
    ))

    entries = OrientationKB.query.all()
    if not entries:
        return "The orientation knowledge base is currently being updated. Please check back shortly."

    for entry in entries:
        # If user asks for general clearance without medical keywords, do not match medicals
        if entry.category == "medicals" and "clearance" in q and not has_medical_keyword:
            continue

        # If user explicitly asks for medical clearance, do not match general faculty clearance
        if entry.category in ("clearance", "clearance_deadline") and has_medical_keyword:
            continue

        # 1. Check direct category match
        cat = (entry.category or "").lower().replace("_", " ")
        cat_score = fuzz.token_set_ratio(q, cat)
        if cat in q and cat != "clearance":
            cat_score = max(cat_score, 88)
        elif cat == "clearance" and "clearance" in q and not is_deadline_query:
            cat_score = max(cat_score, 88)

        # 2. Check each pattern variation
        pattern_scores = []
        for pattern in entry.question_pattern.lower().split(","):
            p = pattern.strip()
            if not p:
                continue
            set_ratio = fuzz.token_set_ratio(q, p)
            partial_ratio = fuzz.partial_ratio(q, p)
            
            # If the user's question contains the pattern or pattern contains user's question
            if p in q or q in p:
                pattern_scores.append(max(set_ratio, 92))
            else:
                pattern_scores.append((set_ratio * 0.7) + (partial_ratio * 0.3))

        max_pattern_score = max(pattern_scores) if pattern_scores else 0
        combined_score = max(cat_score, max_pattern_score)

        # Disambiguate Deadlines vs Requirements
        if is_deadline_query:
            if entry.category in ("clearance_deadline", "registration_deadline"):
                combined_score += 15
            elif entry.category in ("clearance", "registration_steps"):
                combined_score -= 25

        if is_requirements_query and ("clearance" in q or "register" in q or "registration" in q):
            if entry.category in ("clearance", "registration_steps"):
                combined_score += 15
            elif entry.category in ("clearance_deadline", "registration_deadline"):
                combined_score -= 25

        if combined_score > best_score:
            best_entry = entry
            best_score = combined_score

    # Return top answer if confidence threshold met and semantic relevance confirmed
    if best_entry:
        if has_orientation_signal and best_score >= threshold:
            return best_entry.answer
        if not has_orientation_signal and best_score >= 82:
            return best_entry.answer

    # Helpful fallback showing available knowledge domains
    return (
        "I couldn't find an exact match for that question. Here are key campus topics I can guide you through:\n"
        "• **Fees & Payments**: Acceptance fee, school charges, Remita RRR invoice.\n"
        "• **Academics & Registration**: Course enrollment, advisers, clearance requirements.\n"
        "• **Campus Living**: Hostel allocation, UNN Medical Centre, Student ID card.\n"
        "• **Facilities & Study**: Library card, campus Wi-Fi, Franco Refectory, photocopying.\n"
        "• **Grading**: CGPA calculation formula, 5-point grading scale, exam rules.\n\n"
        "Try asking: *'How do I do clearance?'* or *'How is CGPA calculated?'*"
    )
