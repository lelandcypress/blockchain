import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.new_block(previous_hash=1,proof=100)
    def new_block(self, proof, previous_hash=None ):
        #Creates new block, also used for genesis block
        """
        :param proof: <int> the proof given by the Proof of work algo
        :param previous_hash:  (Optional) <str> Hask of previous block
        :return: <dict> New Block
        """
        block={
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),

        }
        self.current_transactions=[]
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction that will go into the next mined block
        :param sender: <str> Address of sender
        :param recipient: <str> Address of recipient
        :param amount:  <int> Amount
        :return: <int> the index of the block that will hold the transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        :param last_proof: <int>
        :return: <int>
        """
        proof=0
        while self.valid_proof(last_proof, proof) is False:
            proof +=1
        return proof
    @staticmethod
    def hash(block):
        """
        :param block: <Dict> BLOCK
        :return: <str>
        """

        block_string= json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def valid_proof(last_proof,proof):
        """
        Does the hash contain 4 leading 0's?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool>
        """
        guess= f'{last_proof}{proof}'.encode()
        guess_hash= hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=="0000"
    @property
    def last_block(self):
        return self.chain[-1]
        #pass is a nice little placeholder that allows you to build the class without throwing an error


app= Flask(__name__)
node_identifier = str(uuid4()).replace('-','')

blockchain=Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof= blockchain.proof_of_work(last_proof)
    blockchain.new_transaction(sender=0, recipient=node_identifier, amount=1)
    previous_hash = blockchain.hash(last_block)
    block= blockchain.new_block(proof, previous_hash)
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash':block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required= ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400
    index= blockchain.new_transaction(values['sender'],values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__== '__main__':
    app.run(host='0.0.0.0', port=5000)
