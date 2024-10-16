# Maat
A Program to profitably rebalance prices between Penumbra and Osmosis.
(aka an arbitrage bot)
## Setup
Program expects chain binaries to be available in path, with wallets initialized and appropriate balances available. `pcli` should be initialized with `soft-kms` and GRPC of choice. Cosmos-SDK binaries should have keys loaded into `keyring-backend=test`.
### Example
`pcli init --grpc-url https://void.s9.gay soft-kms generate`

`osmosisd keys add Maat --keyring-backend=test`

## Usage
Project is managed with the python package/project manager [uv](https://github.com/astral-sh/uv).

Runtime configuration can be provided with `config.toml`, or with command line arguments which override config file values.
### Example `config.toml`
```
TokenA = "UM"
TokenB = "OSMO"

[Osmosis]
RPC = "https://rpc.osmosis.zone"
Wallet = "Maat"

[Penumbra]
RPC = "https://void.s9.gay"
Account = "0"
```
### Default Usage
`uv run maat.py`
### Equivalent Args
`uv run maat.py --TokenA UM --TokenB OSMO --Osmosis_Wallet Maat --Penumbra_Account 0`
### UM/USDC Example
`uv run maat.py --TokenA UM --TokenB USDC --Osmosis_Wallet Maat --Noble_Wallet Maat --Penumbra_Account 1`