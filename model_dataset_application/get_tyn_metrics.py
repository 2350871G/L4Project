import spacy, os, sys, srsly, shutil

MODEL_PATH = "model"
DUMP_PATH = "tyn_dump"
WIKI_CATEGORIES = ['Home and Garden', 'Hobbies and Crafts', 'Food and Entertaining']

def get_tyn_files():
    cwd = os.path.dirname(__file__)
    dump_dir = os.path.join(cwd, DUMP_PATH)
    try:
        files = os.listdir(dump_dir)
        return files
    except:
        print(f"Error getting files from from {dump_dir}")

def remove_heading_tyns():
    files = get_tyn_files()
    print('REMOVING HEADING TYNS')
    no = len(files)
    cwd = os.path.dirname(__file__)
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        if 'methods' in o:
            for m in o['methods']:
                if m['name'] in o['tyn_section']:
                    o['tyn_section'].remove(m['name'])
        elif 'parts' in o:
            for p in o['parts']:
                if p['name'] in o['tyn_section']:
                    o['tyn_section'].remove(p['name'])
        srsly.write_json(os.path.join(cwd, DUMP_PATH, f), o)
        no-=1
        if no%1000==0:
            print(no)

def add_tyn_simple_metrics_field():
    files = get_tyn_files()
    no = len(files)
    print('CALCULATING METRICS FOR TYN FILES')
    cwd = os.path.dirname(__file__)
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        simple_metrics = {}
        simple_metrics['r'] = get_simple_recall(o)
        simple_metrics['p'] = get_simple_precision(o)
        simple_metrics['f1'] = get_simple_f1(simple_metrics)
        simple_metrics['avg_pos'] = get_simple_avg_pos(o)
        o['simple_metrics'] = simple_metrics
        srsly.write_json(os.path.join(cwd, DUMP_PATH, f), o)
        no-=1
        if no%1000==0:
            print(no)

def get_simple_recall(o):
    if o['tyn_section']:
        return sum([1 if x.lower() in [t.lower() for t in o['tyn_model']] else 0 for x in o['tyn_section']])/len(o['tyn_section'])
    return 0
    
def get_simple_precision(o):
    if o['tyn_model']:
        return sum([1 if x.lower() in [t.lower() for t in o['tyn_section']] else 0 for x in o['tyn_model']])/len(o['tyn_model'])
    return 0
    
def get_simple_f1(m):
    if (m['p']+m['r']) != 0:    
        return 2*(m['p']*m['r'])/(m['p']+m['r'])
    return 0
    
def get_simple_avg_pos(o):
    pos_l = []
    for t in o['tyn_section']:
        if t.lower() in [t.lower() for t in o['tyn_model']]:
            pos_l.append(o['tyn_model'].index(t.lower())/len(o['tyn_model']))
        if pos_l:
            return sum(pos_l)/len(pos_l)
        return 0

def output_avg_metrics():
    files = get_tyn_files()
    cwd = os.path.dirname(__file__)
    p,r,f1,pos = 0,0,0,0
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        p+= o['simple_metrics']['p']
        r+= o['simple_metrics']['r']
        pos+= o['simple_metrics']['avg_pos']
        f1+= o['simple_metrics']['f1']
    m = {}
    m['p'], m['r'], m['f1'], m['pos'] = p/len(files), r/len(files), f1/len(files), pos/len(files)
    srsly.write_json(os.path.join(cwd, 'avg_simple_metrics.json'), m)
    
