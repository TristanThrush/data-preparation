conda activate dedup-dataset

DATA_TOOLING_REPO=/home/lucile/code/data_tooling

DATASET_PATH=/home/lucile/data/tokenization_dataset/alpha_arrow
SAVE_DATASET_DIR=/home/lucile/data/tokenization_dataset/alpha_arrow-dedup

pushd $DATA_TOOLING_REPO

export HF_DATASETS_OFFLINE=1
export HF_DATASETS_CACHE=/home/lucile/to_delete

python tokenizer/python_script/dedup_lines.py \
    --save-dir $SAVE_DATASET_DIR \
    --dataset_dir $DATASET_PATH \
    --batch-size 1000 \
    --num-proc 1 \
    --min-chars 0 \
    --n-records 57290988 \
    --min-repetition-threshold 0 \
    --preserve_code \
    --with-meta-col