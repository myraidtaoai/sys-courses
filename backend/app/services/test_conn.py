
import os
import sys
import time
from typing import Literal, Dict, List
from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase

sys.path.append('..')
from config import settings

load_dotenv()
print(os.getenv("GOOGLE_API_KEY"))
database = settings.DATABASE_NAME


db_start = time.time()
sqlite_url = f"sqlite:///../../../database/{database}"
db = SQLDatabase.from_uri(sqlite_url)
db_duration = time.time() - db_start
print(f"🗄️ Database connection in {db_duration*1000:.0f}ms")