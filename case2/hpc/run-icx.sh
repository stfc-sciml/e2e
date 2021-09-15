#!/bin/bash

export HOME=/localhome/sljack92/

NUM_JOBS=4

TRAIN_DATA_HDF=/localhome/sljack92/git/e2e/data/hdf/one-day
TEST_DATA=/localhome/sljack92/git/e2e/data/ssts
OUTPUT_DIR=/localhome/sljack92/git/e2e/case2/runs/run_j$NUM_JOBS
MODEL_FILE=$OUTPUT_DIR/model.h5

horovodrun -np $NUM_JOBS \
	python e2e_benchmark/command.py train $TRAIN_DATA_HDF $OUTPUT_DIR --epochs 30 --no-cache

horovodrun -np $NUM_JOBS \
	python e2e_benchmark/command.py inference $TEST_DATA $OUTPUT_DIR
