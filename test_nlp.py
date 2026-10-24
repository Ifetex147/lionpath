import spacy

nlp = spacy.load("lionpath_nlp")

def test(text):
    doc = nlp(text)
    intent = max(doc.cats, key=doc.cats.get)
    confidence = doc.cats[intent]
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"\nText: {text}")
    print(f"Intent: {intent} ({confidence:.2f})")
    print(f"Entities: {entities}")

test("how do I get to the physics block")
test("what is the CSC 101 timetable")
test("when is the next faculty event")
test("how do I pay my acceptance fee")
test("hi")