import pandas as pd
from sqlalchemy import create_engine
import cx_Oracle
import logging

# Logging configuration
from common_utilities.utilities import read_file_and_write_to_database, download_file_from_linux, \
    read_file_from_s3_and_write_to_database
from project_config.etlconfig import *

logging.basicConfig(
    filename="application_logs/etljob.log",
    filemode='w',
    format='%(asctime)s-%(levelname)s-%(message)s',
    level=logging.INFO )
logger = logging.getLogger(__name__)


# database connection
oracle_engine = create_engine(f"oracle+cx_oracle://{ORACLE_USER}:{ORACLE_PASSWORD}@{ORACLE_HOST}:{ORACLE_PORT}/{ORACLE_SERVICE}")
mysql_engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")


class DataExtrcation:

    def extract_sales_data_load_stage(self,bucket_name,file_key):
        logger.info("Data extrcation for sales data has started...")
        try:
            df = read_file_from_s3_and_write_to_database(bucket_name,file_key)
            df.to_sql("stag_sales",mysql_engine,index=False)
            logger.info("Data extrcation for sales data has completed...")
        except Exception as e:
            logger.error(f"Error encountered while data extrcation of sales data,{e},exc_info=True")

    def extract_product_data_load_stage(self,file_path,file_type):
        logger.info("Data extrcation for product data has started...")
        download_file_from_linux()
        df = read_file_and_write_to_database(file_path,file_type)
        df.to_sql("stag_product",mysql_engine,index=False)
        logger.info("Data extrcation for product data has completed...")

    def extract_inventory_data_load_stage(self,file_path,file_type):
        logger.info("Data extrcation for inventory data has started...")
        df = read_file_and_write_to_database(file_path,file_type)
        df.to_sql("stag_inventory",mysql_engine,index=False)
        logger.info("Data extrcation for inventory data has completed...")

    def extract_supplier_data_load_stage(self,file_path,file_type):
        logger.info("Data extrcation for supplier data has started...")
        df = read_file_and_write_to_database(file_path,file_type)
        df.to_sql("stag_supplier", mysql_engine, index=False)
        logger.info("Data extrcation for supplier data has completed...")

    def extract_stores_data_load_stage(self):
        logger.info("Data extrcation for stores data has started...")
        df = pd.read_sql("""select * from stores""",oracle_engine)
        df.to_sql("stag_stores", mysql_engine,if_exists ='replace', index=False)
        logger.info("Data extrcation for stores data has completed...")

if __name__ == "__main__":
    de = DataExtrcation()
    de.extract_sales_data_load_stage(bucket_name=S3_BUCKET_NAME,file_key=FILE_KEY)
    #de.extract_sales_data_load_stage("source_systems/sales_data.csv","csv")
    de.extract_product_data_load_stage("source_systems/product_data_from_linux.csv","csv")
    de.extract_inventory_data_load_stage("source_systems/inventory_data.xml","xml")
    de.extract_supplier_data_load_stage("source_systems/supplier_data.json","json")
    de.extract_stores_data_load_stage()

