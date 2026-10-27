from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import spacy
import re
from models import db, Node, Edge, OrientationKB, Timetable, Event, Admin
from navigation import get_directions
from resolver import resolve_location, check_location_ambiguity, resolve_disambiguated_location, resolve_event_venue, resolve_course_venue, resolve_target_venue
from orientation import answer_orientation
from academics import get_timetable, get_events, get_physics_timetable, get_department_timetable, resolve_department, DAYS_OF_WEEK
from datetime import datetime
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "lionpath-secret-key-change-in-prod")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///lionpath.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Image upload directory
app.config["UPLOAD_FOLDER"] = "static/images"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True) 
db.init_app(app)

nlp = spacy.load("lionpath_nlp")

# session_id -> {"pending": None or "awaiting_source", "destination": Node, "last_location": str}
contexts = {}


def handle_navigate(session_id, locations, clean_message):
    ctx = contexts[session_id]

    # Parse 'from X to Y' and 'to Y from X' route requests
    from_to = re.search(r"\bfrom\s+(.+?)\s+to\s+(.+)", clean_message)
    if from_to:
        src_raw = from_to.group(1).strip()
        dst_raw = from_to.group(2).strip()

        # Check source ambiguity
        src_ambig = check_location_ambiguity(src_raw)
        if src_ambig == "AMBIGUOUS_LIBRARY":
            dst = resolve_target_venue(dst_raw)
            if dst:
                ctx["destination"] = dst
                ctx["pending"] = "awaiting_library_source"
                return {
                    "text": f"Are you starting from the **Faculty of Physical Sciences Library** or the **Nnamdi Azikiwe Library (Main Library)** on your way to **{dst.formal_name}**?",
                    "options": ["Faculty Library", "Main Library (NAL)"]
                }
        elif src_ambig == "AMBIGUOUS_CANTEEN":
            dst = resolve_target_venue(dst_raw)
            if dst:
                ctx["destination"] = dst
                ctx["pending"] = "awaiting_canteen_source"
                return {
                    "text": f"Are you starting from the **Faculty Science Canteen** or **Franco Refectory** on your way to **{dst.formal_name}**?",
                    "options": ["Faculty Science Canteen", "Franco Refectory"]
                }

        # Check destination ambiguity
        dst_ambig = check_location_ambiguity(dst_raw)
        if dst_ambig == "AMBIGUOUS_LIBRARY":
            src = resolve_target_venue(src_raw)
            if src:
                ctx["source"] = src
                ctx["pending"] = "awaiting_library_destination_direct"
                return {
                    "text": "Are you heading to the **Faculty of Physical Sciences Library** or the **Nnamdi Azikiwe Library (Main Library)**?",
                    "options": ["Faculty Library", "Main Library (NAL)"]
                }
        elif dst_ambig == "AMBIGUOUS_CANTEEN":
            src = resolve_target_venue(src_raw)
            if src:
                ctx["source"] = src
                ctx["pending"] = "awaiting_canteen_destination_direct"
                return {
                    "text": "Are you heading to the **Faculty Science Canteen** or **Franco Refectory**?",
                    "options": ["Faculty Science Canteen", "Franco Refectory"]
                }

        src = resolve_target_venue(src_raw)
        dst = resolve_target_venue(dst_raw)
        if src and dst:
            return finish_route(session_id, src, dst)

    to_from = re.search(r"\bto\s+(.+?)\s+from\s+(.+)", clean_message)
    if to_from:
        dst_raw = to_from.group(1).strip()
        src_raw = to_from.group(2).strip()

        src_ambig = check_location_ambiguity(src_raw)
        if src_ambig == "AMBIGUOUS_LIBRARY":
            dst = resolve_target_venue(dst_raw)
            if dst:
                ctx["destination"] = dst
                ctx["pending"] = "awaiting_library_source"
                return {
                    "text": f"Are you starting from the **Faculty of Physical Sciences Library** or the **Nnamdi Azikiwe Library (Main Library)** on your way to **{dst.formal_name}**?",
                    "options": ["Faculty Library", "Main Library (NAL)"]
                }
        elif src_ambig == "AMBIGUOUS_CANTEEN":
            dst = resolve_target_venue(dst_raw)
            if dst:
                ctx["destination"] = dst
                ctx["pending"] = "awaiting_canteen_source"
                return {
                    "text": f"Are you starting from the **Faculty Science Canteen** or **Franco Refectory** on your way to **{dst.formal_name}**?",
                    "options": ["Faculty Science Canteen", "Franco Refectory"]
                }

        dst_ambig = check_location_ambiguity(dst_raw)
        if dst_ambig == "AMBIGUOUS_LIBRARY":
            src = resolve_target_venue(src_raw)
            if src:
                ctx["source"] = src
                ctx["pending"] = "awaiting_library_destination_direct"
                return {
                    "text": "Are you heading to the **Faculty of Physical Sciences Library** or the **Nnamdi Azikiwe Library (Main Library)**?",
                    "options": ["Faculty Library", "Main Library (NAL)"]
                }
        elif dst_ambig == "AMBIGUOUS_CANTEEN":
            src = resolve_target_venue(src_raw)
            if src:
                ctx["source"] = src
                ctx["pending"] = "awaiting_canteen_destination_direct"
                return {
                    "text": "Are you heading to the **Faculty Science Canteen** or **Franco Refectory**?",
                    "options": ["Faculty Science Canteen", "Franco Refectory"]
                }

        src = resolve_target_venue(src_raw)
        dst = resolve_target_venue(dst_raw)
        if src and dst:
            return finish_route(session_id, src, dst)

    # Check if query targets a Class/Course venue (e.g., "how goi go for the GSP 101 class?", "where is COS 101?")
    tt, tt_venue = resolve_course_venue(clean_message)
    if tt and tt_venue:
        ctx["pending"] = "awaiting_source"
        ctx["destination"] = tt_venue
        return {
            "text": f"📚 **{tt.course_code}** ({tt.course_title}) lectures take place at **{tt_venue.formal_name}** ({tt.day}s at {tt.time}).\n\nWhere are you starting from, on your way to **{tt_venue.formal_name}**? (e.g., from your hostel, a campus gate, or Carver Building)",
            "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
        }

    # Check if query targets an Event (e.g., "Dean's Matriculation Address to Freshmen event")
    ev, ev_venue = resolve_event_venue(clean_message)
    if ev:
        if ev_venue:
            ctx["pending"] = "awaiting_source"
            ctx["destination"] = ev_venue
            ctx["last_location"] = ev_venue.formal_name
            if "ekpo" in ev.venue.lower():
                text_msg = (
                    f"🎉 **{ev.title}** takes place at **{ev.venue}** ({ev.date_time}).\n\n"
                    f"• **Ekpo Ref**: Head up the hill past the **Student Affairs Building** (beside the statue of a woman's face).\n"
                    f"• **Departmental Sessions**: Held at your respective departmental lecture halls (NCSB, Carver, Abuja Building, Geology).\n\n"
                    f"Where are you starting from, on your way to **{ev_venue.formal_name}**?"
                )
            else:
                venue_display = f"**{ev_venue.formal_name}**" if ev.venue.lower() in ev_venue.formal_name.lower() or ev_venue.formal_name.lower() in ev.venue.lower() else f"**{ev.venue}** (at {ev_venue.formal_name})"
                text_msg = f"🎉 **{ev.title}** takes place at {venue_display} ({ev.date_time}).\n\nWhere are you starting from, on your way there?"
            return {
                "text": text_msg,
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }
        else:
            ctx["last_location"] = ev.venue
            return {
                "text": f"🎉 **{ev.title}** takes place at **{ev.venue}** ({ev.date_time}).\n\n(Note: This venue is situated outside the immediate Faculty of Physical Sciences walking graph)."
            }

    # Standalone ambiguity check (e.g., user just asked "where is library")
    ambig = check_location_ambiguity(clean_message)
    if ambig == "AMBIGUOUS_LIBRARY":
        ctx["pending"] = "awaiting_library_destination"
        return {
            "text": "Which library do you want directions to?\n"
                    "• 🏛️ **Faculty of Physical Sciences Library** (say *'faculty'*)\n"
                    "• 🏢 **Nnamdi Azikiwe Library (Main Library / NAL)** (say *'main'* or *'nal'*)",
            "options": ["Faculty Library", "Main Library (NAL)"]
        }
    elif ambig == "AMBIGUOUS_CANTEEN":
        ctx["pending"] = "awaiting_canteen_destination"
        return {
            "text": "Which spot do you want directions to?\n"
                    "• 🍲 **Faculty Science Canteen** (behind SLT)\n"
                    "• 🍽️ **Franco Refectory** (main campus dining)",
            "options": ["Faculty Science Canteen", "Franco Refectory"]
        }

    # Contextual memory
    if len(locations) == 0 and re.search(r"\b(there|it|the place|that place|this place)\b", clean_message):
        if ctx.get("destination"):
            target_dest = ctx["destination"]
            ctx["pending"] = "awaiting_source"
            return {
                "text": f"Where are you starting from, on your way to **{target_dest.formal_name}**?",
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }
        elif ctx.get("last_location"):
            locations.append(ctx["last_location"])
        else:
            return {"text": "I'm not exactly sure which place you mean. Could you name the specific building?"}

    if len(locations) >= 2:
        source = resolve_target_venue(locations[0])
        destination = resolve_target_venue(locations[1])
        if not source or not destination:
            return {"text": "I couldn't recognise one of those places on campus. Can you name them differently?"}
        return finish_route(session_id, source, destination)

    if len(locations) == 1:
        single_ambig = check_location_ambiguity(locations[0])
        if single_ambig == "AMBIGUOUS_LIBRARY":
            ctx["pending"] = "awaiting_library_destination"
            return {
                "text": "Which library do you want directions to?\n"
                        "• 🏛️ **Faculty of Physical Sciences Library** (say *'faculty'*)\n"
                        "• 🏢 **Nnamdi Azikiwe Library (Main Library / NAL)** (say *'main'* or *'nal'*)",
                "options": ["Faculty Library", "Main Library (NAL)"]
            }
        elif single_ambig == "AMBIGUOUS_CANTEEN":
            ctx["pending"] = "awaiting_canteen_destination"
            return {
                "text": "Which spot do you want directions to?\n"
                        "• 🍲 **Faculty Science Canteen** (behind SLT)\n"
                        "• 🍽️ **Franco Refectory** (main campus dining)",
                "options": ["Faculty Science Canteen", "Franco Refectory"]
            }

        destination = resolve_target_venue(locations[0])
        if not destination:
            destination = resolve_target_venue(clean_message)
        if not destination:
            return {"text": "I couldn't find that place on campus. Try another name for it?"}
        ctx["pending"] = "awaiting_source"
        ctx["destination"] = destination
        return {
            "text": f"Where are you starting from, on your way to **{destination.formal_name}**?",
            "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
        }

    if len(locations) == 0:
        cleaned_dest = re.sub(
            r"^(?:(?:campus\s+)?directions?\s+(?:to\s+)?|route\s+(?:to\s+)?|path\s+(?:to\s+)?|"
            r"how\s+(?:do\s+i|can\s+i|to|goi|i)\s+(?:get\s+to|go\s+to|go|reach|find|locate)\s+(?:to\s+)?|"
            r"where\s+(?:is|can\s+i\s+find|are)\s+(?:the\s+)?|"
            r"take\s+me\s+to\s+|navigate\s+to\s+|lead\s+me\s+to\s+|way\s+to\s+)",
            "",
            clean_message
        ).strip()

        cand_ambig = check_location_ambiguity(cleaned_dest)
        if cand_ambig == "AMBIGUOUS_LIBRARY":
            ctx["pending"] = "awaiting_library_destination"
            return {
                "text": "Which library do you want directions to?\n"
                        "• 🏛️ **Faculty of Physical Sciences Library** (say *'faculty'*)\n"
                        "• 🏢 **Nnamdi Azikiwe Library (Main Library / NAL)** (say *'main'* or *'nal'*)",
                "options": ["Faculty Library", "Main Library (NAL)"]
            }
        elif cand_ambig == "AMBIGUOUS_CANTEEN":
            ctx["pending"] = "awaiting_canteen_destination"
            return {
                "text": "Which spot do you want directions to?\n"
                        "• 🍲 **Faculty Science Canteen** (behind SLT)\n"
                        "• 🍽️ **Franco Refectory** (main campus dining)",
                "options": ["Faculty Science Canteen", "Franco Refectory"]
            }

        destination = resolve_target_venue(cleaned_dest) if cleaned_dest else None
        if not destination:
            destination = resolve_target_venue(clean_message)
        if destination:
            ctx["pending"] = "awaiting_source"
            ctx["destination"] = destination
            return {
                "text": f"Where are you starting from, on your way to **{destination.formal_name}**?",
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }

    return {"text": "Which place on campus do you want directions to? (e.g., *'Directions to SLT'* or *'From CS to Library'*)"}

