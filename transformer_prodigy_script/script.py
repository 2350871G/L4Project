import spacy
import os
import sys
import pathlib

MODEL_PATH = "model"

def get_filepath():
    if len(sys.argv) > 1:
        if os.path.exists(sys.argv[1]):
            return sys.argv[1]
        print("The file you entered does not exist, please enter another")
    print("Please a filepath to the instruction text")
    
def get_model():
    cwd = os.path.dirname(__file__)
    model_dir = os.path.join(cwd, MODEL_PATH)
    try:
        model = spacy.load(model_dir)
        return model
    except:
        print(f"Error loading model from {model_dir}")
    
def get_tyn(filepath):
    with open(filepath) as f:
        text = f.read()
    tyn = get_tyn_from_text(text)
    return sorted(tyn)

def get_tyn_from_text(text):
    ner = get_model()
    if ner:
        d = ner(text)
        return collate_tyn(d.ents)
        
def collate_tyn(tyn):
    ents = [ent.text.lower() for ent in tyn]
    freqs = freq(ents)
    return sorted(list(freqs.keys()), key = lambda x: freqs[x], reverse = True)

def freq(l):
    d = {}
    for x in l:
        if x in d:
            d[x]+=1
        else:
            d[x] = 1
    return d

# MAIN PROGRAM
if __name__ == "__main__":
    text_filepath = get_filepath()
    if text_filepath:
        print('Getting \'Things you need\' from instruction text in file at', text_filepath)
        tyn = get_tyn(text_filepath)
        if tyn:
            print('\'Things you need\' found in instruction text:')
            for thing in tyn:
                print(thing)
        else:
            print('No \'Things you need\' found')