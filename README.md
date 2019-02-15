# SARRLEK
Semantic Analysis of Radiology Reports with Lexicon as Embedded Knowledge

## Installing required packages

Python requirements are listed on the `requirements.txt` file. To install all
requirements, make sure your run:

```
pip install -r requirements.txt
```
## Running pipeline
Currently there are 3 steps to run in the pipeline: data preparation, training
word2vec model and training topic model (LDA). This can be done with the following
python scripts:

data preparation:
```
python cleaning.py --in=Data/ct_report_dmg_thoracic_only.csv --out=Data/ct_report_dmg_thoracic_only_CLEAN.csv
```

data preparation (with additional structurize step):
```
python cleaning.py --in=Data/ct_report_dmg_thoracic_only.csv --out=Data/ct_report_dmg_thoracic_only_CLEAN_STRUCT.csv --structurize
```

training word2vec model:
```
python buildw2v.py --in Data/ct_report_dmg_thoracic_only_CLEAN.csv --out Data/ct_report_model.w2v --vectors Data/ct_report_vectors.csv
```

training topic model:
```
python buildlda.py --in Data/ct_report_dmg_thoracic_only_CLEAN.csv --out-dict Data/ct_report_topics.dict --out-model Data/ct_report_topics.lda --out-topics Data/ct_report_topics.csv
```

training flair model:
```
python buildflair.py --in-reports=Data/ct_report_dmg_thoracic_only_CLEAN.csv --in-classes=Data/classes.csv --cancer-classifier=out/classifier_cancer --prog-classifier=out//classifier_prog
```
