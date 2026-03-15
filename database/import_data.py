import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

# Load CSV
df = pd.read_csv(r"C:\Path\To\MAT1223423432432.csv")

# Create engine
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)

# Import data
df.to_sql("EOL_LEVEL1_MASTER", con=engine, if_exists="append", index=False)

print("✅ Data imported successfully!")