import spacy
from difflib import get_close_matches
# If you have your Dijkstra script, import it here:
# from graph_logic import get_shortest_path, campus_nodes

# 1. Load the trained NLP model
nlp = spacy.load("lionpath_nlp")

# 2. Define your valid graph nodes (replace with your actual graph nodes)
VALID_LOCATIONS = [
    "Physics Block", 
    "Faculty Library", 
    "CS Block", 
    "Hostel",
    "Admin Block",
    "Main Gate"
]

def get_bot_response(user_input):
    # 3. Pass text through the NLP pipeline
    doc = nlp(user_input)
    
    # 4. Get the highest scoring intent
    intent = max(doc.cats, key=doc.cats.get)
    confidence = doc.cats[intent]
    
    # Optional: Safety net for low confidence
    if confidence < 0.6:
        return "I'm not quite sure what you mean. Could you rephrase that?"

    # 5. Route based on intent
    if intent == "navigate":
        # Extract the LOCATION entity
        locations = [ent.text for ent in doc.ents if ent.label_ == "LOCATION"]
        
        if not locations:
            return "I know you need directions, but I didn't catch the exact building. Where are you heading?"
            
        target = locations[-1] # Take the last location mentioned
        
        # 6. Fuzzy Match: Bridge the gap between human text and strict graph nodes
        matches = get_close_matches(target.title(), VALID_LOCATIONS, n=1, cutoff=0.5)
        
        if matches:
            best_match = matches[0]
            # --- DIJKSTRA HAPPENS HERE ---
            # path = get_shortest_path("Current Location", best_match)
            # return f"Path found: {path}"
            return f"[SYSTEM]: Calculating Dijkstra path to the {best_match}..."
        else:
            return f"I couldn't find '{target}' on the campus map. Did you mean somewhere else?"

    elif intent == "timetable_query":
        courses = [ent.text for ent in doc.ents if ent.label_ == "COURSE"]
        if courses:
            return f"Fetching the timetable for {courses[0].upper()}..."
        return "Which course timetable do you need?"

    elif intent == "event_query":
        return "Here is the link to the UNN faculty events calendar: [Link]"

    elif intent == "orientation_help":
        return "You can find clearance steps and fee payment guides on the freshman portal: [Link]"

    elif intent == "general_chat":
        return "Hello! I'm LionPath. I can help you navigate campus, check timetables, or find events. What do you need?"

# 7. Start the terminal chat loop
print("🦁 LionPath Terminal Interface")
print("Type 'quit' to exit.\n")

while True:
    text = input("You: ")
    if text.lower() in ['quit', 'exit']:
        break
        
    response = get_bot_response(text)
    print(f"LionPath: {response}\n")