def finish_route(session_id, source, destination):
    ctx = contexts[session_id]
    ctx["pending"] = None

    # Save this destination as the last known location for future context
    ctx["last_location"] = destination.formal_name

    directions_text, route_nodes, total_dist, est_mins, steps_data = get_directions(
        source.formal_name, destination.formal_name, return_route_data=True
    )

    return {
        "text": directions_text,
        "image": destination.photo_path,
        "route_nodes": route_nodes,
        "total_distance": total_dist,
        "est_mins": est_mins,
        "steps": steps_data,
        "source_name": source.formal_name,
        "destination_name": destination.formal_name
    }


def handle_general_chat(clean_message, session_id=None):
    msg = clean_message.strip().lower()
    ctx = contexts.get(session_id, {}) if session_id else {}

    # User name and identity
    if re.search(r"\b(what is my name|who am i|do you know my name|what'?s my name)\b", msg):
        user_name = ctx.get("user_name")
        if user_name:
            return {
                "text": f"Your name is **{user_name}**! 😊 What can I help you with around campus today?",
                "options": ["Campus Directions", "Lecture Schedules", "Orientation FAQs", "How is CGPA calculated?"]
            }
        else:
            if ctx:
                ctx["pending"] = "awaiting_user_name"
            return {
                "text": "I don't know your name yet! What should I call you?"
            }

    name_match = re.search(r"\b(my name is|i am called|call me)\s+([a-zA-Z]+)\b", msg)
    if name_match and not re.search(r"\b(lost|looking|going|heading|a student|new)\b", msg):
        name = name_match.group(2).capitalize()
        if ctx:
            ctx["user_name"] = name
            ctx["pending"] = None
        return {
            "text": f"Nice to meet you, **{name}**! 👋 I am LionPath, your campus guide for the Faculty of Physical Sciences. How can I assist you today?",
            "options": ["Campus Directions", "Lecture Schedules", "Orientation FAQs", "How is CGPA calculated?"]
        }

    # Date and time responses
    if re.search(r"\b(today'?s\s+date|what\s+is\s+(the\s+)?date|what\s+is\s+todays?\s+date|date\s+today|what\s+date\s+is\s+it)\b", msg):
        now = datetime.now()
        return {
            "text": f"📅 Today is **{now.strftime('%A, %B %d, %Y')}**.\n\n"
                    f"💡 *Tip: If you're looking for lectures scheduled for today, you can ask 'What classes do I have today?'*"
        }

    if re.search(r"\b(what\s+time\s+is\s+it|current\s+time|the\s+time\s+now|time\s+is\s+it)\b", msg):
        now = datetime.now()
        return {
            "text": f"🕒 The current time is **{now.strftime('%I:%M %p')}** ({now.strftime('%A')})."
        }

    if re.search(r"\b(what\s+day\s+is\s+today|what\s+day\s+is\s+it|which\s+day\s+is\s+today)\b", msg):
        now = datetime.now()
        return {
            "text": f"📅 Today is **{now.strftime('%A')}**, {now.strftime('%B %d, %Y')}."
        }

    # Greetings
    if re.search(r"\b(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|good\s+day|howdy|greetings)\b", msg):
        greeting_prefix = "Hello"
        if "good morning" in msg:
            greeting_prefix = "Good morning"
        elif "good afternoon" in msg:
            greeting_prefix = "Good afternoon"
        elif "good evening" in msg:
            greeting_prefix = "Good evening"
        elif "good day" in msg:
            greeting_prefix = "Good day"

        return {
            "text": f"{greeting_prefix}! I'm **LionPath**, your campus assistant for the Faculty of Physical Sciences, UNN.\n\n"
                    "Here are things you can ask me:\n"
                    "• 🗺️ **Directions**: *'How do I get to Science Lecture Theatre from CS?'*\n"
                    "• 🕒 **Timetables**: *'What time is COS 101?'* or *'Classes on Monday'*\n"
                    "• 📚 **Orientation**: *'How do I pay acceptance fee?'*, *'Clearance documents'*, *'Hostel steps'*\n"
                    "• 🎓 **Grading**: *'How is CGPA calculated?'* or *'5-point grading scale'*\n"
                    "• 🎉 **Events**: *'What events are happening?'*\n\n"
                    "What would you like to know?",
            "options": ["Campus Directions", "Lecture Schedules", "Orientation FAQs", "How is CGPA calculated?"]
        }

    # Help and capabilities
    if re.search(r"\b(what can you do|help|capabilities|how does this work|features|commands|what do you know)\b", msg):
        return {
            "text": "Here is everything I can help you with:\n\n"
                    "1. 📍 **Campus Navigation**: Turn-by-turn walking directions between 16 faculty landmarks, libraries, theatres, and cafeterias.\n"
                    "2. 🕒 **Lecture Timetables**: Complete schedule for 100-level courses (COS 101, MTH 101, PHY 115, STA 111, GS 101, etc.) or lookups by day.\n"
                    "3. 📚 **Orientation & Clearances**: Detailed guidance on school fees, Remita RRR generation, faculty clearance files, ID cards, and hostel applications.\n"
                    "4. 🎓 **Academics & CGPA**: UNN's 5.0 grading scale, degree classifications, and semester GPA calculation formulas.\n"
                    "5. 🏛️ **Campus Living**: Medical registration at UNN Health Centre, library borrower cards, Wi-Fi setup, and dining spots (Franco, Science Canteen).\n\n"
                    "Try asking: *'How do I do clearance?'* or *'Where is Carver Building?'*"
        }

    # About LionPath
    if re.search(r"\b(who are you|what is your name|who made you|who created you|project|about you)\b", msg):
        return {
            "text": "I am **LionPath**, an intelligent campus guide and assistant built for the Faculty of Physical Sciences at the University of Nigeria, Nsukka.\n\n"
                    "I was developed as a Final Year Project combining Graph Theory (Dijkstra's Shortest Path Algorithm), Natural Language Processing (spaCy), and relational campus data to support student orientation and micro-navigation."
        }

    # UNN overview and facts
    if re.search(r"\b(unn|university of nigeria|motto|history|vice chancellor|vc|nsukka)\b", msg):
        return {
            "text": "🏛️ **University of Nigeria, Nsukka (UNN)**:\n"
                    "• **Founded**: 1960 by Nigeria's first President, Dr. Nnamdi Azikiwe.\n"
                    "• **Motto**: *'To Restore the Dignity of Man'*\n"
                    "• **Colours**: Green and White (symbolizing agriculture and peace).\n"
                    "• **Campuses**: Nsukka (Main Campus), Enugu Campus (UNEC), and Ituku-Ozalla (Teaching Hospital/College of Medicine)."
        }

    # Freshers orientation tips
    if re.search(r"\b(advice|tips|freshers?|new student|survival|succeed)\b", msg):
        return {
            "text": "💡 **Key Advice for Freshers in Physical Sciences**:\n"
                    "1. **Attend all 100-level lectures from Day 1**: Courses like MTH 101 and COS 101 build fast.\n"
                    "2. **Protect your GPA in Year 1**: Building a high first-year CGPA provides a strong foundation.\n"
                    "3. **Never skip science practicals (PHY 121 / CHM Labs)**: Continuous assessment counts for 30-40%.\n"
                    "4. **Meet your Course Adviser early**: They sign your course forms and approve electives.\n"
                    "5. **Use campus study spaces**: Faculty Library and Nnamdi Azikiwe Library offer quiet revision zones."
        }

    # Conversational acknowledgments
    if re.search(r"^(ok|okay|k|alright|all right|got it|understood|noted|cool|sure|fine|great|nice|perfect|good(?!\s+(?:morning|afternoon|evening|day))|awesome|sounds good|yes|yeah|yep|no problem|no worries)\b", msg):
        return {
            "text": "Glad to help! 😊 Let me know if you need any other directions, lecture schedules, or campus info."
        }

    # Gratitude and farewells
    if re.search(r"\b(thank you|thanks|appreciated|bless you|good job)\b", msg):
        return {
            "text": "You're very welcome! Feel free to ask anytime you need directions, timetables, or campus guidance around UNN."
        }

    if re.search(r"\b(bye|goodbye|see you|later|good night)\b", msg):
        return {
            "text": "Goodbye! Have a great time on campus. LionPath is always here whenever you need assistance."
        }

    # Check if input matches location or orientation before fallback
    resolved_loc = resolve_location(msg)
    if resolved_loc:
        return {
            "text": f"Did you want directions to **{resolved_loc.formal_name}**? Where are you starting from?"
        }

    orientation_answer = answer_orientation(msg, threshold=50)
    if "I couldn't find an exact match" not in orientation_answer:
        return {"text": orientation_answer}

    # Default fallback response
    return {
        "text": "I'm not completely sure about that. I specialize in:\n"
                "• 🗺️ **Campus Directions**: *'How do I get to SLT?'* or *'Where is Carver Building?'*\n"
                "• 🕒 **Lecture Schedules**: *'What time is COS 101?'* or *'Classes on Monday'*\n"
                "• 📚 **Orientation FAQs**: *'Steps for fees'*, *'Clearance documents'*, *'Hostel room'*, *'ID card capture'*\n"
                "• 🎓 **Grading**: *'How is CGPA calculated?'*\n\n"
                "Try rephrasing your question or picking one of the topics above!"
    }


