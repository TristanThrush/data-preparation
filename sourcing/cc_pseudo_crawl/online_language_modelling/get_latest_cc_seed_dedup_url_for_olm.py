import subprocess
import logging
from argparse import ArgumentParser
from pyathena import connect
import boto3


logging.basicConfig(
    level="INFO", format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


parser = ArgumentParser()
parser.add_argument("--cc-dump", type=str, required=True)

args = parser.parse_args()

s3_location="s3://olm-pseudo-crawl"

cursor = connect(
    s3_staging_dir="{}/staging".format(s3_location), region_name="us-east-1", work_group="olm"
).cursor()

s3 = boto3.resource('s3')
bucket = s3.Bucket('olm-pseudo-crawl')
bucket.objects.filter(Prefix="cc-seed/").delete()
bucket.objects.filter(Prefix="cc-seed_dedup_url").delete()

drop_cc_seed = "DROP TABLE IF EXISTS olm.cc_seed"
cursor.execute(drop_cc_seed)
logging.info("Athena query: %s", drop_cc_seed)

drop_cc_seed_dedup_url = "DROP TABLE IF EXISTS olm.cc_seed_dedup_url"
cursor.execute(drop_cc_seed_dedup_url)
logging.info("Athena query: %s", drop_cc_seed_dedup_url)

update_cc_index = "MSCK REPAIR TABLE olmccindex;"
cursor.execute(update_cc_index)
logging.info("Athena query: %s", update_cc_index)

subprocess.call(f"python3 ../python_scripts/cc_lookup_seed.py {s3_location} seed {args.cc_dump}", shell=True)

create_cc_seed = f"""
CREATE EXTERNAL TABLE olm.cc_seed (
    seed_id                     INT,
    url_surtkey                 STRING,
    url_host_tld                STRING,
    url_host_registered_domain  STRING,
    url_host_name               STRING,
    url                         STRING,
    fetch_status              SMALLINT,
    fetch_time               TIMESTAMP,
    warc_filename               STRING,
    warc_record_offset             INT,
    warc_record_length             INT,
    fetch_redirect              STRING,
    content_mime_detected       STRING,
    content_languages           STRING)
PARTITIONED BY (
    crawl STRING,
    subset STRING)
STORED AS parquet
LOCATION '{s3_location}/cc-seed/'
TBLPROPERTIES (
  'has_encrypted_data'='false',
  'parquet.compression'='GZIP');
 """
cursor.execute(create_cc_seed)
logging.info("Athena query: %s", create_cc_seed)

load_cc_seed_partitions = f"MSCK REPAIR TABLE olm.cc_seed;"
cursor.execute(load_cc_seed_partitions)
logging.info("Athena query: %s", load_cc_seed_partitions)

deduplicate_cc_seed = f"""
 CREATE TABLE IF NOT EXISTS olm.cc_seed_dedup_url
  WITH (external_location = '{s3_location}/cc-seed_dedup_url/',
        partitioned_by = ARRAY['crawl', 'subset'],
        format = 'PARQUET',
        parquet_compression = 'GZIP')
  AS
  WITH tmp AS (
      SELECT *, row_number() over (partition by url order by fetch_time desc) row
      FROM olm.cc_seed
  )

  SELECT
     seed_id,
     url,
     url_surtkey,
     url_host_tld,
     url_host_registered_domain,
     url_host_name,
     fetch_status,
     fetch_time,
     warc_filename,
     warc_record_offset,
     warc_record_length,
     fetch_redirect,
     content_mime_detected,
     content_languages,
     crawl,
     subset
  FROM tmp
  WHERE row = 1
  """
cursor.execute(deduplicate_cc_seed)
logging.info("Athena query: %s", deduplicate_cc_seed)