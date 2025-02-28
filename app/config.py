import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
# Load environment variables from a .env file
load_dotenv()

# AWS credentials and region
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'AKIAZQ3DSIQ5BGLY355N')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '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')
REGION = os.getenv('REGION', 'us-east-2')
SENDGRID_API_KEY= os.getenv('SENDGRID_API_KEY', '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')
# Database credentials
MSSQLS_PWD = os.getenv('MSSQLS_PWD', 'Ftu5675FDG54hjhiuu$')

# Grok API settings for image processing
GROK_API_KEY = os.getenv('GROK_API_KEY', 'xai-ucA8EcERzruUwHAa1duxYallTxycDumI5n3eVY7EJqhZVD0ywiiza3zEmRB4Tw7eNC5k0VuXVndYOUj9')
GROK_ENDPOINT = os.getenv('GROK_ENDPOINT', 'https://api.x.ai/v1/chat/completions')

# Database connection string
pwd_str = f"Pwd={MSSQLS_PWD};"
conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};Server=35.172.243.170;Database=luxurymarket_p4;Uid=luxurysitescraper;{pwd_str}"
# Database connection strings
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % conn_str)