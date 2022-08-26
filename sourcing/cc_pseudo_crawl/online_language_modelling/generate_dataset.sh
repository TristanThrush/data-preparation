python get_latest_cc_seed_dedup_url_for_olm.py --cc-dump=CC-MAIN-2022-27 --s3-location=s3://olm-pseudo-crawl
aws s3 cp --recursive {s3_location}/cc-{crawl}-{crawl_selector}-dedup-url/subset=warc cc-seed_dedup_url/subset=warc
python ../python_scripts/download_warc.py --dataset=bigscience-catalogue-data/pseudo_crawl_seed_dedup_url --cc-index-folder=. --save_dir=datasets --num_proc=96
python ../python_scripts/preprocess_dataset.py --dataset-path=datasets/bigscience-catalogue-data/pseudo_crawl_seed_dedup_url/ --num-proc=96 --save-path=datasets-preprocessed/bigscience-catalogue-data/ --use-datasets-caching --flavor=seed
export HF_DATASETS_OFFLINE=1
export WANDB_MODE=offline
export WANDB_DIR=$SCRATCH
python ../python_scripts/extract_text/extract_text_and_html_metadata.py out_dir=$(pwd)/datasets-preprocessed-text-extracted/bigscience-catalogue-data/ dataset_name=$(pwd)/datasets-preprocessed/bigscience-catalogue-data/ metadata_to_include='["website_description", "entity", "timestamp", "html"]' project_name=pseudo_crawl_extract use_load_from_disk=true task_id=0 num_files_to_process=1 preprocessing_num_workers=96
