import json
import os
import sqlite3


DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "food_safety.db"
)


def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS blocks (
                block_index INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                hash TEXT NOT NULL,
                nonce INTEGER NOT NULL
            )
            """
        )


def save_block(block):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO blocks (
                block_index, timestamp, data, previous_hash, hash, nonce
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                block.index,
                block.timestamp,
                json.dumps(block.data, sort_keys=True),
                block.previous_hash,
                block.hash,
                block.nonce
            )
        )


def load_blocks():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT block_index, timestamp, data, previous_hash, hash, nonce
            FROM blocks
            ORDER BY block_index
            """
        ).fetchall()

    return [
        {
            "block_index": row["block_index"],
            "timestamp": row["timestamp"],
            "data": json.loads(row["data"]),
            "previous_hash": row["previous_hash"],
            "hash": row["hash"],
            "nonce": row["nonce"]
        }
        for row in rows
    ]
