import os

# Set required env vars before any lambda module is imported during test collection
os.environ.setdefault("TEMP_DB_TABLE_NAME", "test-table")
