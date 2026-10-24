with open('app.py', 'rb') as f:
    text = f.read().decode('utf-8')

norm = text.replace('\r\n', '\n')

# 1. Update imports
old_import = "from academics import get_timetable, get_events, get_physics_timetable"
new_import = "from academics import get_timetable, get_events, get_physics_timetable, get_department_timetable, resolve_department, DAYS_OF_WEEK\nfrom datetime import datetime"

assert old_import in norm, "old_import not found!"
norm = norm.replace(old_import, new_import, 1)

# 2. Add awaiting_user_department state handler right after awaiting_physics_type
old_physics_block = """    # --- PHYSICS DISAMBIGUATION CHECK ---
    if ctx.get("pending") == "awaiting_physics_type":
        phy_res = get_physics_timetable(clean_message)
        if phy_res and phy_res != "DISAMBIGUATE_PHYSICS":
            ctx["pending"] = None
            venue_match = re.search(r"\*(.*?)\*|\((.*?)\)", phy_res)
            if venue_match:
                v = venue_match.group(1) or venue_match.group(2)
                if v:
                    ctx["last_location"] = v.strip()
            return {"text": phy_res}
        elif re.search(r"\b(what|how|who|when|where|why|tell|hi|hello|cancel|nevermind)\b", clean_message):
            ctx["pending"] = None
        else:
            return {
                "text": "Are you asking about **Physics Theory (PHY 115)** or **Physics Practical (PHY 121)**? (You can say *'theory'*, *'practical'*, or *'both'*).",
                "options": ["PHY 115 Theory", "PHY 121 Practical", "Both Physics Classes"]
            }"""

new_physics_block = """    # --- PHYSICS DISAMBIGUATION CHECK ---
    if ctx.get("pending") == "awaiting_physics_type":
        phy_res = get_physics_timetable(clean_message)
        if phy_res and phy_res != "DISAMBIGUATE_PHYSICS":
            ctx["pending"] = None
            venue_match = re.search(r"\*(.*?)\*|\((.*?)\)", phy_res)
            if venue_match:
                v = venue_match.group(1) or venue_match.group(2)
                if v:
                    ctx["last_location"] = v.strip()
            return {"text": phy_res}
        elif re.search(r"\b(what|how|who|when|where|why|tell|hi|hello|cancel|nevermind)\b", clean_message):
            ctx["pending"] = None
        else:
            return {
                "text": "Are you asking about **Physics Theory (PHY 115)** or **Physics Practical (PHY 121)**? (You can say *'theory'*, *'practical'*, or *'both'*).",
                "options": ["PHY 115 Theory", "PHY 121 Practical", "Both Physics Classes"]
            }

    # --- DEPARTMENT TIMETABLE SELECTION CHECK ---
    if ctx.get("pending") == "awaiting_user_department":
        dept = resolve_department(clean_message)
        if dept:
            ctx["user_department"] = dept
            ctx["pending"] = None
            requested_day = ctx.pop("pending_timetable_day", None)
            tt = get_department_timetable(dept, requested_day)
            return {
                "text": f"🎓 **Saved your department as {dept}!**\\n\\n{tt}"
            }
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Department selection cancelled. How else can I assist you?"}
        elif re.search(r"\b(how do i|directions? to|where is|route to|clearance|hostel|medicals?|wifi|library card)\b", clean_message):
            ctx["pending"] = None
            # Allow to fall through as a new command/question
        else:
            return {
                "text": "Please choose your department in the Faculty of Physical Sciences to view your schedule:",
                "options": [
                    "Computer Science",
                    "Geology",
                    "Science Laboratory Technology",
                    "Mathematics",
                    "Physics & Astronomy",
                    "Pure & Industrial Chemistry",
                    "Statistics",
                    "Computer Science & Statistics"
                ]
            }"""

assert old_physics_block in norm, "old_physics_block not found!"
norm = norm.replace(old_physics_block, new_physics_block, 1)

# 3. Handle Timetable Trigger with personal inquiry check
old_tt_trigger = """    # 3. Direct Timetable Trigger ("timetable", "schedule", "classes", "lecture time", "what time is", "when is", course codes)
    if re.search(r"\b(timetable|schedule|classes|lectures?|what time is|when is|when do we have)\b", clean_message) or re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday)\b", clean_message) or re.search(r"\b(cos|csc|mth|mat|phy|sta|chm|gs|geo)\s*(\d{3})?\b", clean_message):
        reply_text = get_timetable(clean_message)"""

new_tt_trigger = """    # 3. Direct Timetable Trigger ("timetable", "schedule", "classes", "lecture time", "what time is", "when is", course codes)
    if re.search(r"\b(timetable|schedule|classes|lectures?|what time is|when is|when do we have)\b", clean_message) or re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday)\b", clean_message) or re.search(r"\b(cos|csc|mth|mat|phy|sta|chm|gs|gsp|geo|glg|slt|glt)\s*(\d{3})?\b", clean_message):
        # A. Check for Personal / Open-ended Inquiries ("what classes do I have", "my timetable", "my classes")
        personal_tt_match = re.search(r"\b(what classes? do (i|we) have|which classes? do (i|we) have|what are my classes|what lectures? do (i|we) have|my classes|my lectures|my timetable|my schedule|show (me )?my classes|what class(es)? do i have)\b", clean_message)
        if personal_tt_match:
            # Extract day if mentioned
            req_day = None
            for d in DAYS_OF_WEEK:
                if re.search(rf"\\b{d.lower()}\\b", clean_message):
                    req_day = d
                    break
            if "today" in clean_message:
                req_day = datetime.now().strftime("%A")

            # Check if department was also mentioned in this exact message
            dept_in_msg = resolve_department(clean_message)
            if dept_in_msg:
                ctx["user_department"] = dept_in_msg
                return {"text": get_department_timetable(dept_in_msg, req_day)}

            # If user already has a saved department in session
            if ctx.get("user_department"):
                return {"text": get_department_timetable(ctx["user_department"], req_day)}

            # Ask user for department with interactive pill buttons
            ctx["pending"] = "awaiting_user_department"
            ctx["pending_timetable_day"] = req_day
            return {
                "text": "Which department in the Faculty of Physical Sciences are you in? Please select your department to view your official 100-Level lecture schedule:",
                "options": [
                    "Computer Science",
                    "Geology",
                    "Science Laboratory Technology",
                    "Mathematics",
                    "Physics & Astronomy",
                    "Pure & Industrial Chemistry",
                    "Statistics",
                    "Computer Science & Statistics"
                ]
            }

        reply_text = get_timetable(clean_message)"""

assert old_tt_trigger in norm, "old_tt_trigger not found!"
norm = norm.replace(old_tt_trigger, new_tt_trigger, 1)

with open('app.py', 'wb') as f:
    f.write(norm.replace('\n', '\r\n').encode('utf-8'))

print("SUCCESS: app.py updated with smart department prompting and personal timetable handling!")

