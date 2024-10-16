from src.Args import Args, get_rpc, get_wallet
from src.Consts import (
    get_denom,
    get_chain_id,
    get_channel,
    get_home,
    get_binary,
    get_gas_price,
)
from src.Query import (
    get_penumbra_deposit_address,
    get_osmosis_address,
    get_sdk_address,
    await_osmosis_tx,
    await_sdk_tx,
)

import subprocess
import json
import time


def ibc_withdraw(amount, token):
    home = get_home(token)
    if home in ["Osmosis", "Penumbra"]:
        return withdraw("Osmosis", amount, token)
    withdraw(home, amount, token)
    ibc_transfer(home, "Osmosis", amount, token)


def ibc_deposit(amount, token):
    home = get_home(token)
    if home in ["Osmosis", "Penumbra"]:
        return deposit("Osmosis", amount, token)
    ibc_transfer("Osmosis", home, amount, token)
    deposit(home, amount, token)


def ibc_transfer(src, dst, amount, token):
    cmd = [
        get_binary(src),
        "tx",
        "ibc-transfer",
        "transfer",
        "transfer",
        f"channel-{get_channel(src, dst)}",
        get_sdk_address(dst),
        f"{amount}{get_denom(src, token)}",
        f"--node={get_rpc(src)}",
        "--keyring-backend=test",
        f"--chain-id={get_chain_id(src)}",
        "--gas=auto",
        "--gas-adjustment=1.5",
        f"--gas-prices={get_gas_price(src)}",
        f"--from={get_wallet(src)}",
        "--output=json",
        "-y",
    ]
    print("ibc transfer:", cmd)
    r = subprocess.run(cmd, capture_output=True, text=True)

    print("errors: ", r.stderr)
    print("output: ", r.stdout)
    j = json.loads(r.stdout)
    hash = j["txhash"]
    await_sdk_tx(src, hash, 30)
    print(
        "sleeping 90 seconds to avoid IBC spam failures"
    )  # FIXME check ack on receiver chain instead
    time.sleep(90)
    return hash


def withdraw(chain, amount, token):
    match chain:
        case "Noble":
            print("noble withdraw")
            denom = get_denom("Penumbra", token)
            print(f"{amount}{denom}")
            cmd = [
                "pcli",
                "tx",
                "withdraw",
                "--to",
                get_sdk_address("Noble"),
                "--channel",
                get_channel("Penumbra", "Noble"),
                f"{amount}{denom}",
                "--source",
                Args.Penumbra_Account,
                "--use-compat-address",
            ]
            print(cmd)
            r = subprocess.run(cmd, capture_output=True, text=True)
            print("errors: ", r.stderr)
            print("output: ", r.stdout)
            print(
                "sleeping 90 seconds to avoid IBC spam failures"
            )  # FIXME check ack on receiver chain instead
            time.sleep(90)
            return r
        case "Osmosis":
            denom = get_denom("Penumbra", token)
            print(f"{amount}{denom}")
            cmd = [
                "pcli",
                "tx",
                "withdraw",
                "--to",
                get_osmosis_address(),
                "--channel",
                get_channel("Penumbra", "Osmosis"),
                f"{amount}{denom}",
                "--source",
                Args.Penumbra_Account,
            ]
            print(cmd)

            r = subprocess.run(cmd, capture_output=True, text=True)
            print("errors: ", r.stderr)
            print("output: ", r.stdout)
            print(
                "sleeping 90 seconds to avoid IBC spam failures"
            )  # FIXME check ack on receiver chain instead
            time.sleep(90)
            return r


def deposit(chain, amount, token):
    match chain:
        case "Noble":
            print("noble deposit")
            cmd = [
                get_binary(chain),
                "tx",
                "ibc-transfer",
                "transfer",
                "transfer",
                f"channel-{get_channel(chain, 'Penumbra')}",
                get_penumbra_deposit_address(chain == "Noble"),
                f"{amount}{get_denom(chain, token)}",
                f"--node={get_rpc(chain)}",
                "--keyring-backend=test",
                f"--chain-id={get_chain_id(chain)}",
                "--gas=auto",
                "--gas-adjustment=1.5",
                f"--gas-prices={get_gas_price(chain)}",
                f"--from={get_wallet(chain)}",
                "--output=json",
                "--packet-timeout-height=1-1800",
                "-y",
            ]
            print(cmd)
            r = subprocess.run(cmd, capture_output=True, text=True)
            print("errors: ", r.stderr)
            print("output: ", r.stdout)
            j = json.loads(r.stdout)
            hash = j["txhash"]
            await_sdk_tx(chain, hash, 30)
            print(
                "sleeping 90 seconds to avoid IBC spam failures"
            )  # FIXME check ack on receiver chain instead
            time.sleep(90)
            return hash
        case "Osmosis":
            cmd = [
                get_binary(chain),
                "tx",
                "ibc-transfer",
                "transfer",
                "transfer",
                f"channel-{get_channel(chain, 'Penumbra')}",
                get_penumbra_deposit_address(chain == "Noble"),
                f"{amount}{get_denom(chain, token)}",
                f"--node={get_rpc(chain)}",
                "--keyring-backend=test",
                f"--chain-id={get_chain_id(chain)}",
                "--gas=auto",
                "--gas-adjustment=1.5",
                f"--gas-prices={get_gas_price(chain)}",
                f"--from={get_wallet(chain)}",
                "--output=json",
                "-y",
            ]
            print(cmd)
            r = subprocess.run(cmd, capture_output=True, text=True)
            print("errors: ", r.stderr)
            print("output: ", r.stdout)
            j = json.loads(r.stdout)
            hash = j["txhash"]
            await_osmosis_tx(hash, 30)
            print(
                "sleeping 90 seconds to avoid IBC spam failures"
            )  # FIXME check ack on receiver chain instead
            time.sleep(90)
            return hash
