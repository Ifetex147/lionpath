import spacy
from spacy.training import offsets_to_biluo_tags
from train_data import TRAINING_DATA

nlp = spacy.blank("en")
ok = True
for text, ann in TRAINING_DATA:
    if not ann["entities"]:
        continue
    tags = offsets_to_biluo_tags(nlp.make_doc(text), ann["entities"])
    if "-" in tags:
        ok = False
        print(f"MISALIGNED: {text}")
        print(f"  entities: {ann['entities']}")
print("All offsets OK" if ok else "Fix the ones above")