from src.Arbitrage import arbitrage
from src.Rebalance import rebalance
from src.Args import Args


def main():
    print("Hello from Maat!")
    while True:
        rebalance(Args.TokenA, Args.TokenB)
        arbitrage(Args.TokenA, Args.TokenB)


if __name__ == "__main__":
    main()
