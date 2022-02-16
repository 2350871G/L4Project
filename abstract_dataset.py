
from abc import ABC, abstractmethod


class AbstractDataset(ABC):

    @staticmethod
    def get_chunks(lst, k):
        """Yield successive chunks from n-sized lst."""
        length = len(lst)
        for i in range(0, length, k):
            yield lst[i:i + k]

    @abstractmethod
    def generate_documents(self, k=1):
        """ Generator of k-sized chunks of documents for a given dataset. """
        pass
