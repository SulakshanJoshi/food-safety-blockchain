from flask import Flask, render_template, request, redirect

from blockchain import FoodSafetyBlockchain
from database import initialize_database, load_blocks, save_block


app = Flask(__name__)


SUPPLY_CHAIN_STAGES = [
    ("Farm", "Registered"),
    ("Processing", "Passed"),
    ("Quality Inspection", "Passed"),
    ("Transportation", "In Transit"),
    ("Warehouse", "Stored"),
    ("Retail", "Available")
]


initialize_database()


def load_blockchain():

    saved_blocks = load_blocks()

    if saved_blocks:
        return FoodSafetyBlockchain.from_records(saved_blocks)

    blockchain = FoodSafetyBlockchain()

    save_block(blockchain.chain[0])

    return blockchain


# Load the existing blockchain, or create and save its Genesis Block once.
food_blockchain = load_blockchain()


def batch_records(batch_id):

    return [
        block
        for block in food_blockchain.chain
        if block.data.get("batch_id") == batch_id
    ]


def get_dashboard_stats():

    batches = {}

    for block in food_blockchain.chain:

        batch_id = block.data.get("batch_id")

        if batch_id:

            batches.setdefault(batch_id, [])

            batches[batch_id].append(block)


    total_batches = len(batches)


    total_blocks = len(food_blockchain.chain)


    completed_journeys = 0

    for records in batches.values():

        latest_stage = records[-1].data.get("stage")

        if latest_stage == "Retail":

            completed_journeys += 1


    blockchain_valid = food_blockchain.is_chain_valid()


    return {
        "total_batches": total_batches,
        "total_blocks": total_blocks,
        "completed_journeys": completed_journeys,
        "blockchain_valid": blockchain_valid
    }


def show_error(message):

    stats = get_dashboard_stats()

    return render_template(
        "index.html",
        blockchain=food_blockchain.chain,
        error=message,
        stats=stats
    )


@app.route("/")
def home():

    stats = get_dashboard_stats()

    return render_template(
        "index.html",
        blockchain=food_blockchain.chain,
        stats=stats
    )


@app.route("/add_product", methods=["POST"])
def add_product():

    product = request.form["product"]

    batch_id = request.form["batch_id"]

    producer = request.form["producer"]


    if batch_records(batch_id):

        return show_error(
            f"Batch ID '{batch_id}' is already registered. "
            "Use a new Batch ID for a new product."
        )


    food_data = {
        "product": product,
        "batch_id": batch_id,
        "producer": producer,
        "stage": "Farm",
        "status": "Registered"
    }


    new_block = food_blockchain.add_block(food_data)

    save_block(new_block)


    return redirect("/")


@app.route("/update_stage", methods=["POST"])
def update_stage():

    batch_id = request.form["batch_id"]

    stage = request.form["stage"]

    location = request.form["location"]

    temperature = request.form["temperature"]

    status = request.form["status"]


    records = batch_records(batch_id)


    if not records:

        return show_error(
            f"Batch ID '{batch_id}' is not registered."
        )


    current_stage = records[-1].data.get("stage")


    current_stage_index = next(
        (
            index
            for index, (saved_stage, _) in enumerate(
                SUPPLY_CHAIN_STAGES
            )
            if saved_stage == current_stage
        ),
        None
    )


    if current_stage_index is None:

        return show_error(
            f"Batch ID '{batch_id}' has an unrecognized "
            "current stage and cannot be updated automatically."
        )


    if current_stage_index == len(SUPPLY_CHAIN_STAGES) - 1:

        return show_error(
            f"Batch ID '{batch_id}' has already completed "
            "its supply-chain journey."
        )


    expected_stage, expected_status = (
        SUPPLY_CHAIN_STAGES[current_stage_index + 1]
    )


    if stage != expected_stage:

        return show_error(
            f"The next stage for Batch ID '{batch_id}' "
            f"must be '{expected_stage}', not '{stage}'."
        )


    if status != expected_status:

        return show_error(
            f"The status for '{stage}' must be "
            f"'{expected_status}'."
        )


    stage_data = {
        "batch_id": batch_id,
        "stage": stage,
        "location": location,
        "temperature": temperature,
        "status": status
    }


    new_block = food_blockchain.add_block(stage_data)

    save_block(new_block)


    return redirect("/")


@app.route("/validate")
def validate_blockchain():

    is_valid = food_blockchain.is_chain_valid()


    if is_valid:

        message = (
            "✅ Blockchain is valid and has not been tampered with."
        )

    else:

        message = (
            "❌ Blockchain is invalid. "
            "Data may have been tampered with."
        )


    stats = get_dashboard_stats()


    return render_template(
        "index.html",
        blockchain=food_blockchain.chain,
        validation_message=message,
        stats=stats
    )


@app.route("/batch/<batch_id>")
def view_batch(batch_id):

    batch_records_list = []


    for block in food_blockchain.chain:

        if block.data.get("batch_id") == batch_id:

            batch_records_list.append({
                "stage": block.data.get("stage"),
                "location": block.data.get("location"),
                "temperature": block.data.get("temperature"),
                "status": block.data.get("status"),
                "timestamp": block.timestamp
            })


    return render_template(
        "batch.html",
        batch_id=batch_id,
        records=batch_records_list
    )


@app.route("/blockchain")
def view_blockchain():

    return {
        "blockchain": [
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "previous_hash": block.previous_hash,
                "hash": block.hash,
                "nonce": block.nonce
            }

            for block in food_blockchain.chain
        ]
    }


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5002
    )