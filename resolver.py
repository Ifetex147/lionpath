from thefuzz import fuzz
from models import Node, Event, Timetable
import re


def check_location_ambiguity(text):
    """
    Detects if the user query ambiguously refers to:
    - 'library': Faculty Library vs Nnamdi Azikiwe Library (Main Library)
    - 'canteen' / 'cafeteria': Faculty Science Canteen vs Franco Refectory
    Returns 'AMBIGUOUS_LIBRARY', 'AMBIGUOUS_CANTEEN', or None.
    """
    if not text:
        return None
    clean = text.lower().strip()

    # If the user is asking an orientation/registration/card question, do NOT trigger location ambiguity
    if re.search(r"\b(card|cards|register|registration|fee|fees|how to|requirements|documents|open|hours)\b", clean):
        return None

    # Library check
    if re.search(r"\b(library|lib|the library|libraries)\b", clean):
        has_faculty = bool(re.search(r"\b(faculty|science|physical)\b", clean))
        has_main = bool(re.search(r"\b(nnamdi|azikiwe|na\b|nal\b|main|central|university)\b", clean))
        if has_faculty and not has_main:
            return None
        if has_main and not has_faculty:
            return None
        return "AMBIGUOUS_LIBRARY"

    # Canteen / Food check
    if re.search(r"\b(canteen|cafeteria|buka|mama put|dining|refectory)\b", clean):
        has_science = bool(re.search(r"\b(faculty|science|slt)\b", clean))
        has_franco = bool(re.search(r"\b(franco|refectory|main)\b", clean))
        if has_science and not has_franco:
            return None
        if has_franco and not has_science:
            return None
        return "AMBIGUOUS_CANTEEN"

    return None


def resolve_disambiguated_location(choice_text, ambiguity_type):
    """
    Resolves the chosen landmark from the user's clarification.
    """
    c = choice_text.lower().strip()
    if ambiguity_type == "AMBIGUOUS_LIBRARY":
        if re.search(r"\b(faculty|science|physical|first|1)\b", c):
            return Node.query.filter(Node.formal_name.like("%Faculty%Library%")).first()
        if re.search(r"\b(main|nnamdi|azikiwe|na\b|nal\b|central|university|second|2)\b", c):
            return Node.query.filter(Node.formal_name.like("%Nnamdi Azikiwe Library%")).first()
        return None

    if ambiguity_type == "AMBIGUOUS_CANTEEN":
        if re.search(r"\b(faculty|science|slt|first|1)\b", c):
            return Node.query.filter(Node.formal_name.like("%Science Canteen%")).first()
        if re.search(r"\b(franco|main|refectory|second|2)\b", c):
            return Node.query.filter(Node.formal_name.like("%Franco Refectory%")).first() or Node.query.filter(Node.formal_name.like("%Canteen%")).first()
        return None

    return None


def _normalize_ordinals(s):
    if not s:
        return ""
    # Normalize 1st <-> first, 2nd <-> second, 3rd <-> third
    s = re.sub(r"\b1st\b", "first", s, flags=re.IGNORECASE)
    s = re.sub(r"\b2nd\b", "second", s, flags=re.IGNORECASE)
    s = re.sub(r"\b3rd\b", "third", s, flags=re.IGNORECASE)
    return s


