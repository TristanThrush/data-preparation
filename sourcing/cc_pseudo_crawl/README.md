# Pseudo-crawl dataset

The scripts in this folder are used to build up a text dataset from the web pages of several domain names.

## Context

For this pipeline, first 605 seeds - grouped under the name seeds batch 1 - were identified. After extracting text from them, a new batch of 9 seeds - grouped under the name  seeds batch 2 - was added in order to obtain more text in certain languages.  Finally, the texts extracted from these two batches of seeds were cleaned and deduplicated.

## Folder organization

All the scripts (bash/slurm) used to extract the text from batch 1 are grouped in the `seeds_batch_1` folder, all those for batch 2 in `seeds_batch_2` and finally the scripts used on both batches in `seeds_batch_1_2`.

In the `python_scripts` folder are the python scripts that are called by the scripts mentioned in the previous paragraph.

Finally, the `language_annotation` folder gathers all the scripts (bash/slurm/python) developed to identify the languages of the texts.

## Pipeline

### Batch 1

- **Step 0**: Create a seed-to-WARC mapping using the index from Common Crawl ([CC](https://commoncrawl.org/)).

  Cross the list of domains names with the web pages available on the CC dumps of 2021 to obtain a mapping.

  <details>
    <summary>This mapping contains the columns:</summary>

        - 'seed_id'
        - 'url_surtkey'
        - 'url_host_tld'
        - 'url_host_registered_domain'
        - 'url_host_name', 'url'
        - 'fetch_status'
        - 'fetch_time'
        - 'warc_filename'
        - 'warc_record_offset'
        - 'warc_record_length'
        - 'fetch_redirect'
        - 'content_mime_detected'
        - 'content_languages’
    </details>

    Link to documentation to reproduce this step: #TODO isolate relevant information from `sourcing/cc_pseudo_crawl/seeds_batch_1/README.md` and probably clean `data-preparation/sourcing/cc_pseudo_crawl/seeds_batch_1/sourcing_sheet_seeds`

1.  **Step 1**: Request Common Crawl to retrieve the WARC files identified in step 0

    a. Download the WARCs in shards

        The idea is to divide the list of WARCS to be recovered into 10 shards so that 10 different jobs can be used to recover the files listed in one of the shards.

        Jobs used:
            - 01_download_warc.slurm
            - 02_download_warc_trial_4.slurm
            - 03_download_warc_trial_5.slurm
            - 04_download_warc_too_big.slurm

    b. 