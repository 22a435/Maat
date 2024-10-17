import argparse
import tomllib


with open("config.toml", "rb") as f:
    config = tomllib.load(f)

print(config)

parser = argparse.ArgumentParser(
    prog="Maat", description="Penumbra <=> Osmosis rebalancing arbitrage bot"
)

parser.add_argument("--TokenA", default=config.get("TokenA", "UM"))
parser.add_argument("--TokenB", default=config.get("TokenB", "OSMO"))

parser.add_argument(
    "--Celestia_RPC",
    default=config.get("Celestia", {}).get("RPC", "https://celestia-rpc.polkachu.com:443"),
)
parser.add_argument(
    "--Cosmos_RPC",
    default=config.get("Cosmos", {}).get("RPC", "https://cosmos-rpc.polkachu.com"),
)
parser.add_argument(
    "--Noble_RPC",
    default=config.get("Noble", {}).get("RPC", "https://noble-rpc.polkachu.com:443"),
)
parser.add_argument(
    "--Osmosis_RPC",
    default=config.get("Osmosis", {}).get("RPC", "https://rpc.osmosis.zone"),
)
parser.add_argument(
    "--Penumbra_RPC",
    default=config.get("Penumbra", {}).get("RPC", "https://void.s9.gay"),
)


parser.add_argument(
    "--Celestia_Wallet", default=config.get("Celestia", {}).get("Wallet", "Maat")
)
parser.add_argument(
    "--Cosmos_Wallet", default=config.get("Cosmos", {}).get("Wallet", "Maat")
)
parser.add_argument(
    "--Noble_Wallet", default=config.get("Noble", {}).get("Wallet", "Maat")
)
parser.add_argument(
    "--Osmosis_Wallet", default=config.get("Osmosis", {}).get("Wallet", "Maat")
)
parser.add_argument(
    "--Penumbra_Account", default=config.get("Penumbra", {}).get("Account", "0")
)

Args = parser.parse_args()


def get_rpc(chain):
    return vars(Args)[f"{chain}_RPC"]


def get_wallet(chain):
    return vars(Args)[f"{chain}_Wallet"]
