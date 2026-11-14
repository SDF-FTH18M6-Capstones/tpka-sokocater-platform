
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()


# Enable foreign-key enforcement for SQLite databases
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(connection, connection_record):

    if connection.__class__.__module__.startswith("sqlite3"):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
