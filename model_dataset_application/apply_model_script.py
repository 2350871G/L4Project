import spacy, os, sys, srsly, shutil

MODEL_PATH = "model"
DUMP_PATH = "tyn_dump"
WIKI_DUMP_PATH = "D:/Uni/4th Year/Computing/Project/Code/Data/wikihow_dump_v1"
UNAPPLIED_DUMP_PATH = "new_wiki_dump"
WIKI_CATEGORIES = ['Home and Garden', 'Hobbies and Crafts', 'Food and Entertaining']

def get_model():
    cwd = os.path.dirname(__file__)
    model_dir = os.path.join(cwd, MODEL_PATH)
    try:
        model = spacy.load(model_dir)
        return model
    except:
        print(f"Error loading model from {model_dir}")
        
def get_tyn_files():
    cwd = os.path.dirname(__file__)
    dump_dir = os.path.join(cwd, DUMP_PATH)
    try:
        files = os.listdir(dump_dir)
        return files
    except:
        print(f"Error getting files from from {dump_dir}")
        
def get_non_tyn_files():
    cwd = os.path.dirname(__file__)
    dump_dir = os.path.join(cwd, UNAPPLIED_DUMP_PATH)
    try:
        files = os.listdir(dump_dir)
        return files
    except:
        print(f"Error getting files from from {dump_dir}")
        
def move_non_tyn_articles():
    print('MOVING NON TYN FILES')
    cwd = os.path.dirname(__file__)
    files = os.listdir(WIKI_DUMP_PATH)
    no = len(files)
    tyn_articles = get_tyn_files()
    for f in files:
        if f not in tyn_articles:
            o = srsly.read_json(os.path.join(WIKI_DUMP_PATH, f))
            if any([cat in o['category_hierarchy'] for cat in WIKI_CATEGORIES]):
                shutil.copyfile(os.path.join(WIKI_DUMP_PATH, f), os.path.join(cwd, UNAPPLIED_DUMP_PATH, f))
        no-=1
        if no%1000==0:
            print(no)
    
def change_tag_to_section():
    files = get_tyn_files()
    no = len(files)
    cwd = os.path.dirname(__file__)
    print("CHANGING TYN TAG TO SECTION")
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        if 'tyn' in o:
            tyn_section = o['tyn']
            o['tyn_section'] = tyn_section
            o.pop('tyn', None)
            srsly.write_json(os.path.join(cwd, DUMP_PATH, f), o)
        else:
            print(f'No tyn in file: {f}')
        no-=1
        if no%100==0:
            print(no)

def remove_non_desired_articles():
    files = get_tyn_files()
    no = len(files)
    cwd = os.path.dirname(__file__)
    print("REMOVING UNDESIRED ARTICLES")
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        if not any([cat in o['category_hierarchy'] for cat in WIKI_CATEGORIES]):
            os.remove(os.path.join(cwd, DUMP_PATH, f))
        no-=1
        if no%100==0:
            print(no)

def freq(l):
    d = {}
    for x in l:
        if x in d:
            d[x]+=1
        else:
            d[x] = 1
    return d
  
def apply_model_to_articles():
    model = get_model()
    files = get_tyn_files()
    no = len(files)
    cwd = os.path.dirname(__file__)
    print('APPLYING MODEL TO ARTICLES')
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        if 'tyn_model' in o:
            no-=1
            if no%100==0:
                print(no)
            pass
        else:
            doc = model(o['text'])
            ents = [ent.text.lower() for ent in doc.ents]
            freqs = freq(ents)
            o['tyn_model'] = sorted(list(freqs.keys()), key = lambda x: freqs[x], reverse = True)
            srsly.write_json(os.path.join(cwd, DUMP_PATH, f), o)
            no-=1
            if no%100==0:
                print(no)

def apply_model_to_non_tyn_articles():
    files = get_non_tyn_files()
    model = get_model()
    no = len(files)
    cwd = os.path.dirname(__file__)
    print('APPLYING MODEL TO ARTICLES')
    for f in files:
        o = srsly.read_json(os.path.join(cwd, UNAPPLIED_DUMP_PATH, f))
        if 'tyn_model' in o:
            no-=1
            if no%100==0:
                print(no)
        else:
            doc = model(o['text'])
            ents = [ent.text.lower() for ent in doc.ents]
            freqs = freq(ents)
            o['tyn_model'] = sorted(list(freqs.keys()), key = lambda x: freqs[x], reverse = True)
            srsly.write_json(os.path.join(cwd, UNAPPLIED_DUMP_PATH, f), o)
            no-=1
            if no%100==0:
                print(no)
  
def add_text_field():
    """
    Add 'text' field which includes all instructions text in one field
    """
    print('ADDING TEXT FIELD')
    files = get_non_tyn_files()
    cwd = os.path.dirname(__file__)
    no = len(files)
    for f in files:
        o = srsly.read_json(os.path.join(cwd, UNAPPLIED_DUMP_PATH, f))
        o = get_obj_with_text(o )
        srsly.write_json(os.path.join(cwd, UNAPPLIED_DUMP_PATH, f), o)
        no-=1
        if no%1000==0:
                print(no)
        
def get_obj_with_text(obj):
    text = ''
    if 'steps' in list(obj.keys()):
        steps = obj['steps']
        for step in steps:
            text+=' '+step['headline']
            text+=' '+step['description']
    elif 'parts' in list(obj.keys()):
        parts = obj['parts']
        for part in parts:
            text+=' '+part['name']
            for step in part['steps']:
                text+=' '+step['headline']
                text+=' '+step['description']
    elif 'methods' in list(obj.keys()):
        methods = obj['methods']
        for method in methods:
            text+=' '+method['name']
            for step in method['steps']:
                text+=' '+step['headline']
                text+=' '+step['description']
    obj['text'] = text
    return obj

#####MAIN PROGRAM#######
if __name__ == '__main__':
    #remove_non_desired_articles()
    #change_tag_to_section()
    #apply_model_to_articles()
    #move_non_tyn_articles()
    #add_text_field()
    apply_model_to_non_tyn_articles()