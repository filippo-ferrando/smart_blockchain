from datetime import datetime
FEE = 0.00005
BPSC_WALLET = './wallets/bpsc_wallet.txt'

def write_amount(wallet, amount):
    with open(wallet, 'a') as f:
        f.write(f"{datetime.now} - amount: {amount}")

def create_wallet(name):
    with open(f'{name}_wallet.txt', 'a') as f:
        f.write(f"amount: 0")