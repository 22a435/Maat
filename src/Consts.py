Consts = {
    "chains": {
        "Celestia": {
            "binary": "celestia-appd",
            "chain-id": "celestia",
            "channels": {"Osmosis": "2", "Penumbra": "35"},
            "denoms": {"TIA": "utia"},
            "gas_price": "0.002utia",
        },
        "Cosmos": {
            "binary": "gaiad",
            "chain-id": "cosmoshub-4",
            "channels": {"Osmosis": "141", "Penumbra": "940"},
            "denoms": {"ATOM": "uatom"},
            "gas_price": "0.005uatom",
        },
        "Noble": {
            "binary": "nobled",
            "chain-id": "noble-1",
            "channels": {"Osmosis": "1", "Penumbra": "89"},
            "denoms": {"USDC": "uusdc", "USDY": "ausdy"},
            "gas_price": "0.1uusdc",
        },
        "Osmosis": {
            "binary": "osmosisd",
            "chain-id": "osmosis-1",
            "channels": {
                "Celestia": "6994",
                "Cosmos": "0",
                "Noble": "750",
                "Penumbra": "79703",
            },
            "denoms": {
                "ATOM": "ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2",
                "OSMO": "uosmo",
                "SHITMOS": "factory/osmo1q77cw0mmlluxu0wr29fcdd0tdnh78gzhkvhe4n6ulal9qvrtu43qtd0nh8/shitmos",
                "TIA": "ibc/D79E7D83AB399BFFF93433E54FAA480C191248FC556924A2A8351AE2638B3877",
                "UM": "ibc/0FA9232B262B89E77D1335D54FB1E1F506A92A7E4B51524B400DC69C68D28372",
                "USDC": "ibc/498A0751C798A0D9A389AA3691123DADA57DAA4FE165D5C75894505B876BA6E4",
                "USDY": "ibc/23104D411A6EB6031FA92FB75F227422B84989969E91DCAD56A535DD7FF0A373",
            },
            "gas_price": "0.0025uosmo",
        },
        "Penumbra": {
            "binary": "pcli",
            "channels": {"Celestia": "3", "Cosmos": "0", "Noble": "2", "Osmosis": "4"},
            "denoms": {
                "ATOM": "transfer/channel-0/uatom",
                "OSMO": "transfer/channel-4/uosmo",
                "SHITMOS": "transfer/channel-4/factory/osmo1q77cw0mmlluxu0wr29fcdd0tdnh78gzhkvhe4n6ulal9qvrtu43qtd0nh8/shitmos",
                "TIA": "transfer/channel-3/utia",
                "UM": "upenumbra",
                "USDC": "transfer/channel-2/uusdc",
                "USDY": "transfer/channel-2/ausdy",
            },
        },
    },
    "tokens": {  # TODO replace const min with calculating $0.01 worth of token at start of arb
        "ATOM": {"decimals": int(1e6), "min": int(1e4), "home": "Cosmos"},
        "OSMO": {"decimals": int(1e6), "min": int(1e5), "home": "Osmosis"},
        "SHITMOS": {"decimals": int(1e6), "min": int(2e6), "home": "Osmosis"},
        "TIA": {"decimals": int(1e6), "min": int(1e4), "home": "Celestia"},
        "UM": {"decimals": int(1e6), "min": int(1e5), "home": "Penumbra"},
        "USDC": {"decimals": int(1e6), "min": int(1e5), "home": "Noble"},
        "USDY": {
            "decimals": int(1e18),
            "min": int(1e17),
            "home": "Noble",
        },
    },
}


def get_binary(chain):
    return Consts["chains"][chain]["binary"]


def get_channel(chain_from, chain_to):
    return Consts["chains"][chain_from]["channels"][chain_to]


def get_chain_id(chain):
    return Consts["chains"][chain]["chain-id"]


def get_denom(chain, token):
    return Consts["chains"][chain]["denoms"][token]


def get_gas_price(chain):
    return Consts["chains"][chain]["gas_price"]


def get_decimals(token):
    return Consts["tokens"][token]["decimals"]


def get_min(token):
    return Consts["tokens"][token]["min"]


def get_home(token):
    return Consts["tokens"][token]["home"]