def handle_message(message, session_id):
    if session_id not in contexts:
        contexts[session_id] = {"pending": None, "destination": None, "last_location": None}
    ctx = contexts[session_id]

    clean_message = re.sub(r"[\U00010000-\U0010ffff]", "", message).strip()
    clean_message = re.sub(r"^[^\w\s]+", "", clean_message).strip().lower()
    clean_message = re.sub(r"\s+", " ", clean_message)
    if not clean_message:
        clean_message = message.lower().strip()
    clean_message = re.sub(r"doi", "do i", clean_message)
    clean_message = re.sub(r"dowe", "do we", clean_message)

    # Physics theory vs practical disambiguation
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

    # Department selection for lecture schedules
    if ctx.get("pending") == "awaiting_user_department":
        dept = resolve_department(clean_message)
        if dept:
            ctx["user_department"] = dept
            ctx["pending"] = None
            requested_day = ctx.pop("pending_timetable_day", None)
            tt = get_department_timetable(dept, requested_day)
            return {
                "text": f"🎓 **Official 100-Level Lecture Schedule for {dept}**:\n\n{tt}\n\n💡 *Need directions to any of your lecture venues? Just ask, e.g. 'Directions to Abuja Building' or 'Where is FPSLT?'*"
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
            }

    # Location disambiguation states
    if ctx.get("pending") == "awaiting_library_source":
        target = resolve_disambiguated_location(clean_message, "AMBIGUOUS_LIBRARY")
        if target:
            return finish_route(session_id, target, ctx["destination"])
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Route request cancelled. What else would you like assistance with?"}
        else:
            return {
                "text": "Please clarify which library:\n• 🏛️ **Faculty of Physical Sciences Library** (say *'faculty'*)\n• 🏢 **Nnamdi Azikiwe Library** (say *'main'* or *'nal'*)",
                "options": ["Faculty Library", "Main Library (NAL)"]
            }

    if ctx.get("pending") == "awaiting_canteen_source":
        target = resolve_disambiguated_location(clean_message, "AMBIGUOUS_CANTEEN")
        if target:
            return finish_route(session_id, target, ctx["destination"])
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Route request cancelled. What else would you like assistance with?"}
        else:
            return {
                "text": "Please clarify which spot:\n• 🍲 **Faculty Science Canteen** (say *'faculty'*)\n• 🍽️ **Franco Refectory** (say *'franco'*)",
                "options": ["Faculty Science Canteen", "Franco Refectory"]
            }

    if ctx.get("pending") == "awaiting_library_destination":
        target = resolve_disambiguated_location(clean_message, "AMBIGUOUS_LIBRARY")
        if target:
            ctx["destination"] = target
            ctx["pending"] = "awaiting_source"
            return {
                "text": f"Where are you starting from, on your way to **{target.formal_name}**?"
            }
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Route request cancelled. What else would you like assistance with?"}
        else:
            return {
                "text": "Which library do you want directions to?\n• 🏛️ **Faculty of Physical Sciences Library** (say *'faculty'*)\n• 🏢 **Nnamdi Azikiwe Library** (say *'main'* or *'nal'*)"
            }

    if ctx.get("pending") == "awaiting_canteen_destination":
        target = resolve_disambiguated_location(clean_message, "AMBIGUOUS_CANTEEN")
        if target:
            ctx["destination"] = target
            ctx["pending"] = "awaiting_source"
            return {
                "text": f"Where are you starting from, on your way to **{target.formal_name}**?"
            }
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Route request cancelled. What else would you like assistance with?"}
        else:
            return {
                "text": "Which spot do you want directions to?\n• 🍲 **Faculty Science Canteen** (say *'faculty'*)\n• 🍽️ **Franco Refectory** (say *'franco'*)"
            }

    if ctx.get("pending") == "awaiting_library_destination_direct":
        target = resolve_disambiguated_location(clean_message, "AMBIGUOUS_LIBRARY")
        if target:
            return finish_route(session_id, ctx["source"], target)
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Route request cancelled. What else would you like assistance with?"}
        else:
            return {
                "text": "Are you heading to the **Faculty of Physical Sciences Library** or the **Nnamdi Azikiwe Library (Main Library)**?"
            }

    if ctx.get("pending") == "awaiting_destination":
        target = resolve_target_venue(clean_message)
        if target:
            ctx["destination"] = target
            ctx["pending"] = "awaiting_source"
            return {
                "text": f"Where are you starting from, on your way to **{target.formal_name}**?",
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }
        else:
            return {
                "text": f"I couldn't find '{clean_message}' on campus. What is the nearest building or lecture theatre you're heading to?",
                "options": ["Carver Building", "Faculty Library", "Science Lecture Theatre (FPSLT)", "General Studies Building (GS Building)"]
            }

    if ctx.get("pending") == "awaiting_user_name":
        if not re.search(r"\b(what|how|why|when|where|who|cancel|no|stop|help)\b", clean_message):
            clean_name = re.sub(r"^(my name is|i am|call me)\s+", "", clean_message, flags=re.IGNORECASE).strip()
            name = clean_name.split()[0].capitalize()
            ctx["user_name"] = name
            ctx["pending"] = None
            return {
                "text": f"Nice to meet you, **{name}**! 👋 I am LionPath, your campus guide for the Faculty of Physical Sciences.\n\nWhat would you like to know or find on campus?",
                "options": ["Campus Directions", "Lecture Schedules", "Orientation FAQs", "How is CGPA calculated?"]
            }
        else:
            ctx["pending"] = None

    if ctx.get("pending") == "awaiting_canteen_destination_direct":
        target = resolve_disambiguated_location(clean_message, "AMBIGUOUS_CANTEEN")
        if target:
            return finish_route(session_id, ctx["source"], target)
        elif re.search(r"\b(cancel|stop|nevermind|back)\b", clean_message):
            ctx["pending"] = None
            return {"text": "Route request cancelled. What else would you like assistance with?"}
        else:
            return {
                "text": "Are you heading to the **Faculty Science Canteen** or **Franco Refectory**?"
            }

    # Handle responses when awaiting starting location:
    if ctx["pending"] == "awaiting_source":
        # Check for ambiguous location terms
        ambig = check_location_ambiguity(clean_message)
        if ambig == "AMBIGUOUS_LIBRARY":
            ctx["pending"] = "awaiting_library_source"
            return {
                "text": "Are you starting from the **Faculty of Physical Sciences Library** or the **Nnamdi Azikiwe Library (Main Library)**?",
                "options": ["Faculty Library", "Main Library (NAL)"]
            }
        elif ambig == "AMBIGUOUS_CANTEEN":
            ctx["pending"] = "awaiting_canteen_source"
            return {
                "text": "Are you starting from the **Faculty Science Canteen** (behind SLT) or **Franco Refectory** (main campus dining)?",
                "options": ["Faculty Science Canteen", "Franco Refectory"]
            }
        
        # If user repeats inquiry about getting there without providing a source
        if re.search(r"\b(how\s+(?:do\s+i|to|can\s+i)\s+(?:get|reach|go)\s+there|give\s+directions|directions?\s+(?:to\s+get\s+there|please)?|take\s+me\s+there|how\s+do\s+i\s+get|take\s+me)\b", clean_message) or re.search(r"^\s*(there|it)\s*$", clean_message):
            dest_name = ctx["destination"].formal_name if ctx.get("destination") else "your destination"
            return {
                "text": f"To guide you to **{dest_name}**, where are you currently starting from on campus?",
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }

        # Check if input matches a valid campus landmark
        clean_src = re.sub(r"^(from|starting\s+from|i\s+am\s+at|am\s+at|at)\s+", "", clean_message).strip()
        source = resolve_location(clean_src) or resolve_location(clean_message)
        if source:
            return finish_route(session_id, source, ctx["destination"])

        # Check if user switched to another topic, event, course, orientation question, or cancellation
        topic_switch_pattern = (
            r"\b("
            r"what|how|who|when|where|why|tell|is\s+there|can\s+you|hi|hello|hey|help|advice|"
            r"orientation|matriculation|matric|freshers?|event|events|seminars?|symposium|"
            r"cgpa|grade|grading|gpa|fees?|charges?|remita|rrr|receipt|"
            r"card|cards|id\s+card|library\s+card|"
            r"timetables?|schedules?|class(?:es)?|lectures?|today|tomorrow|"
            r"cos|csc|mth|mat|phy|sta|chm|gs|gsp|geo|glg|slt|glt|\d{3}|"
            r"clearance|register|registration|admission|acceptance|"
            r"hostel|hostels|bedspace|accommodation|room|porter|"
            r"medicals?|clinic|doctor|health\s+centre|"
            r"wifi|wi-fi|clionet|internet|"
            r"cancel|stop|nevermind|back|reset|no"
            r")\b"
        )
        is_topic_switch = bool(re.search(topic_switch_pattern, clean_message))
        if not is_topic_switch:
            is_topic_switch = bool(resolve_target_venue(clean_message) or resolve_event_venue(clean_message)[0])

        if is_topic_switch:
            ctx["pending"] = None
            # Drop down to process as a fresh question or command!
        else:
            return {"text": f"I couldn't find '{message}' as a starting point on campus. What is the nearest building, hostel, or gate to start from?"}

    # Keyword routing
    # Greetings
    if re.search(r"^\s*(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|good\s+day|howdy|greetings)\b", clean_message):
        return handle_general_chat(clean_message, session_id)

    # Acknowledgments
    if re.search(r"^(ok|okay|k|alright|all right|got it|understood|noted|cool|sure|fine|great|nice|perfect|good(?!\s+(?:morning|afternoon|evening|day))|awesome|sounds good|yes|yeah|yep|no problem|no worries)\b", clean_message):
        return {
            "text": "Glad to help! 😊 Let me know if you need any other directions, lecture schedules, or campus info."
        }
    # Date, time, and university overview queries
    if re.search(r"\b(about unn|unn motto|history of unn|when was unn founded|who founded unn|motto of unn|tell me about unn|today'?s\s+date|what\s+is\s+(the\s+)?date|what\s+is\s+todays?\s+date|date\s+today|what\s+date\s+is\s+it|what\s+day\s+is\s+today|what\s+time\s+is\s+it|current\s+time)\b", clean_message):
        return handle_general_chat(clean_message, session_id)

    # Quick menu shortcuts
    if re.search(r"^\s*(campus\s+directions?|directions?|navigation|wayfinding)\s*$", clean_message):
        ctx["pending"] = "awaiting_destination"
        return {
            "text": "🗺️ **Campus Navigation & Wayfinding**:\n\n"
                    "Which place on campus do you want directions to? (e.g. *'Directions to SLT'*, *'From Carver to GS Building'*, or *'Where is NAL Library?'*)\n\n"
                    "You can also pick a popular destination below:",
            "options": ["Carver Building", "Faculty Library", "Science Lecture Theatre (FPSLT)", "General Studies Building (GS Building)", "UNN 1st Gate (Main Gate)"]
        }

    if re.search(r"^\s*(lecture\s+schedules?|class\s+schedules?|timetables?|classes)\s*$", clean_message):
        ctx["pending"] = "awaiting_user_department"
        return {
            "text": "📚 Which department in the Faculty of Physical Sciences are you in? Select your department to view your official 100-Level lecture schedule:",
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

    if re.search(r"^\s*(orientation\s+faqs?|orientation|faqs?|clearance\s+help)\s*$", clean_message):
        return {
            "text": "📚 **Freshmen Orientation & Registration Guides**:\n\nWhat procedure do you need help with?",
            "options": ["School Fees & Remita", "Faculty Clearance Requirements", "Hostel Allocation", "Library Card", "Medical Registration", "How is CGPA calculated?"]
        }

    # Procedural orientation inquiries (hostel booking, ID card, fees, clearance, registration, CGPA)
    orientation_action_pattern = (
        r"\b("
        r"how\s+(?:do\s+i|can\s+i|to|goi|i)\s+(?:get|complete|finish|apply|apply\s+for|obtain|pay|secure|register|open|boot)\s+(?:a\s+|an\s+|my\s+)?(hostel|bedspace|bed\s+space|accommodation|room|id\s+card|library\s+card|rrr|remita|fees?|receipt|school\s+fees?|clearance|registration|medicals?|wifi|clionet|admission)|"
        r"hostel\s+(?:allocation|booting|application|steps?|process|portal|accommodation)|"
        r"how\s+(?:is|to\s+calculate)\s+cgpa"
        r")\b"
    )
    if re.search(orientation_action_pattern, clean_message):
        return {"text": answer_orientation(clean_message)}

    # Direct single-word chip match for registration / clearance / hostel / cgpa
    if re.search(r"^\s*(registration|register|course\s+reg)\s*$", clean_message):
        return {"text": answer_orientation("registration")}
    if re.search(r"^\s*(hostel|accommodation|bedspace)\s*$", clean_message):
        return {"text": answer_orientation("hostel")}
    if re.search(r"^\s*(clearance\s+deadline|deadline)\s*$", clean_message):
        return {"text": answer_orientation("clearance deadline")}
    if re.search(r"^\s*(cgpa\s+scale|cgpa|grading)\s*$", clean_message):
        return {"text": answer_orientation("cgpa")}

    # Navigation queries
    nav_pattern = (
        r"\b("
        r"how\s+(?:do\s+i|can\s+i|to|goi|i)\s+(?:get\s+to|go\s+to|go|reach|find|locate|attend)|"
        r"how\s+goi\s+go|"
        r"go\s+(?:to|for)\s+(?:the\s+)?|"
        r"(?:campus\s+)?directions?|"
        r"navigation|"
        r"wayfinding|"
        r"from\s+.+?\s+to|"
        r"to\s+.+?\s+from|"
        r"where\s+(?:is|can\s+i\s+find|do\s+we\s+have|are|does)|"
        r"where\s+.+?\s+(?:hold|held|holding|take\s+place)|"
        r"venue\s+(?:for|of)|"
        r"route\s+to|"
        r"take\s+me\s+to|"
        r"path\s+to|"
        r"lead\s+me\s+to|"
        r"navigate\s+to|"
        r"way\s+to"
        r")\b"
    )
    if re.search(nav_pattern, clean_message):
        doc = nlp(clean_message)
        locations = [ent.text for ent in doc.ents if ent.label_ == "LOCATION"]
        return handle_navigate(session_id, locations, clean_message)

    # Standalone department timetable queries
    dept_standalone = resolve_department(clean_message)
    if dept_standalone:
        ctx["user_department"] = dept_standalone
        tt = get_department_timetable(dept_standalone)
        return {
            "text": f"🎓 **Official 100-Level Lecture Schedule for {dept_standalone}**:\n\n{tt}\n\n💡 *Need directions to any of your lecture venues? Just ask, e.g. 'Directions to Abuja Building' or 'Where is FPSLT?'*"
        }

    # Lecture timetable queries
    timetable_signal = (
        r"\b("
        r"timetables?|schedules?|class(?:es)?|lectures?|"
        r"what\s+time\s+is|when\s+is|when\s+do\s+we\s+have|"
        r"(?:what|which|any)\s+class|"
        r"(?:what|which)\s+lecture|"
        r"classes?\s+today|"
        r"class(?:es)?\s+for\s+today|"
        r"today'?s?\s+classes?"
        r")\b"
    )
    if ((re.search(timetable_signal, clean_message) and not re.search(r"\b(theatre|fpslt)\b", clean_message)) or re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday)\b", clean_message) or re.search(r"\b(cos|csc|mth|mat|phy|sta|chm|gs|gsp|geo|glg|slt|glt)\s*(\d{3})\b", clean_message)):
        # Personal timetable inquiries
        personal_tt_pattern = (
            r"\b("
            r"(?:what|which|show\s+me|show|any|do\s+(?:i|we)\s+have|are\s+there)\s+(?:any\s+)?(?:my\s+)?(?:class(?:es)?|lectures?|schedules?|timetables?)|"
            r"(?:what|which)\s+do\s+(?:i|we)\s+have|"
            r"my\s+(?:class(?:es)?|lectures?|schedules?|timetables?)|"
            r"(?:class(?:es)?|lectures?|schedules?|timetables?)\s+(?:for\s+)?(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday)|"
            r"(?:class(?:es)?|lectures?)\s+do\s+(?:i|we)\s+have"
            r")\b"
        )
        personal_tt_match = re.search(personal_tt_pattern, clean_message)
        if personal_tt_match:
            # Extract day if mentioned
            req_day = None
            for d in DAYS_OF_WEEK:
                if re.search(rf"\b{d.lower()}\b", clean_message):
                    req_day = d
                    break
            if "today" in clean_message or not req_day:
                req_day = datetime.now().strftime("%A")
            elif "tomorrow" in clean_message:
                from datetime import timedelta
                req_day = (datetime.now() + timedelta(days=1)).strftime("%A")

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
            today_label = f" for **{req_day}**" if req_day else ""
            return {
                "text": f"📅 Today is **{req_day}**.\n\nWhich department in the Faculty of Physical Sciences are you in? Please select your department to view your official 100-Level lecture schedule{today_label}:",
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

        reply_text = get_timetable(clean_message)
        if reply_text == "DISAMBIGUATE_PHYSICS":
            ctx["pending"] = "awaiting_physics_type"
            return {
                "text": "Are you asking about **Physics Theory (PHY 115)** or **Physics Practical (PHY 121)**?",
                "options": ["PHY 115 Theory", "PHY 121 Practical", "Both Physics Classes"]
            }
        venue_match = re.search(r"\*(.*?)\*|\((.*?)\)", reply_text)
        if venue_match:
            v = venue_match.group(1) or venue_match.group(2)
            if v:
                ctx["last_location"] = v.strip()
        return {"text": reply_text}

    # Check if query targets a specific known Campus Event (e.g. "freshers orientation", "matriculation")
    ev, ev_venue = resolve_event_venue(clean_message)
    if ev:
        if ev_venue:
            ctx["pending"] = "awaiting_source"
            ctx["destination"] = ev_venue
            ctx["last_location"] = ev_venue.formal_name
            if "ekpo" in ev.venue.lower():
                text_msg = (
                    f"🎉 **{ev.title}** takes place at **{ev.venue}** ({ev.date_time}).\n\n"
                    f"• **Ekpo Ref**: Head up the hill past the **Student Affairs Building** (beside the statue of a woman's face).\n"
                    f"• **Departmental Sessions**: Held at your respective departmental lecture halls (NCSB, Carver, Abuja Building, Geology).\n\n"
                    f"Where are you starting from, on your way to **{ev_venue.formal_name}**?"
                )
            else:
                venue_display = f"**{ev_venue.formal_name}**" if ev.venue.lower() in ev_venue.formal_name.lower() or ev_venue.formal_name.lower() in ev.venue.lower() else f"**{ev.venue}** (at {ev_venue.formal_name})"
                text_msg = f"🎉 **{ev.title}** takes place at {venue_display} ({ev.date_time}).\n\nWhere are you starting from, on your way there?"
            return {
                "text": text_msg,
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }
        else:
            ctx["last_location"] = ev.venue
            return {
                "text": f"🎉 **{ev.title}** takes place at **{ev.venue}** ({ev.date_time}).\n\n(Note: This venue is situated outside the immediate Faculty of Physical Sciences walking graph)."
            }

    # Campus event queries
    if re.search(r"\b(events?|seminars?|symposium|programmes?|party|colloquium|workshops?)\b", clean_message):
        reply_text = get_events()
        if "@" in reply_text:
            ctx["last_location"] = reply_text.split("@")[-1].strip()
        return {"text": reply_text}

    # Direct campus landmark clicks/queries (e.g. "Science Lecture Theatre (FPSLT)", "Faculty Science Canteen", "Franco Refectory", "UNN 2nd Gate")
    if not re.search(r"\b(how\s+to|when|what|deadline|last\s+day|fee|fees|cost|pay|rrr|remita|requirements?|documents?|steps?|process)\b", clean_message):
        direct_venue = resolve_location(clean_message) or resolve_target_venue(clean_message)
        if direct_venue:
            ctx["pending"] = "awaiting_source"
            ctx["destination"] = direct_venue
            return {
                "text": f"Where are you starting from, on your way to **{direct_venue.formal_name}**?",
                "options": ["Carver Building", "UNN 1st Gate (Main Gate)", "UNN 2nd Gate (Abuja / Franco Gate)", "Bello Hall (Hostel)", "New Computer Science Building (NCSB)"]
            }

    # Orientation and clearance FAQ queries
    if re.search(r"\b(cleara?nce|clerance|cgpa|gpa|grading|grade|fees?|remita|rrr|hostel|id card|library|wi-?fi|eduroam|medical|clinic|doctor|docket|exams?|malpractice|food|canteen|franco|dean|hod|officer|photocopy|print|laptop|lunch|eat|meals?)\b", clean_message):
        return {"text": answer_orientation(clean_message)}

    # spaCy NLP intent classification and entity extraction
    doc = nlp(clean_message)
    intent = max(doc.cats, key=doc.cats.get)
    confidence_score = doc.cats[intent]

    if confidence_score < 0.60:
        intent = "general_chat"

    locations = [ent.text for ent in doc.ents if ent.label_ == "LOCATION"]

    if intent == "navigate":
        return handle_navigate(session_id, locations, clean_message)

    elif intent == "orientation_help":
        return {"text": answer_orientation(clean_message)}

    elif intent == "event_query":
        has_event_signal = bool(re.search(
            r"\b(events?|seminars?|symposium|programmes?|party|colloquium|workshops?|orientation\s+ceremony|matriculation|activities|happening|functions?)\b",
            clean_message
        ))
        if not has_event_signal:
            return handle_general_chat(clean_message, session_id)

        reply_text = get_events()
        if "@" in reply_text:
            ctx["last_location"] = reply_text.split("@")[-1].strip()
        return {"text": reply_text}

    elif intent == "timetable_query":
        has_timetable_signal = bool(
            re.search(r"\b(timetable|schedule|classes?|lectures?|course|venue|mth|mat|cos|csc|phy|sta|chm|gs|gsp|geo|glg|slt|glt)\b", clean_message) or
            re.search(r"\b(monday|tuesday|wednesday|thursday|friday|saturday)\b", clean_message)
        )
        if not has_timetable_signal:
            return handle_general_chat(clean_message, session_id)

        reply_text = get_timetable(clean_message)
        if reply_text == "DISAMBIGUATE_PHYSICS":
            ctx["pending"] = "awaiting_physics_type"
            return {
                "text": "Are you asking about **Physics Theory (PHY 115)** or **Physics Practical (PHY 121)**?",
                "options": ["PHY 115 Theory", "PHY 121 Practical", "Both Physics Classes"]
            }
        venue_match = re.search(r"\*(.*?)\*|\((.*?)\)", reply_text)
        if venue_match:
            v = venue_match.group(1) or venue_match.group(2)
            if v:
                ctx["last_location"] = v.strip()
        return {"text": reply_text}

    else:
        return handle_general_chat(clean_message, session_id)



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/landmarks")
def api_landmarks():
    nodes = Node.query.all()
    edges = Edge.query.all()
    return jsonify({
        "landmarks": [{
            "id": n.node_id,
            "formal_name": n.formal_name,
            "informal_names": n.informal_names,
            "category": n.category,
            "description": n.description,
            "photo_path": n.photo_path
        } for n in nodes],
        "edges": [{
            "source": e.source_node_id,
            "destination": e.destination_node_id,
            "distance": e.distance_meters,
            "instruction": e.instruction
        } for e in edges]
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    reply_data = handle_message(message, session_id)
    
    return jsonify({
        "reply": reply_data["text"],
        "image": reply_data.get("image"),
        "options": reply_data.get("options", []),
        "route_nodes": reply_data.get("route_nodes", []),
        "total_distance": reply_data.get("total_distance"),
        "est_mins": reply_data.get("est_mins"),
        "steps": reply_data.get("steps", []),
        "source_name": reply_data.get("source_name"),
        "destination_name": reply_data.get("destination_name"),
        "session_id": session_id
    })

# Admin authentication
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.environ.get(
    "ADMIN_PASSWORD_HASH",
    generate_password_hash(os.environ.get("ADMIN_PASSWORD", "lionpath2026"))
)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        admin_record = Admin.query.filter_by(username=username).first()
        is_authenticated = False

        if admin_record and check_password_hash(admin_record.password_hash, password):
            is_authenticated = True
            session["admin_name"] = admin_record.full_name
        elif username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            is_authenticated = True
            session["admin_name"] = "System Administrator"

        if is_authenticated:
            session["is_admin"] = True
            flash("Logged in successfully as Administrator.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("admin_dashboard"))
        else:
            flash("Invalid administrator credentials. Please try again.", "danger")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_login"))


# Admin dashboard routes

@app.route("/admin")
@admin_required
def admin_dashboard():
    active_tab = request.args.get("tab", "faq")
    new_id = request.args.get("new_id", type=int)
    faqs = OrientationKB.query.order_by(OrientationKB.kb_id.desc()).all()
    nodes = Node.query.order_by(Node.node_id.desc()).all()
    timetables = Timetable.query.order_by(Timetable.id.desc()).all()
    events = Event.query.order_by(Event.id.desc()).all()
    return render_template("admin.html", faqs=faqs, nodes=nodes, timetables=timetables, events=events, active_tab=active_tab, new_id=new_id)

@app.route("/admin/add_faq", methods=["POST"])
@admin_required
def add_faq():
    category = request.form.get("category")
    pattern = request.form.get("question_pattern")
    answer = request.form.get("answer")
    
    if category and pattern and answer:
        new_faq = OrientationKB(category=category, question_pattern=pattern, answer=answer)
        db.session.add(new_faq)
        db.session.commit()
        flash("FAQ added successfully!", "success")
        return redirect(url_for("admin_dashboard", tab="faq", new_id=new_faq.kb_id))
    flash("Missing data! Please try again.", "danger")
    return redirect(url_for("admin_dashboard", tab="faq"))

@app.route("/admin/add_node", methods=["POST"])
@admin_required
def add_node():
    formal_name = request.form.get("formal_name")
    informal_names = request.form.get("informal_names")
    category = request.form.get("category")
    description = request.form.get("description")
    
    photo = request.files.get("photo_file")
    photo_path = ""
    
    if photo and photo.filename:
        filename = secure_filename(photo.filename)
        save_location = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        photo.save(save_location)
        photo_path = f"images/{filename}"

    if formal_name and category:
        new_node = Node(
            formal_name=formal_name,
            informal_names=informal_names,
            category=category,
            description=description,
            photo_path=photo_path
        )
        db.session.add(new_node)
        db.session.commit()
        flash(f"Building '{formal_name}' added successfully!", "success")
        return redirect(url_for("admin_dashboard", tab="building", new_id=new_node.node_id))
    flash("Missing required data! Please try again.", "danger")
    return redirect(url_for("admin_dashboard", tab="building"))

@app.route("/admin/add_timetable", methods=["POST"])
@admin_required
def add_timetable():
    course_code = request.form.get("course_code")
    course_title = request.form.get("course_title", "").strip()
    department = request.form.get("department", "General").strip()
    day = request.form.get("day")
    time = request.form.get("time")
    venue = request.form.get("venue")
    
    if course_code and day and time and venue:
        new_class = Timetable(course_code=course_code, course_title=course_title, department=department, day=day, time=time, venue=venue)
        db.session.add(new_class)
        db.session.commit()
        flash(f"Timetable for {course_code} added successfully!", "success")
        return redirect(url_for("admin_dashboard", tab="timetable", new_id=new_class.id))
    flash("Missing data! Please try again.", "danger")
    return redirect(url_for("admin_dashboard", tab="timetable"))

@app.route("/admin/add_event", methods=["POST"])
@admin_required
def add_event():
    title = request.form.get("title")
    date_time = request.form.get("date_time")
    venue = request.form.get("venue")
    
    if title and date_time and venue:
        new_event = Event(title=title, date_time=date_time, venue=venue)
        db.session.add(new_event)
        db.session.commit()
        flash(f"Event '{title}' added successfully!", "success")
        return redirect(url_for("admin_dashboard", tab="event", new_id=new_event.id))
    flash("Missing data! Please try again.", "danger")
    return redirect(url_for("admin_dashboard", tab="event"))

@app.route("/admin/delete_faq/<int:id>", methods=["POST"])
@admin_required
def delete_faq(id):
    faq = OrientationKB.query.get_or_404(id)
    db.session.delete(faq)
    db.session.commit()
    flash("FAQ deleted successfully.", "info")
    return redirect(url_for("admin_dashboard", tab="faq"))


@app.route("/admin/delete_node/<int:id>", methods=["POST"])
@admin_required
def delete_node(id):
    node = Node.query.get_or_404(id)
    # Remove connected routes first
    Edge.query.filter((Edge.source_node_id == id) | (Edge.destination_node_id == id)).delete()
    db.session.delete(node)
    db.session.commit()
    flash(f"Landmark '{node.formal_name}' and connected paths deleted successfully.", "info")
    return redirect(url_for("admin_dashboard", tab="building"))


@app.route("/admin/delete_timetable/<int:id>", methods=["POST"])
@admin_required
def delete_timetable(id):
    entry = Timetable.query.get_or_404(id)
    code = entry.course_code
    db.session.delete(entry)
    db.session.commit()
    flash(f"Schedule for '{code}' deleted successfully.", "info")
    return redirect(url_for("admin_dashboard", tab="timetable"))


@app.route("/admin/delete_event/<int:id>", methods=["POST"])
@admin_required
def delete_event(id):
    event = Event.query.get_or_404(id)
    title = event.title
    db.session.delete(event)
    db.session.commit()
    flash(f"Event '{title}' deleted successfully.", "info")
    return redirect(url_for("admin_dashboard", tab="event"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(host=host, port=port, debug=debug_mode)