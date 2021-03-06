<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->

# 🪐 spaCy Project: TYN NER Pipeline on human-labelled data 

An NER project for labelling "Things you'll need" in instructional text. Trained and evaluated on human-labelled data created using Prodigy. CNN architecture is used for the model.

## 📋 project.yml

The [`project.yml`](project.yml) defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation](https://spacy.io/usage/projects).

### ⏯ Commands

The following commands are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run).
Commands are only re-run if their inputs have changed.

| Command | Description |
| --- | --- |
| `download` | Download a spaCy model with pretrained vectors |
| `convert` | Convert the data to spaCy's binary format |
| `create-config` | Create a new config with an NER pipeline component |
| `train` | Train the NER model |
| `train-with-vectors` | Train the NER model with vectors |
| `evaluate` | Evaluate the model and export metrics |
| `package` | Package the trained model as a pip package |
| `visualize-model` | Visualize the model's output interactively using Streamlit |

### ⏭ Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `all` | `convert` &rarr; `create-config` &rarr; `train` &rarr; `evaluate` |

### 🗂 Assets

The following assets are defined by the project. They can
be fetched by running [`spacy project assets`](https://spacy.io/api/cli#project-assets)
in the project directory.

| File | Source | Description |
| --- | --- | --- |
| [`assets/train.json`](assets/train.json) | Local | 80% of the labelled data used for training |
| [`assets/dev.json`](assets/dev.json) | Local | Unseen 20% of the labelled data used for evaluation |

<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->
