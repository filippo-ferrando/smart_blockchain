import hashlib
import json
from urllib import response

import config
import requests
from time import time
from urllib.parse import urlparse

from flask import Flask, jsonify, request


class Smart_Blockchain:
    def __init__(self):
        self.current_information = []
        self.chain = [] #public blockchain (bspc)
        self.chain2 = [] #personal blockchain
        self.nodes = set()
        
        self.new_block(prev_hash='1') #genesis block personal chain


    def register_node(self, address):   #register new node
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def new_block(self, prev_hash): #new block personal chain
        block = {
            'index2': len(self.chain2) + 1,
            'timestamp': time(),
            'information': self.current_information,
            'prev_hash': prev_hash or self.hash(self.chain2[-1]),
        }

        self.current_information = []
        self.chain2.append(block)
        return block
    
    def new_information(self, information): #new information personal chain
        self.current_information.append({
            'information': information,
        })

        return self.last_block['index2'] + 1


    def smart_chain(self): #update local (remote) chain (BSPC)
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
        return self.chain2[-1]

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
        'message': "New Block Forged",
        'index2': block['index2'],
        'information': block['information'],
        'prev_hash': block['prev_hash'],
    }
    return jsonify(response), 200

@app.route('/information/new', methods=['POST'])
def new_information():
    values = request.get_json()

    required = ['information']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_information(values['information'])
    
    response = {'message': f'information will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET']) #return remote chain
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/chain2', methods=['GET']) #return personal chain
def full_chain2():
    response = {
        'chain2': blockchain.chain2,
        'length': len(blockchain.chain2),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST']) #add new node to nodes list
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

@app.route('/nodes/register/chain', methods=['POST']) #add new node to nodes list
def register_node_chain():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: Please supply  a valid list of nodes', 400

    response = requests.post(f"http://127.0.0.1:5000/nodes/register", json={"nodes": f"{nodes}"})
    

    return response.content, 201

@app.route('/smart/chain', methods=['GET']) #update local (remote) chain
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

    parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port, debug=True)