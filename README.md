# L4Project
Repository for code, datasets, and resources related to my Level 4 project. My project is an NLP task for extracting household task structure from Wikihow articles, specifically related to the tools and materials required for a given task.

## Directory structure
- **Datasets** - Unlabelled datasets generated over the course of the project. Includes TYN dump scraped from Wikihow.
- **Notebooks** - Notebooks created in the project. Includes exploration of initial design ideas and training of transformer models on hosted GPU.
- **Preprocessing scripts** - Scripts used to generate and convert labelled training data created using gazetteers and Jaccard similarity matching on noun chunks.
- **ner** - CNN NER model trained on simple string matching labelled data. spaCy project with instructions for running inside.
- **ner_jaccard** CNN NER model trained on  Jaccard labelled data. spaCy project
- **Jaccard_trained_script** - To interact with packaged CNN model trained on Jaccard labelled data. Model achieves good results on unseen data labelled using the same method, but system does not perform well at TYN extraction on practical examples.
- **Prodigy labelling** - Folder with files related to human-labelled data created using Prodigy and models trained on this dataset. Includes spaCy projects for models with instructions to run.
- **transformer_ner_HaG** - Transformer model trained only on instructions from articles in the "Home and Garden" category, labelled using Jaccard matching. Model achieves good performance and script works well with practical examples from instructions for tasks in the correct category.
- **transformer_prodigy_script** - Script for interacting with transformer model trained on human-labelled data. This is the final system evaluated, and this model has the strongest metrics on test data and best results at extracting TYN from real instructions. tests folder inside includes tests on examples of real instructional text.
- **model_dataset_application** - Directory for scripts and metrics from applying final system for extracting TYN using trained model to Wikihow dataset.
