from models import Timetable, Event
import re
from datetime import datetime

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Domain dictionary linking departments, subjects, colloquial terms, and official course codes
SUBJECT_MAP = {
    "mathematics": {
        "codes": ["MTH", "MAT"],
        "aliases": ["mathematics", "maths", "math", "calculus", "algebra", "mth", "mat"],
        "display_name": "Mathematics (MTH)"
    },
    "computer_science": {
        "codes": ["COS", "CSC"],
        "aliases": ["computer science", "comp sci", "compsci", "computing", "programming", "software", "cos", "csc"],
        "display_name": "Computer Science (COS)"
    },
    "physics": {
        "codes": ["PHY"],
        "aliases": ["physics", "astronomy", "optics", "mechanics", "phy"],
        "display_name": "Physics (PHY)"
    },
    "statistics": {
        "codes": ["STA"],
        "aliases": ["statistics", "stats", "probability", "inference", "sta"],
        "display_name": "Statistics (STA)"
    },
    "chemistry": {
        "codes": ["CHM"],
        "aliases": ["chemistry", "chem", "chm"],
        "display_name": "Chemistry (CHM)"
    },
    "general_studies": {
        "codes": ["GSP", "GS"],
        "aliases": ["general studies", "gen studies", "use of english", "gsp", "gs", "gst"],
        "display_name": "General Studies (GSP)"
    },
    "geology": {
        "codes": ["GLG", "GEO"],
        "aliases": ["geology", "earth science", "geo", "glg"],
        "display_name": "Geology (GLG)"
    },
    "slt": {
        "codes": ["SLT", "GLT"],
        "aliases": ["science laboratory technology", "slt", "lab tech", "workshop technology", "glt"],
        "display_name": "Science Laboratory Technology (SLT)"
    }
}

# Department lookup map with order prioritizing compound names
DEPT_MAP = {
    "Computer Science & Statistics": [r"\b(computer science and statistics|computer and statistics|cs and stats|computer & statistics|cs\s*&\s*stats)\b"],
    "Computer Science": [r"\b(computer science|comp sci|compsci|cs\b|csc\b)"],
    "Statistics": [r"\b(statistics|stats|sta\b)"],
    "Geology": [r"\b(geology|earth science|geo\b|glg\b)"],
    "Science Laboratory Technology": [r"\b(science laboratory technology|science lab tech|slt\b|lab tech|glt\b)"],
    "Mathematics": [r"\b(mathematics|maths|math\b|mth\b|mat\b)"],
    "Physics & Astronomy": [r"\b(physics & astronomy|physics and astronomy|physics|astronomy|phy\b|ast\b)"],
    "Pure & Industrial Chemistry": [r"\b(pure & industrial chemistry|pure and industrial chemistry|industrial chemistry|chemistry|chem|chm\b|ich\b)"]
}


def resolve_department(text):
    """Identifies and returns the official department name from free-form text."""
    if not text:
        return None
    clean = text.lower().strip()
    for dept_name, patterns in DEPT_MAP.items():
        for pat in patterns:
            if re.search(pat, clean):
                return dept_name
    return None


def format_lecture(lec):
    title = f" ({lec.course_title})" if getattr(lec, "course_title", None) else ""
    return f"• **{lec.course_code}**{title}: {lec.day}s {lec.time} at *{lec.venue}*"


def deduplicate_lectures(lectures):
    """
    Deduplicates lecture records sharing identical course code, day, time, and venue,
    preventing identical multi-department rows from repeating in responses.
    """
    seen = set()
    unique = []
    for lec in lectures:
        key = (
            (lec.course_code or "").strip().upper(),
            (lec.day or "").strip().lower(),
            (lec.time or "").strip().lower(),
            (lec.venue or "").strip().lower()
        )
        if key not in seen:
            seen.add(key)
            unique.append(lec)
    return unique


