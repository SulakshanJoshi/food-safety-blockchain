# Blockchain Based Food Safety Tracker

A web-based food safety and supply chain tracking system built using Python, Flask, SQLite, and Blockchain technology.

The system records the different stages of a food product's journey in a blockchain. Each supply-chain event is stored as a block containing product information, location, temperature, status, timestamp, and cryptographic hashes.

## Features

- Register new food products with a unique Batch ID
- Track products through different supply-chain stages
- Enforce the correct order of supply-chain stages
- Store blockchain records permanently using SQLite
- SHA-256 hashing for blockchain integrity
- Proof-of-Work mining for new blocks
- Detect blockchain tampering
- View the complete journey of a batch
- Dashboard showing blockchain and batch statistics
- Web-based interface using Flask, HTML, CSS, and JavaScript

## Supply Chain Stages

The system follows this sequence:

Farm → Processing → Quality Inspection → Transportation → Warehouse → Retail

Each stage must be completed in the correct order before the product can move to the next stage.

## Technologies Used

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript
- SHA-256 Cryptographic Hashing
- Blockchain
- Proof of Work

## How It Works

First, a food product is registered with a unique Batch ID. A blockchain block is created containing the product and producer information.

As the product moves through the supply chain, new events are added as new blocks. Each block contains the hash of the previous block, creating a chain of connected records.

The system also verifies the blockchain whenever required. If any stored block is modified, its hash will no longer match its calculated hash, allowing the system to detect possible tampering.

## Project Structure

```text
food-safety-blockchain/
│
├── app.py
├── blockchain.py
├── database.py
├── requirements.txt
├── .gitignore
│
├── static/
│   ├── style.css
│   └── warm.css
│
├── templates/
│   ├── index.html
│   └── batch.html
│
└── data/
    └── food_safety.db