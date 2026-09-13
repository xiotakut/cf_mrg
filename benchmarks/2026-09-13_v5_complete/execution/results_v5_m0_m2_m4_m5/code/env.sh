#!/usr/bin/env bash
export JAVA_HOME=/home/data3/txy/.local/medrgag-jdk-21
export PATH="$JAVA_HOME/bin:$PATH"
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false
export HF_HUB_OFFLINE=1
