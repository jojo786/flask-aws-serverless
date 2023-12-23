import os
import boto3
from botocore.config import Config

DBClusterArn = os.environ['DBClusterArn']
DBName = os.environ['DBName']
SecretArn = os.environ['SecretArn']
my_config = Config(
        region_name = os.environ['AWS_REGION'])
client = boto3.client('rds-data', config=my_config)


with open('schema.sql') as file:
    schema = file.read()
    response = client.execute_statement(
                resourceArn=DBClusterArn,
                secretArn=SecretArn,
                database=DBName,
                sql=schema
            ) 

response = client.execute_statement(
                resourceArn=DBClusterArn,
                secretArn=SecretArn,
                database=DBName,
                sql="""
                INSERT INTO posts (title, content) 
                VALUES (:title, :content)
                """,
                parameters=[
                        {
                        'name':'title', 
                        'value':{'stringValue':"First Post"}
                        },
                        {
                        'name':'content', 
                        'value':{'stringValue':"Content for the first post"}
                        }
                    ] 
            ) 

response = client.execute_statement(
                resourceArn=DBClusterArn,
                secretArn=SecretArn,
                database=DBName,
                sql="""
                INSERT INTO posts (title, content) 
                VALUES (:title, :content)
                """,
                parameters=[
                        {
                        'name':'title', 
                        'value':{'stringValue':"Second Post"}
                        },
                        {
                        'name':'content', 
                        'value':{'stringValue':"Content for the second post"}
                        }
                    ] 
            ) 