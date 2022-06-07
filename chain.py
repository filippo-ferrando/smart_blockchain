import hashlib
import json
from urllib import response

import requests
import config
from time import time
from urllib.parse import urlparse

from flask import Flask, jsonify, request


class Smart_Blockchain:
    def __init__(self):
        self.current_transaction = []
        self.chain = []
        self.nodes = set()

        self.new_block(prev_hash='1')

    def new_block(self, prev_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transaction,
            'prev_hash': prev_hash or self.hash(self.chain[-1]),
        }

        self.current_transaction = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, amount, recipient):
        self.current_transaction.append({
            'sender': sender,
            'amount_send': amount,

            'bpsc': 'bpsc_wallet.txt',
            'amount_bpsc': amount * config.FEE,

            'recipient': recipient,
            'amount_receive': amount * 0.99995,
        })
        config.write_amount(config.BPSC_WALLET, amount * config.FEE)
        return self.last_block['index'] + 1

    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def smart_chain(self):
        schain = None
        response = requests.get(f"http://127.0.0.1:5000/chain")

        if response.status_code == 200:
            chain = response.json()['chain']
            schain = chain

        if schain:
            self.chain = schain
            return True
        return False


    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


app = Flask(__name__)

blockchain = Smart_Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    prev_hash = blockchain.hash(last_block)
    block = blockchain.new_block(prev_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'prev_hash': block['prev_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'amount', 'recipient']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['amount'], values['recipient'])

    response = {'message': f'Transaction will be added to Block {index}'}

    last_block = blockchain.last_block

    prev_hash = blockchain.hash(last_block)
    block = blockchain.new_block(prev_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        prev_hash: block['prev_hash'],
    }

    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply  a valid list of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201

@app.route('/smart/chain', methods=['GET'])
def smart_chain():
    replaced = blockchain.smart_chain()
    
    if replaced:
        response = {
            'message': 'chain update by BSPC',
            'smart chain': blockchain.chain,
            'length': len(blockchain.chain),
        }
    else:
        response = {
            'message': 'chain is up to date | Unsussessful',
            'smart chain': blockchain.chain,
            'length': len(blockchain.chain),
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)