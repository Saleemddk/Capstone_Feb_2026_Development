from io import StringIO

import boto3
import pandas as pd
from sqlalchemy import create_engine
import cx_Oracle
import logging
import paramiko

# Logging configuration
from project_config.etlconfig import *

logging.basicConfig(
    filename="application_logs/etljob.log",
    filemode='a',
    format='%(asctime)s-%(levelname)s-%(message)s',
    level=logging.INFO )
logger = logging.getLogger(__name__)

def read_file_and_write_to_database(file_path,file_type):
    if file_type =='csv':
        df = pd.read_csv(file_path)
    elif file_type =='json':
        df = pd.read_json(file_path)
    elif file_type =='xml':
        df = pd.read_xml(file_path,xpath=".//item")
    else:
        raise ValueError(f"unsupported file type passed {file_type}")
    return df

def download_file_from_linux():
    logger.info("product file download from linux server has started...")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(LIUNX_HOSTNAME,username=LIUNX_USERNAME,password=LIUNX_PASSWORD)
    sftp = ssh_client.open_sftp()
    sftp.get(REMOTE_FILE_PATH,LOCAL_FILE_PATH)
    sftp.close()
    logger.info("product file download from linux server has completed...")


# initialize the connection
s3 = boto3.client("s3")
def read_file_from_s3_and_write_to_database(bucket_name,file_key):
    # fetch the csv file from S3
    try:
        response = s3.get_object(Bucket=bucket_name,Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        data = StringIO(csv_content)
        df = pd.read_csv(data)
        return df
    except Exception as e:
        logger.error(f"exception raised while reading from S3 {e}", exc_info=True)