def output_category_metrics():
    files = get_tyn_files()
    cwd = os.path.dirname(__file__)
    cat_mets = {cat : {'p':0,'r':0,'pos':0,'f1':0,'len':0} for cat in WIKI_CATEGORIES}
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        if o['category_hierarchy'][0] in cat_mets:
            cat_mets[o['category_hierarchy'][0]]['p']+= o['simple_metrics']['p']
            cat_mets[o['category_hierarchy'][0]]['r']+= o['simple_metrics']['r']
            cat_mets[o['category_hierarchy'][0]]['pos']+= o['simple_metrics']['avg_pos']
            cat_mets[o['category_hierarchy'][0]]['f1']+= o['simple_metrics']['f1']
            cat_mets[o['category_hierarchy'][0]]['len'] += 1
        else:
            x = o['category_hierarchy'][0]
            print(f'UNEXPECTED CATEGORY FOUND: {x}')
    m = {cat:{'p':cat_mets[cat]['p']/cat_mets[cat]['len'], 'r':cat_mets[cat]['r']/cat_mets[cat]['len'], 'pos':cat_mets[cat]['pos']/cat_mets[cat]['len'], 'f1':cat_mets[cat]['f1']/cat_mets[cat]['len'], 'len': cat_mets[cat]['len']} for cat in WIKI_CATEGORIES}
    srsly.write_json(os.path.join(cwd, 'avg_simple_cat_metrics.json'), m)
    
def add_tyn_jaccard_metrics_field(thresh):
    files = get_tyn_files()
    no = len(files)
    print(f'CALCULATING JACCARD METRICS FOR TYN FILES WITH THRESHOLD = {thresh}')
    cwd = os.path.dirname(__file__)
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        if 'jacc_metrics' in o:
            o.pop('jacc_metrics', None)
        jacc_metrics = {}
        jacc_metrics['r'] = get_jacc_recall(o, thresh)
        jacc_metrics['p'] = get_jacc_precision(o, thresh)
        jacc_metrics['f1'] = get_jacc_f1(jacc_metrics)
        o[f'jacc_metrics_{thresh}'] = jacc_metrics
        srsly.write_json(os.path.join(cwd, DUMP_PATH, f), o)
        no-=1
        if no%1000==0: print(no)
    
def jaccard(d1, d2):
    doc1, doc2 = d1.split(), d2.split()
    s1 = set([t.lower() for t in doc1])
    s2 = set([t.lower() for t in doc2])
    return (len(s1.intersection(s2)))/(len(s1.union(s2)))
  
def get_jacc_recall(o, thresh):
    if o['tyn_section']:
        count = 0
        for x in o['tyn_section']:
            if any([jaccard(x,y)>= thresh for y in o['tyn_model']]):
                count+=1
        return count/len(o['tyn_section'])
    return 0
    
def get_jacc_precision(o, thresh):
    if o['tyn_model']:
        count = 0
        for x in o['tyn_model']:
            if any([jaccard(x,y)>= thresh for y in o['tyn_section']]):
                count+=1
        return count/len(o['tyn_model'])
    return 0
    
def get_jacc_f1(m):
    if (m['p']+m['r']) != 0:    
        return 2*(m['p']*m['r'])/(m['p']+m['r'])
    return 0
    
def output_avg_metrics_jacc(thresh):
    files = get_tyn_files()
    cwd = os.path.dirname(__file__)
    p,r,f1 = 0,0,0
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        p+= o[f'jacc_metrics_{thresh}']['p']
        r+= o[f'jacc_metrics_{thresh}']['r']
        f1+= o[f'jacc_metrics_{thresh}']['f1']
    m = {}
    m['p'], m['r'], m['f1']= p/len(files), r/len(files), f1/len(files)
    srsly.write_json(os.path.join(cwd, f'avg_jacc_{thresh}_metrics.json'), m)

def output_perf_articles():
    files = get_tyn_files()
    cwd = os.path.dirname(__file__)
    metrics = ["simple_metrics", "jacc_metrics_0.5", "jacc_metrics_0.3333333333333333", "jacc_metrics_0.6666666666666666"]
    output = {metric: {'count':0, 'articles': []} for metric in metrics}
    for f in files:
        o = srsly.read_json(os.path.join(cwd, DUMP_PATH, f))
        for m in metrics:
            if o[m]['r'] == 1.0:
                output[m]['count']+=1
    srsly.write_json('perf_articles.json', output)
        
#####MAIN PROGRAM#######
if __name__ == '__main__':
    #remove_heading_tyns()
    #add_tyn_simple_metrics_field()
    #output_avg_metrics()
    #output_category_metrics()
    #add_tyn_jaccard_metrics_field(2/3)
    #output_avg_metrics_jacc(2/3)
    output_perf_articles()