def get_department_timetable(dept_name, specific_day=None):
    """
    Returns the formatted timetable for a specific department, optionally filtered by day.
    """
    lectures = Timetable.query.filter(Timetable.department.ilike(f"%{dept_name}%")).all()
    if not lectures:
        lectures = Timetable.query.filter(Timetable.department == "General").all()

    if specific_day:
        day_lectures = deduplicate_lectures([l for l in lectures if l.day.lower() == specific_day.lower()])
        if day_lectures:
            resp = f"📅 **100-Level {dept_name} Lectures on {specific_day.capitalize()}:**\n\n"
            for l in day_lectures:
                resp += f"• **{l.course_code}** ({l.course_title}): {l.time} at *{l.venue}*\n"
            return resp.strip()
        else:
            return f"There are no lectures scheduled for **{dept_name}** on **{specific_day.capitalize()}**."

    resp = f"📚 **100-Level {dept_name} First Semester Timetable:**\n\n"
    for day in DAYS_OF_WEEK:
        day_lectures = deduplicate_lectures([l for l in lectures if l.day.lower() == day.lower()])
        if day_lectures:
            resp += f"📅 **{day}:**\n"
            for l in day_lectures:
                resp += f"• **{l.course_code}** ({l.course_title}): {l.time} at *{l.venue}*\n"
            resp += "\n"
    return resp.strip()


def get_physics_timetable(text):
    """
    Intelligently handles disambiguation between Physics Theory (PHY 115) and Physics Practical (PHY 121 / PHY 191).
    """
    clean = text.lower().strip()
    is_practical = bool(re.search(r"\b(practical|practicals|lab|laboratory|191|121|pracs)\b", clean))
    is_theory = bool(re.search(r"\b(theory|lecture|lectures|auditorium|theatre|115|class)\b", clean))
    is_both = bool(re.search(r"\b(both|all|everything|two)\b", clean))

    if is_both:
        return (
            "📚 **Physics Complete Timetable (Theory & Practical):**\n\n"
            "• **PHY 115 (General Physics for Physical Sciences I - Theory)**:\n"
            "  - Fridays: 8:00 AM - 10:00 AM at *Faculty of Physical Sciences Lecture Theatre (FPSLT)*\n\n"
            "• **PHY 191 (Practical Physics I - Lab)**:\n"
            "  - Thursdays: 2:00 PM - 5:00 PM at *Abuja Building Laboratories*"
        )

    if is_practical:
        return (
            "🔬 **Timetable for Physics Practical (PHY 191):**\n"
            "• **Thursdays**: 2:00 PM - 5:00 PM at *Abuja Building Laboratories*\n\n"
            "📌 *Requirement: Remember to bring your Physics Lab Manual, white lab coat, and practical workbook.*"
        )

    if is_theory:
        return (
            "📚 **Timetable for Physics Theory (PHY 115 - General Physics I):**\n"
            "• **Fridays**: 8:00 AM - 10:00 AM at *Faculty of Physical Sciences Lecture Theatre (FPSLT)*"
        )

    # Ambiguous prompt where user didn't specify theory vs practical
    return "DISAMBIGUATE_PHYSICS"


