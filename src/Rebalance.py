from src.Query import get_osmosis_balance, get_penumbra_balance, get_decimals
from src.IBC import ibc_deposit, ibc_withdraw


def rebalance(A, B):
    for token in [A, B]:
        print("Rebalancing: ", token)
        ob = get_osmosis_balance(token)
        print("Osmosis Balance", ob / get_decimals(token), token)
        pb = get_penumbra_balance(token)
        print("Penumbra Balance", pb / get_decimals(token), token)
        if pb > 2 * ob:
            print("Moving", pb - (pb + ob) // 2, token, "from Penumbra to Osmosis")
            ibc_withdraw(pb - (pb + ob) // 2, token)
        elif ob > pb * 2:
            print("Moving", ob - (pb + ob) // 2, token, "from Osmosis to Penumbra")
            ibc_deposit(ob - (pb + ob) // 2, token)
        else:
            print(token, "Balances with 1/3 - 2/3 range")