def resolve_location(text):
    """
    Intelligently matches user input text to a physical campus landmark (Node)
    using exact matches and fuzzy Token-Set + Token-Sort ratio scoring with
    ordinal discrimination guards.
    Returns None if the query is an ambiguous umbrella term (e.g., 'library' or 'canteen').
    """
    if not text:
        return None

    query_text = text.lower().strip()

    # Do not silently guess if the user gave an ambiguous term without qualification
    if check_location_ambiguity(query_text):
        return None

    # Do not treat procedural or FAQ questions as physical landmark locations
    if re.search(r"\b(how to|how do|how can|what do i need|requirements?|documents?|register|registration|id card|library card|fee|fees|cost|procedure|process)\b", query_text):
        return None

    # Generic contextual references (e.g. "the class", "class", "the lecture", "venue") should NOT match physical buildings
    if re.match(r"^(the\s+)?(class|lecture|venue|room|hall|place|building|spot)$", query_text) or re.match(r"^(there|it|that place|this place)$", query_text):
        return None

    clean = re.sub(r"\b(to|the|at|from|towards|building|block|department|hall|centre|center)\b", "", query_text).strip()
    clean = re.sub(r"\s+", " ", clean)

    query_norm = _normalize_ordinals(query_text)
    clean_norm = _normalize_ordinals(clean)

    nodes = Node.query.all()
    # Exact match lookup
    for node in nodes:
        candidates = [node.formal_name] + (node.informal_names or "").split(",")
        for candidate in candidates:
            c = candidate.strip().lower()
            if not c:
                continue
            if c == query_text or c == clean:
                return node
            c_norm = _normalize_ordinals(c)
            if c_norm and (c_norm == query_norm or c_norm == clean_norm):
                return node

    # Fuzzy match lookup using token set and sort ratios
    best_node = None
    best_score = 0

    has_ord1_q = bool(re.search(r"\b(1st|first)\b", query_text))
    has_ord2_q = bool(re.search(r"\b(2nd|second)\b", query_text))

    for node in nodes:
        candidates = [node.formal_name] + (node.informal_names or "").split(",")
        node_has_ord1 = bool(re.search(r"\b(1st|first)\b", node.formal_name.lower()))
        node_has_ord2 = bool(re.search(r"\b(2nd|second)\b", node.formal_name.lower()))

        for candidate in candidates:
            c = candidate.strip().lower()
            if not c:
                continue

            c_has_ord1 = node_has_ord1 or bool(re.search(r"\b(1st|first)\b", c))
            c_has_ord2 = node_has_ord2 or bool(re.search(r"\b(2nd|second)\b", c))

            # Cross-ordinal mismatch guard (prevents 1st Gate matching 2nd Gate queries and vice versa)
            if (has_ord1_q and c_has_ord2) or (has_ord2_q and c_has_ord1):
                continue

            c_norm = _normalize_ordinals(c)

            set_score = max(
                fuzz.token_set_ratio(query_text, c),
                fuzz.token_set_ratio(clean, c),
                fuzz.token_set_ratio(query_norm, c_norm),
                fuzz.token_set_ratio(clean_norm, c_norm)
            )
            sort_score = max(
                fuzz.token_sort_ratio(query_text, c),
                fuzz.token_sort_ratio(clean, c),
                fuzz.token_sort_ratio(query_norm, c_norm),
                fuzz.token_sort_ratio(clean_norm, c_norm)
            )
            score = (set_score * 0.5) + (sort_score * 0.5)

            if score > best_score:
                best_score = score
                best_node = node

    if best_score >= 70:
        return best_node
    return None


def resolve_event_venue(text):
    """
    Checks if the user's query refers to a known campus event title,
    and returns (event_model, physical_venue_node).
    """
    if not text:
        return None, None

    clean = text.lower().strip()

    # Require an explicit event signal keyword unless the title matches directly
    has_event_signal = bool(re.search(
        r"\b(event|events|programme|programmes|ceremony|ceremonies|orientation|matriculation|matric|freshers\s+meeting|freshers\s+meetings|symposium|seminar|colloquium)\b",
        clean
    ))

    clean_query = re.sub(
        r"\b(where\s+(?:does|is|will|do|can\s+we)|takes?\s+place|hold|held|holding|"
        r"how\s+(?:do\s+i|can\s+i|to)\s+(?:get\s+to|reach|attend|find|go\s+to)|"
        r"directions?\s+(?:to)?|route\s+(?:to)?|the|event|programme|ceremony|address)\b",
        "",
        clean
    ).strip()
    clean_query = re.sub(r"\s+", " ", clean_query)

    best_event = None
    best_score = 0

    events = Event.query.all()
    for ev in events:
        title_lower = ev.title.lower()
        if title_lower in clean or clean in title_lower:
            best_event = ev
            best_score = 100
            break

        if has_event_signal:
            score = max(fuzz.token_set_ratio(clean, title_lower), fuzz.token_set_ratio(clean_query, title_lower))
            if score > best_score:
                best_score = score
                best_event = ev

    if best_event and best_score >= 60:
        venue_node = resolve_location(best_event.venue)
        if not venue_node and "ekpo" in best_event.venue.lower():
            venue_node = Node.query.filter(Node.formal_name.like("%Student Affairs%")).first()
        return best_event, venue_node

    return None, None


