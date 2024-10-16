from src.Args import Args, get_rpc, get_wallet
from src.Consts import get_denom, get_chain_id, get_decimals, get_gas_price
from src.Query import (
    await_osmosis_tx,
    simulate_osmosis_swap,
    osmosis_swap_tx_to_amount_out,
    parse_penumbra_amount,
)

import subprocess
import json


def osmosis_swap(input, output, amount):
    slippage = 0.05
    (expected, path) = simulate_osmosis_swap(input, output, amount)
    ids = f"--swap-route-pool-ids={','.join([p[0] for p in path])}"
    denoms = f"--swap-route-denoms={','.join([p[1] for p in path])}"
    cmd = [
        "osmosisd",
        "tx",
        "poolmanager",
        "swap-exact-amount-in",
        f"{amount}{get_denom('Osmosis',input)}",
        str(int((1 - slippage) * expected)),
        f"--node={get_rpc('Osmosis')}",
        "--keyring-backend=test",
        f"--chain-id={get_chain_id('Osmosis')}",
        "--gas=auto",
        "--gas-adjustment=1.5",
        f"--gas-prices={get_gas_price('Osmosis')}",
        f"--from={get_wallet('Osmosis')}",
        "--output=json",
        denoms,
        ids,
        "-y",
    ]
    print(cmd)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("errors: ", r.stderr)
    print("output: ", r.stdout)
    j = json.loads(r.stdout)
    hash = j["txhash"]
    tx = await_osmosis_tx(hash, 30)
    actual = osmosis_swap_tx_to_amount_out(tx, output)

    print(
        "Swapped on Osmosis: ",
        amount / get_decimals(input),
        input,
        "=>",
        actual / get_decimals(output),
        output,
    )
    return actual


def penumbra_swap(input, output, amount):
    cmd = [
        "pcli",
        "tx",
        "swap",
        "--into",
        get_denom("Penumbra", output),
        f"{amount}{get_denom('Penumbra', input)}",
        "--source",
        Args.Penumbra_Account,
    ]
    print(cmd)
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("errors: ", r.stderr)
    print("output: ", r.stdout)

    try:
        t = r.stdout
        o = t.split("You will receive outputs of ")
        x = o[1].split(". Claiming now...")[0]
        oa = x.split(" and ")
        print(oa)
        if oa[0].startswith("0"):  # TODO parse both amounts and get output
            actual = parse_penumbra_amount(output, oa[1])
        else:
            actual = parse_penumbra_amount(output, oa[0])
        print(
            "Swapped on Penumbra: ",
            amount / get_decimals(input),
            input,
            "=>",
            actual / get_decimals(output),
            output,
        )

        return actual
    except:
        print("Penumbra Swap error, presume failed")
        return 0
