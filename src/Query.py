from src.Args import Args, get_wallet, get_rpc
from src.Consts import get_denom, get_chain_id, get_decimals, get_binary

from functools import cache
import json
import requests
import subprocess
import time


@cache
def get_penumbra_address():
    cmd = ["pcli", "view", "address", Args.Penumbra_Account]
    return subprocess.run(cmd, text=True, capture_output=True).stdout.strip()


def get_penumbra_deposit_address(compat):
    if compat:
        cmd = ["pcli", "view", "address", Args.Penumbra_Account, "-e", "--compat"]
    else:
        cmd = ["pcli", "view", "address", Args.Penumbra_Account, "-e"]
    return subprocess.run(cmd, text=True, capture_output=True).stdout.strip()


@cache
def get_osmosis_address():
    cmd = [
        "osmosisd",
        "keys",
        "show",
        Args.Osmosis_Wallet,
        "--keyring-backend=test",
        "--output=json",
    ]
    return json.loads(subprocess.run(cmd, capture_output=True).stdout)["address"]


@cache
def get_sdk_address(chain):
    cmd = [
        get_binary(chain),
        "keys",
        "show",
        get_wallet(chain),
        "--keyring-backend=test",
        "--output=json",
    ]
    return json.loads(subprocess.run(cmd, capture_output=True).stdout)["address"]


@cache
def get_address(chain):
    match chain:
        case "Penumbra":
            return get_penumbra_address()
        case "Osmosis":
            return get_osmosis_address()


def get_osmosis_balance(token):
    cmd = [
        "osmosisd",
        "q",
        "bank",
        "balance",
        get_osmosis_address(),
        get_denom("Osmosis", token),
        f"--node={Args.Osmosis_RPC}",
        "--output=json",
    ]
    j = json.loads(subprocess.run(cmd, capture_output=True).stdout)
    return int(j["balance"]["amount"])


def parse_penumbra_amount(token, amount):
    if token == "UM":
        r = (lambda line: line[0 : len(line) - len("penumbra")])(amount)
        if r.endswith("u"):
            return int(float(r[:-1]))
        elif r.endswith("m"):
            return int(float(r[:-1]) * 1000)
        return int(float(r) * 1000000)
    return int(
        (lambda line: line[0 : len(line) - len(get_denom("Penumbra", token))])(amount)
    )


def get_penumbra_balance(token):
    if token == "UM":
        denom = "penumbra"
    else:
        denom = get_denom("Penumbra", token)
    cmd = ["pcli", "view", "balance"]
    r = subprocess.run(cmd, text=True, capture_output=True).stdout
    lines = [
        line
        for line in [x.split() for x in r.splitlines()[1:]]
        if line[1] == Args.Penumbra_Account and line[2].endswith(denom)
    ]
    if len(lines) == 0:
        return 0
    return parse_penumbra_amount(token, lines[0][2])


def get_balance(chain, token):
    match chain:
        case "Penumbra":
            return get_penumbra_balance(token)
        case "Osmosis":
            return get_osmosis_balance(token)


def get_tx(chain, hash):
    match chain:
        case "Penumbra":
            return get_penumbra_tx(hash)
        case "Osmosis":
            return get_osmosis_tx(hash)


def get_penumbra_tx(hash):
    cmd = ["pcli", "q", "tx", hash]
    r = subprocess.run(cmd, capture_output=True, text=True).stdout
    return r


def get_osmosis_tx(hash):
    cmd = ["osmosisd", "q", "tx", hash, "--output=json", f"--node={Args.Osmosis_RPC}"]
    r = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if r != "":
        return json.loads(r)
    return r


def get_sdk_tx(chain, hash):
    cmd = [
        get_binary(chain),
        "q",
        "tx",
        hash,
        "--output=json",
        f"--node={get_rpc(chain)}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if r != "":
        return json.loads(r)
    return r


def await_sdk_tx(chain, hash, timeout):
    print("awaiting tx")
    s = time.time()
    while time.time() < s + timeout:
        r = get_sdk_tx(chain, hash)
        if r != "":
            print("tx found")
            return r
        print("looping await tx")
        time.sleep(2)
    print("tx not found after timeout")
    return None


def await_osmosis_tx(hash, timeout):
    print("awaiting tx")
    s = time.time()
    while time.time() < s + timeout:
        r = get_osmosis_tx(hash)
        if r != "":
            print("tx found")
            return r
        print("looping await tx")
        time.sleep(2)
    print("tx not found after timeout")
    return None


def osmosis_swap_tx_to_amount_out(tx, token):
    denom = get_denom("Osmosis", token)

    def parse_attrs(attrs):
        return {a["key"]: a["value"] for a in attrs}

    recvs = [
        parse_attrs(e["attributes"])
        for e in tx["events"]
        if e["type"] == "coin_received"
    ]
    myrecvs = [
        r
        for r in recvs
        if r["receiver"] == get_osmosis_address() and r["amount"].endswith(denom)
    ]
    actual = int(myrecvs[0]["amount"][: -len(denom)])
    return actual


def simulate_osmosis_swap(input, output, amount):
    # print("sim osmo swap", input, output, amount)
    r = requests.post(
        "https://api.skip.build/v2/fungible/route",
        json={
            "amount_in": str(amount),
            "source_asset_denom": get_denom("Osmosis", input),
            "source_asset_chain_id": get_chain_id("Osmosis"),
            "dest_asset_chain_id": get_chain_id("Osmosis"),
            "dest_asset_denom": get_denom("Osmosis", output),
        },
    )
    j = json.loads(r.text)
    expected = int(j["amount_out"])
    path = [
        (x["pool"], x["denom_out"])
        for x in j["operations"][0]["swap"]["swap_in"]["swap_operations"]
    ]
    x = (expected, path)
    print(
        amount / get_decimals(input),
        input,
        "=>",
        expected / get_decimals(output),
        output,
    )
    return x


def simulate_penumbra_swap(input, output, amount):
    cmd = [
        "pcli",
        "q",
        "dex",
        "simulate",
        "--into",
        get_denom("Penumbra", output),
        f"{amount}{get_denom('Penumbra',input)}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = r.stdout.split("via")[0].split("=>")[1].strip()
    v = parse_penumbra_amount(output, out)
    print(amount / get_decimals(input), input, "=>", v / get_decimals(output), output)
    return v
