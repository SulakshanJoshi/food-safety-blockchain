import hashlib
import json
from datetime import datetime


class Block:
    def __init__(
        self,
        index,
        timestamp,
        data,
        previous_hash,
        nonce=0,
        block_hash=None
    ):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = block_hash if block_hash is not None else self.calculate_hash()

    def calculate_hash(self):
        block_string = (
            str(self.index)
            + str(self.timestamp)
            + json.dumps(self.data, sort_keys=True)
            + str(self.previous_hash)
            + str(self.nonce)
        )

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()


class FoodSafetyBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 3

    def create_genesis_block(self):
        return Block(
            0,
            str(datetime.now()),
            {"message": "Genesis Block - Food Safety Tracker"},
            "0"
        )

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_latest_block()

        new_block = Block(
            len(self.chain),
            str(datetime.now()),
            data,
            previous_block.hash
        )

        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

        return new_block

    @classmethod
    def from_records(cls, records):
        """Rebuild a blockchain from blocks stored in SQLite."""
        blockchain = cls.__new__(cls)
        blockchain.difficulty = 3
        blockchain.chain = [
            Block(
                index=record["block_index"],
                timestamp=record["timestamp"],
                data=record["data"],
                previous_hash=record["previous_hash"],
                nonce=record["nonce"],
                block_hash=record["hash"]
            )
            for record in records
        ]
        return blockchain

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True


if __name__ == "__main__":
    blockchain = FoodSafetyBlockchain()

    blockchain.add_block({
        "product": "Milk",
        "batch_id": "MILK001",
        "stage": "Farm",
        "status": "Passed"
    })

    blockchain.add_block({
        "product": "Milk",
        "batch_id": "MILK001",
        "stage": "Quality Inspection",
        "temperature": "4°C",
        "status": "Passed"
    })

    for block in blockchain.chain:
        print("\n-------------------------")
        print("Block:", block.index)
        print("Data:", block.data)
        print("Hash:", block.hash)
        print("Previous Hash:", block.previous_hash)
        print("Nonce:", block.nonce)

    print("\nBlockchain Valid:", blockchain.is_chain_valid())
