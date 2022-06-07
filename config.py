FEE = 0.00005
BPSC_WALLET = './wallets/bpsc_wallet.txt'

def write_amount(wallet, amount):
    with open(wallet, 'w') as f:
        f.write(f"amount: {amount}")

def create_wallet(name):
    with open(f'{name}_wallet.txt', 'w') as f:
        f.write(f"amount: 0")