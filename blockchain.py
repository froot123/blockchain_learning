from functools import reduce
import hashlib
import json
from collections import OrderedDict
import pickle

from hash_util import hash_block, hash_string_256


# Initializing our (empty) blockchain list
MINING_REWARD = 10
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
blockchain = [genesis_block]
open_transactions = []
owner = 'Froot'
participants = {'Froot'}


def load_data():
    try:
        with open('blockchain.txt', 'r') as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()
            global blockchain
            global open_transactions
            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']
            blockchain = json.loads(file_content[0].strip())
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'proof': block['proof'],
                    'transactions': [OrderedDict(
                        [('sender', tx['sender']),
                         ('recipient', tx['recipient']),
                         ('amount', tx['amount'])]) for tx in block['transactions']]
                }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(file_content[1].strip())
            updated_transations = []
            for tx in open_transactions:
                updated_transation = OrderedDict(
                    [('sender', tx['sender']),
                     ('recipient', tx['recipient']),
                     ('amount', tx['amount'])])
                updated_transations.append(updated_transation)
            open_transactions = updated_transations
    except IOError:
        print('File not found!')


load_data()


def save_data():
    with open('blockchain.txt', 'w') as f:
        f.write(json.dumps(blockchain))
        f.write('\n')
        f.write(json.dumps(open_transactions))
        # save_data = {
        #     'chain': blockchain,
        #     'ot': open_transactions
        # }
        # f.write(pickle.dumps(save_data))

def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_hash = hash_block(blockchain[-1])
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_balance(participant):
    tx_sent = [[tx['amount'] for tx in block['transactions']
                if tx['sender'] == participant] for block in blockchain]
    open_tx_sent = [tx['amount']
                    for tx in open_transactions if tx['sender'] == participant]
    tx_sent.append(open_tx_sent)
    amount_sent = reduce(
        lambda x, y: x + sum(y) if len(y) > 0 else x, tx_sent, 0)
    tx_recieved = [[tx['amount'] for tx in block['transactions']
                    if tx['recipient'] == participant] for block in blockchain]
    amount_recieved = reduce(
        lambda x, y: x + sum(y) if len(y) > 0 else x, tx_recieved, 0)
    return amount_recieved - amount_sent


def get_last_blockchain_data():
    """ Returns the last value of the current blockchain. """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Append a new value as well as the last blockchain value to the blockchain."""
    # transaction = {
    #     'sender': sender,
    #     'recipient': recipient,
    #     'amount': amount
    # }
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)

        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD
    # }
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    copied_transactions = open_transactions[:]
    copied_transactions.append(reward_transaction)
    block = {
        'previous_hash': hashed_block,
        'index': len(blockchain),
        'transactions': copied_transactions,
        'proof': proof
    }
    blockchain.append(block)

    return True


def get_transaction_data():
    """ Returns the input of the user (a new transaction amount) as a float. """
    # Get the user input, transform it from a string to a float and store it in user_input
    tx_recipient = input('Enter the recipient of transaction: ')
    tx_amount = float(input('Your transaction amount, please: '))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    # Output the blockchain list to the console
    for block in blockchain:
        print('Outputting Block')
        print(block)


def verify_chain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            print('PoW is invalid!')
            return False
    return True


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Output participants')
    print('h: Manipulate the chain')
    print('q: Quit')
    user_choice = get_user_choice()
    if user_choice == '1':
        recipient, amount = get_transaction_data()
        if add_transaction(recipient, amount=amount):
            print('Transaction success')
        else:
            print('Transaction failure')
        print(open_transactions)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': 'Chris', 'recipient': 'Michael', 'amount': 1.43}]
            }
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Invalid input!!!')

    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format('Froot', get_balance('Froot')))
else:
    print('User left!')


print('Done!')
