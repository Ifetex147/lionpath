# Domain Training Data for LionPath Campus Assistant
# Categories: navigate, orientation_help, event_query, timetable_query, general_chat

TRAINING_DATA = [
    # =========================================================================
    # 1. NAVIGATE
    # =========================================================================
    ("how do I get to the physics block", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(20, 33, "LOCATION")]}),
    ("where is the faculty library", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(13, 28, "LOCATION")]}),
    ("directions from CS block to the hostel", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(16, 24, "LOCATION"), (32, 38, "LOCATION")]}),
    ("take me to the Computer Science building", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(15, 40, "LOCATION")]}),
    ("where is the physics block located", {
         "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
         "entities": [(13, 26, "LOCATION")]}),
    ("give me directions to the library", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(26, 33, "LOCATION")]}),
    ("take me to the library", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(15, 22, "LOCATION")]}),
    ("can you direct me to the faculty library", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(25, 40, "LOCATION")]}),
    ("how can I reach the physics block from here", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(20, 33, "LOCATION")]}),
    ("I need walking directions to CS department", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(29, 42, "LOCATION")]}),
    ("route to the lecture theatre please", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(13, 28, "LOCATION")]}),
    ("guide me to the main campus gate", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(16, 32, "LOCATION")]}),
    ("where is the student hostel situated", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(13, 27, "LOCATION")]}),
    ("find route to mathematics department", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(14, 36, "LOCATION")]}),
    ("show me the way to science lecture theatre", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(19, 42, "LOCATION")]}),
    ("how do I get to Abuja building", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(16, 30, "LOCATION")]}),
    ("lead me to Carver building", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(11, 26, "LOCATION")]}),
    ("walking path from library to physics block", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": [(18, 25, "LOCATION"), (29, 42, "LOCATION")]}),
    ("campus directions", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("directions", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("navigation", {
        "cats": {"navigate": 1.0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),

    # =========================================================================
    # 2. ORIENTATION_HELP
    # =========================================================================
    ("how do I pay my school fees", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("what do I need for clearance", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how to do clerance", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how to do clearance", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("steps to register my courses", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how do I collect my ID card", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("when does course registration end", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("when does registration close", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how much is the school fees", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("where do I pay my acceptance fee", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("How do I get a hostel?", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("Where can I find hostel accommodation?", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how do freshmen pay their school charges", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("what documents are required for faculty clearance", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("explain the procedure for student ID collection", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("what is the deadline for online course enrollment", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how do I apply for hostel accommodation", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("where can I find information on matriculation fee", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("guidelines for medical registration", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("how do I generate remita for fees", {
        "cats": {"navigate": 0, "orientation_help": 1.0, "event_query": 0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),

    # =========================================================================
    # 3. EVENT_QUERY
    # =========================================================================
    ("what events are happening this week", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("is there any seminar in the faculty soon", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("when is the fresher's welcome party", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("when is the next faculty event", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("Are there any events happening today?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("What events are happening?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("are there any departmental seminars holding this week", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("what time does the orientation symposium start", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("tell me about upcoming faculty activities", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("is there any program scheduled for tomorrow", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("when is the faculty dean welcome address", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("upcoming workshops in physical sciences", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),
    ("campus orientation date and time", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 1.0, "timetable_query": 0, "general_chat": 0},
        "entities": []}),

    # =========================================================================
    # 4. TIMETABLE_QUERY
    # =========================================================================
    ("what is the CSC 101 timetable", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(12, 19, "COURSE")]}),
    ("when do I have MTH 101 on Monday", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(15, 22, "COURSE"), (26, 32, "DATE")]}),
    ("show me my classes for computer science 100 level", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": []}),
    ("when does the physics lecture hold", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(14, 29, "COURSE")]}),
    ("show me my classes", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": []}),
    ("what classes do I have today", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": []}),
    ("what is my schedule", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": []}),
    ("what time is COS 101 on Wednesday", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(13, 20, "COURSE"), (24, 33, "DATE")]}),
    ("when is the schedule for MAT 111 lecture", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(25, 32, "COURSE")]}),
    ("show me STA 131 lecture venue and time", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(8, 15, "COURSE")]}),
    ("when do we have physics practical class", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": []}),
    ("what lectures do I have on Friday morning", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(27, 33, "DATE")]}),
    ("what is the venue for PHY 115", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(22, 29, "COURSE")]}),
    ("timetable for GS 101", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 1.0, "general_chat": 0},
        "entities": [(14, 20, "COURSE")]}),

    # =========================================================================
    # 5. GENERAL_CHAT
    # =========================================================================
    ("hello", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0},
        "entities": []}),
    ("who are you", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0},
        "entities": []}),
    ("thanks for the help", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0},
        "entities": []}),
    ("hi", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0},
        "entities": []}),
    ("hey there", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0},
        "entities": []}),
    ("what is your name?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("who are you?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("good morning", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("good afternoon LionPath", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("good evening assistant", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("how are you doing today?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("thank you very much for assisting me", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what can you help me with?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("bye, talk to you later", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("nice to meet you", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what is today's date?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what is todays date", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what is the date today?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what day is today?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what time is it?", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("tell me the current date and time", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("what is my name", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("who am i", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
    ("do you know my name", {
        "cats": {"navigate": 0, "orientation_help": 0, "event_query": 0, "timetable_query": 0, "general_chat": 1.0}, 
        "entities": []}),
]
