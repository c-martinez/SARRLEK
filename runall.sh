#!/usr/bin/env bash

# DATA_IN -- Input radiology reports
# GT_IN   -- Ground truth annotations
DATA_IN=Data/testrun/ct_report_dmg_thoracic_only.csv
GT_IN=Data/testrun/ct_progression_classes.csv

# Name of files used
BASE_DIR=$(dirname $DATA_IN)
BASE_NAME=$(basename $DATA_IN .csv)

CLEAN_DATA=$BASE_DIR/$BASE_NAME"_CLEAN.csv"

# training word2vec model
W2V_MODEL=$BASE_DIR/$BASE_NAME"_MODEL.w2v"
W2V_VEC=$BASE_DIR/$BASE_NAME"_w2vVectors.csv"
W2V_C_CLSFR=$BASE_DIR/$BASE_NAME"_C_CLASSIFIER_W2V"
W2V_P_CLSFR=$BASE_DIR/$BASE_NAME"_P_CLASSIFIER_W2V"

#training topic model
LDA_DICT=$BASE_DIR/$BASE_NAME"_LDA.dict"
LDA_MODEL=$BASE_DIR/$BASE_NAME"_MODEL.lda"
LDA_VEC=$BASE_DIR/$BASE_NAME"_ldaVectors.csv"
LDA_C_CLSFR=$BASE_DIR/$BASE_NAME"_C_CLASSIFIER_LDA"
LDA_P_CLSFR=$BASE_DIR/$BASE_NAME"_P_CLASSIFIER_LDA"

# training flair model
C_CLSFR_FLAIR=$BASE_DIR/$BASE_NAME"_C_CLASSIFIER_FLAIR"
P_CLSFR_FLAIR=$BASE_DIR/$BASE_NAME"_P_CLASSIFIER_FLAIR"

# This is the test set -- same format as DATA_IN
TEST_IN=Data/testrun/ct_report_dmg_thoracic_only.csv
TEST_DIR=$(dirname $TEST_IN)
TEST_NAME=$(basename $TEST_IN .csv)
TEST_OUT_W2V=$TEST_DIR/TEST_NAME"_W2V_classes.csv"
TEST_OUT_LDA=$TEST_DIR/TEST_NAME"_LDA_classes.csv"
TEST_OUT_FLAIR=$TEST_DIR/TEST_NAME"_FLAIR_classes.csv"

# Preprocessing
python cleaning.py --in $DATA_IN --out $CLEAN_DATA

# training word2vec model
python buildw2v.py --in $CLEAN_DATA --out $W2V_MODEL --vectors $W2V_VEC
python trainw2v.py --w2v-vectors $W2V_VEC --in-classes $GT_IN --prog-classifier $W2V_P_CLSFR --cancer-classifier $W2V_C_CLSFR

#training topic model
python buildlda.py --in $CLEAN_DATA --out-dict $LDA_DICT --out-model $LDA_MODEL --out-topics $LDA_VEC
python trainlda.py --lda-vectors $LDA_VEC --in-classes $GT_IN --prog-classifier $LDA_P_CLSFR --cancer-classifier $LDA_C_CLSFR

# training flair model
python buildflair.py --in-reports $CLEAN_DATA --in-classes $GT_IN --cancer-classifier $C_CLSFR_FLAIR --prog-classifier $P_CLSFR_FLAIR

# Apply classifiers
python testw2v.py --in-data $TEST_IN --out-classes $TEST_OUT_W2V --model $W2V_MODEL --prog-classifier $W2V_P_CLSFR --cancer-classifier $W2V_C_CLSFR
python testlda.py --in-data $TEST_IN --out-classes $TEST_OUT_LDA --lda-dict $LDA_DICT --lda-model $LDA_MODEL --prog-classifier $LDA_P_CLSFR --cancer-classifier $LDA_C_CLSFR
python testflair.py  --in-data $TEST_IN --out-classes $TEST_OUT_FLAIR --cancer-classifier $C_CLSFR_FLAIR --prog-classifier $P_CLSFR_FLAIR