def get_timetable(query_or_code=""):
    """
    Intelligently retrieves timetable information by department, course code,
    full subject name, or day of the week.
    """
    text = (query_or_code or "").lower().strip()

    # Detect day of the week if specified
    matched_day = None
    for day in DAYS_OF_WEEK:
        if re.search(rf"\b{day.lower()}\b", text):
            matched_day = day
            break

    # 0. Check for Department-wide Timetable (e.g., "Computer Science timetable", "Geology schedule", "Physics classes on Monday")
    dept_name = resolve_department(text)
    if dept_name:
        has_course_num = bool(re.search(r"\b\d{3}\b", text))
        if not has_course_num:
            return get_department_timetable(dept_name, matched_day)

    # 1. Day of the week lookup across all faculty classes (e.g. "Monday", "classes on Friday")
    if matched_day and not re.search(r"\b(mth|cos|phy|chm|sta|glg|slt|gsp)\b", text):
        lectures = Timetable.query.filter(Timetable.day.ilike(matched_day)).all()
        lectures = deduplicate_lectures(lectures)
        if lectures:
            resp = f"📅 **Lectures Scheduled for {matched_day.capitalize()}:**\n\n"
            for lec in lectures:
                resp += format_lecture(lec) + "\n"
            return resp.strip()
        return f"There are no lectures recorded in the timetable for {matched_day.capitalize()}."

    # 2. Extract potential course number (e.g. "101", "111", "115", "121", "141")
    number_match = re.search(r"\b(\d{3})\b", text)
    number = number_match.group(1) if number_match else None

    # 3. Check for Subject / Department alias
    matched_subject = None
    for subj_key, subj_info in SUBJECT_MAP.items():
        for alias in subj_info["aliases"]:
            if re.search(rf"\b{re.escape(alias)}\b", text):
                matched_subject = subj_info
                break
        if matched_subject:
            break

    # Special check for Physics: Disambiguate between Theory and Practical
    if (matched_subject and "PHY" in matched_subject["codes"]) or re.search(r"\b(physics|phy)\b", text):
        if not number:
            phy_res = get_physics_timetable(text)
            if phy_res:
                return phy_res

    # Case A: User specified both a Subject and a Course Number (e.g. "mathematics 111", "physics 115", "computer science 101", "cos 199")
    if matched_subject and number:
        matching_lectures = []
        for code_prefix in matched_subject["codes"]:
            lectures = Timetable.query.filter(
                Timetable.course_code.ilike(f"{code_prefix} {number}%") |
                Timetable.course_code.ilike(f"{code_prefix}{number}%")
            ).all()
            matching_lectures.extend(lectures)

        matching_lectures = deduplicate_lectures(matching_lectures)
        primary_prefix = matched_subject["codes"][0]
        course_tag = f"{primary_prefix} {number}"
        if matching_lectures:
            resp = f"📚 **Timetable for {course_tag}:**\n\n"
            for lec in matching_lectures:
                resp += format_lecture(lec) + "\n"
            return resp.strip()
        else:
            # Course number was requested but not found in this department
            available_lectures = []
            for code_prefix in matched_subject["codes"]:
                lectures = Timetable.query.filter(
                    Timetable.course_code.ilike(f"{code_prefix}%")
                ).all()
                available_lectures.extend(lectures)

            available_lectures = deduplicate_lectures(available_lectures)
            primary_prefix = matched_subject["codes"][0]
            code_label = f"{primary_prefix} {number}"

            if available_lectures:
                resp = f"**{code_label}** has not been scheduled or added to the 100-level timetable yet.\n\n"
                resp += f"📚 **Available {matched_subject['display_name']} Courses on the Timetable:**\n\n"
                for lec in available_lectures:
                    resp += format_lecture(lec) + "\n"
                return resp.strip()
            else:
                return f"**{code_label}** has not been scheduled or added to the timetable yet."

    # Case B: User specified a Subject alone (e.g. "when is mathematics lecture?", "computer science classes")
    if matched_subject:
        matching_lectures = []
        for code_prefix in matched_subject["codes"]:
            lectures = Timetable.query.filter(
                Timetable.course_code.ilike(f"{code_prefix}%")
            ).all()
            matching_lectures.extend(lectures)

        matching_lectures = deduplicate_lectures(matching_lectures)
        if matching_lectures:
            resp = f"📚 **Timetable for {matched_subject['display_name']}:**\n\n"
            for lec in matching_lectures:
                resp += format_lecture(lec) + "\n"
            return resp.strip()

    # Case C: Standard alphanumeric code (e.g. "COS 101", "MTH 111", "PHY 115", "GLG 111", "SLT 101")
    code_match = re.search(r"\b([a-zA-Z]{2,4})\s*(\d{3})\b", text)
    if code_match:
        raw_prefix = code_match.group(1).upper()
        num = code_match.group(2)

        # Normalize secondary codes to official primary standard for display
        if raw_prefix in ["COS", "CSC"]:
            prefix = "COS"
            target_prefixes = ["COS", "CSC"]
        elif raw_prefix in ["MTH", "MAT"]:
            prefix = "MTH"
            target_prefixes = ["MTH", "MAT"]
        elif raw_prefix in ["GLG", "GEO"]:
            prefix = "GLG"
            target_prefixes = ["GLG", "GEO"]
        elif raw_prefix in ["GSP", "GS"]:
            prefix = "GSP"
            target_prefixes = ["GSP", "GS"]
        elif raw_prefix in ["SLT", "GLT"]:
            prefix = "SLT"
            target_prefixes = ["SLT", "GLT"]
        elif raw_prefix in ["PHY"]:
            prefix = "PHY"
            target_prefixes = ["PHY"]
        elif raw_prefix in ["CHM", "ICH"]:
            prefix = "CHM"
            target_prefixes = ["CHM", "ICH"]
        elif raw_prefix in ["STA"]:
            prefix = "STA"
            target_prefixes = ["STA"]
        else:
            prefix = raw_prefix
            target_prefixes = [raw_prefix]

        code_upper = f"{prefix} {num}" 

        lectures = []
        for p in target_prefixes:
            res = Timetable.query.filter(
                Timetable.course_code.ilike(f"{p} {num}%") |
                Timetable.course_code.ilike(f"{p}{num}%")
            ).all()
            lectures.extend(res)

        lectures = deduplicate_lectures(lectures)
        if lectures:
            resp = f"📚 **Timetable for {code_upper}:**\n\n"
            for lec in lectures:
                resp += format_lecture(lec) + "\n"
            return resp.strip()
        else:
            any_for_prefix = []
            for p in target_prefixes:
                res = Timetable.query.filter(
                    Timetable.course_code.ilike(f"{p}%")
                ).all()
                any_for_prefix.extend(res)
            any_for_prefix = deduplicate_lectures(any_for_prefix)
            if any_for_prefix:
                resp = f"**{code_upper}** has not been scheduled or added to the 100-level timetable yet.\n\n"
                resp += f"📚 **Available {prefix} Courses on the Timetable:**\n\n"
                for lec in any_for_prefix:
                    resp += format_lecture(lec) + "\n"
                return resp.strip()
            else:
                return (
                    f"**{code_upper}** has not been scheduled or added to the 100-level timetable yet.\n\n"
                    "💡 *LionPath currently covers 100-level courses in the Faculty of Physical Sciences (Computer Science, Mathematics, Physics, Chemistry, Geology, Statistics, and SLT).*"
                )

    # 4. Clean Fallback Overview (Avoiding robotic query echo like "I couldn't find a timetable for 'what classes do i have'")
    clean_search = re.sub(
        r"\b(when is|what time is|where is|how about|tell me about|timetable for|schedule for|classes for|class for|lecture for|lectures for|is there|do we have|what classes? do (i|we) have|what are my classes|which classes? do (i|we) have|show me my classes|my classes|my timetable|my schedule)\b",
        "",
        text
    ).strip()

    if not clean_search:
        msg_header = "I couldn't find any scheduled lectures matching that inquiry."
    else:
        msg_header = f"I couldn't find any scheduled lectures matching **'{clean_search}'**."

    return (
        f"{msg_header}\n\n"
        "📚 **Faculty of Physical Sciences 100L Lecture Timetables**:\n"
        "• 💻 **Computer Science**: COS 101, COS 141\n"
        "• 📐 **Mathematics**: MTH 111, MTH 121, MTH 131\n"
        "• ⚛️ **Physics & Astronomy**: PHY 115 (Theory), PHY 191 (Practical), PHY 121, AST 101\n"
        "• 🧪 **Pure & Industrial Chemistry**: CHM 101, CHM 111, CHM 171, ICH 101\n"
        "• 🪨 **Geology**: GLG 111, GLG 141, GLG 171\n"
        "• 🔬 **Science Laboratory Technology (SLT)**: SLT 101, GLT 101\n"
        "• 📊 **Statistics**: STA 111, STA 131, STA 172\n"
        "• 📖 **General Studies**: GSP 101 (Use of English), GSP 111 (Library Skills)\n\n"
        "💡 *You can ask for your department's complete schedule (e.g. 'Computer Science timetable', 'Geology classes') or a specific course code (e.g. 'COS 101', 'MTH 111').*"
    )


def get_events():
    """Retrieves upcoming faculty and campus events."""
    events = Event.query.all()
    if not events:
        return "There are no upcoming faculty events scheduled at the moment."

    response = "🎉 **Upcoming Faculty & Campus Events:**\n"
    for ev in events:
        response += f"• **{ev.title}**\n  🕒 {ev.date_time} | 📍 *{ev.venue}*\n"
    return response
