
from datasets.abstract_dataset import AbstractDataset

import json
import os

class WikihowDataset(AbstractDataset):

    wiki_categories = ['Home and Garden', 'Hobbies and Crafts', 'Food and Entertaining']

    def __init__(self, input_dir):
        print('--- init WikihowDataset ---')
        self.input_dir =  input_dir
        self.documents = self.__get_documents()

    def __get_documents(self):
        """ Read documents from dataset. """
        path = os.path.join(self.input_dir, 'wiki_upen.jsonl')
        documents = []
        with open(path, 'r') as f:
            for line in f:
                document = json.loads(line)
                if any(t in document['category_hierarchy'] for t in self.wiki_categories):
                    documents.append(document)
        return documents

    def generate_documents(self, k=1):
        """ Generator of k-sized chunks of documents for a given dataset. """
        yield from self.get_chunks(self.documents, k=k)