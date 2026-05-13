import pandas as pd
from sqlalchemy import create_engine
import cx_Oracle
import logging

# Logging configuration
from common_utilities.utilities import read_file_and_write_to_database
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

class DataTransformation:

    def transform_filter_sales_data(self):
        logger.info("Filter Transformation on sales data has started...")
        query = """select * from stag_sales where sale_date >= '2025-09-10'"""
        df = pd.read_sql(query,mysql_engine)
        df.to_sql("filtered_sales", mysql_engine, index=False)
        logger.info("Filter Transformation on sales data has completed...")

    def transform_router_sales_data_High_Region(self):
        logger.info("Router Transformation for High sales data has started...")
        query = """select * from filtered_sales where region='High'"""
        df = pd.read_sql(query,mysql_engine)
        df.to_sql("high_sales", mysql_engine, index=False)
        logger.info("Router Transformation for High sales data has completed...")

    def transform_router_sales_data_Low_Region(self):
        logger.info("Router Transformation for Low sales data has started...")
        query = """select * from filtered_sales where region='Low'"""
        df = pd.read_sql(query, mysql_engine)
        df.to_sql("low_sales", mysql_engine, index=False)
        logger.info("Router Transformation for Low sales data has completed...")

    def transform_aggregator_sales_data(self):
        logger.info("Aggregator Transformation for sales data has started...")
        query = """select product_id,year(sale_date) as year, month(sale_date) as month ,sum(quantity*price) as total_sales from filtered_sales
                    group by product_id,year(sale_date),month(sale_date)"""
        df = pd.read_sql(query, mysql_engine)
        df.to_sql("monthly_sales_summary_source", mysql_engine, index=False)
        logger.info("Aggregator Transformation for sales data has completed...")

    def transform_joiner_sales_product_stores(self):
        logger.info("Joiner Transformation for sales data has started...")
        query = """select fs.sales_id,fs.quantity,fs.price,fs.quantity*fs.price as sales_amount,fs.sale_date,p.product_id,p.product_name,s.store_id,s.store_name
                    from filtered_sales as fs inner join stag_product as p on fs.product_id = p.product_id
                    inner join stag_stores as s on fs.store_id = s.store_id"""
        df = pd.read_sql(query, mysql_engine)
        df.to_sql("sales_with_details", mysql_engine, index=False)
        logger.info("Joiner Transformation for sales data has completed...")

    def transform_aggregator_inventory_level(self):
        logger.info("Aggregator  Transformation for inventory data has started...")
        query = """select store_id,sum(quantity_on_hand) as total_inventory from stag_inventory group by store_id"""
        df = pd.read_sql(query, mysql_engine)
        df.to_sql("aggregated_inventory_level", mysql_engine, index=False)
        logger.info("Aggregator  Transformation for inventory data has completed...")


if __name__ == "__main__":
    dt = DataTransformation()
    dt.transform_filter_sales_data()
    dt.transform_router_sales_data_Low_Region()
    dt.transform_router_sales_data_High_Region()
    dt.transform_aggregator_sales_data()
    dt.transform_joiner_sales_product_stores()
    dt.transform_aggregator_inventory_level()

