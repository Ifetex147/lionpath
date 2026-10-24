import spacy
from spacy.training import Example
from train_data import TRAINING_DATA

INTENTS = ["navigate", "orientation_help", "event_query", "timetable_query", "general_chat"]

nlp = spacy.blank("en")

# Text classifier: picks one of the five intents
textcat = nlp.add_pipe("textcat")
for label in INTENTS:
    textcat.add_label(label)

# Named entity recognizer: finds locations, course codes, dates
ner = nlp.add_pipe("ner")
for label in ["LOCATION", "COURSE", "DATE"]:
    ner.add_label(label)

examples = []
for text, annotations in TRAINING_DATA:
    doc = nlp.make_doc(text)
    example = Example.from_dict(doc, annotations)
    examples.append(example)

# Train
optimizer = nlp.initialize()
for epoch in range(30):
    losses = {}
    nlp.update(examples, sgd=optimizer, losses=losses)
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: {losses}")

nlp.to_disk("lionpath_nlp")
print("Model saved to lionpath_nlp/")