def resolve_course_venue(text):
    """
    Checks if the user's query refers to a class/course code (e.g. 'COS 101', 'MTH 101', 'Physics 115'),
    and resolves the lecture venue Node.
    Returns (timetable_entry, physical_venue_node).
    """
    if not text:
        return None, None

    clean = text.lower().strip()
    match = re.search(r"\b(cos|csc|mth|mat|phy|sta|chm|geo|glg|gs|gsp|bio|slt|glt)\s*(\d{3})\b", clean)
    if match:
        prefix = match.group(1).upper()
        num = match.group(2)
        code = f"{prefix} {num}"
        target_prefixes = [prefix]
        if prefix in ["MTH", "MAT"]:
            target_prefixes = ["MTH", "MAT"]
        elif prefix in ["COS", "CSC"]:
            target_prefixes = ["COS", "CSC"]
        elif prefix in ["GLG", "GEO"]:
            target_prefixes = ["GLG", "GEO"]
        elif prefix in ["SLT", "GLT"]:
            target_prefixes = ["SLT", "GLT"]
        elif prefix in ["GSP", "GS"]:
            target_prefixes = ["GSP", "GS"]

        for p in target_prefixes:
            tt = Timetable.query.filter(
                Timetable.course_code.ilike(f"{p} {num}%") |
                Timetable.course_code.ilike(f"{p}{num}%")
            ).first()
            if tt:
                venue_node = resolve_location(tt.venue)
                return tt, venue_node

    # Also check full subject names with 3-digit number (e.g. "physics 115", "computer science 101", "maths 111")
    num_match = re.search(r"\b(\d{3})\b", clean)
    if num_match:
        num = num_match.group(1)
        subject_map = {
            r"\b(computer science|cs|cos|csc)\b": ["COS", "CSC"],
            r"\b(mathematics|maths|math|mth|mat)\b": ["MTH", "MAT"],
            r"\b(physics|phy)\b": ["PHY"],
            r"\b(chemistry|chem|chm)\b": ["CHM"],
            r"\b(statistics|stats|sta)\b": ["STA"],
            r"\b(geology|glg|geo)\b": ["GLG", "GEO"],
            r"\b(science laboratory technology|slt|glt)\b": ["SLT", "GLT"],
            r"\b(general studies|use of english|gsp|gs)\b": ["GSP", "GS"],
        }
        for pat, prefixes in subject_map.items():
            if re.search(pat, clean):
                for p in prefixes:
                    tt = Timetable.query.filter(
                        Timetable.course_code.ilike(f"{p} {num}%") |
                        Timetable.course_code.ilike(f"{p}{num}%")
                    ).first()
                    if tt:
                        venue_node = resolve_location(tt.venue)
                        return tt, venue_node

    return None, None


def resolve_target_venue(text):
    """
    Resolves text to a physical campus landmark Node, checking:
    1. Direct physical location match via resolve_location()
    2. Course lecture venue via resolve_course_venue()
    3. Event venue via resolve_event_venue()
    Returns Node or None.
    """
    if not text:
        return None
    # 1. Direct physical location
    loc = resolve_location(text)
    if loc:
        return loc
    # 2. Course lecture venue
    _, c_venue = resolve_course_venue(text)
    if c_venue:
        return c_venue
    # 3. Event venue
    _, e_venue = resolve_event_venue(text)
    if e_venue:
        return e_venue
    return None
