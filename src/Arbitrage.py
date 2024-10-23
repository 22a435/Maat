from src.Query import (
    simulate_osmosis_swap,
    simulate_penumbra_swap,
    get_osmosis_balance,
    get_penumbra_balance,
)
from src.Consts import get_decimals, get_min
from src.Swap import osmosis_swap, penumbra_swap
import time

min_diff = 0.01
# only search when at least 1% price difference at minimum size


def arbitrage(A, B):
    minA = get_min(A)
    minB = get_min(B)
    maxOA = get_osmosis_balance(A) - minA
    maxOB = get_osmosis_balance(B) - minB
    maxPA = get_penumbra_balance(A) - minA
    maxPB = get_penumbra_balance(B) - minB
    OAB_cache = {}
    OBA_cache = {}
    PAB_cache = {}
    PBA_cache = {}

    def oab_swap(a):
        if a in OAB_cache:
            return OAB_cache[a]
        (o, path) = simulate_osmosis_swap(A, B, a)
        OAB_cache[a] = o
        return o

    def oba_swap(b):
        if B in OBA_cache:
            return OBA_cache[b]
        (o, path) = simulate_osmosis_swap(B, A, b)
        OBA_cache[b] = o
        return o

    def pab_swap(a):
        if a in PAB_cache:
            return PAB_cache[a]
        o = simulate_penumbra_swap(A, B, a)
        PAB_cache[a] = o
        return o

    def pba_swap(b):
        if b in PBA_cache:
            return PBA_cache[b]
        o = simulate_penumbra_swap(B, A, b)
        PBA_cache[b] = o
        return o

    def solve_direction():
        oab_pba = pba_swap(oab_swap(minA)) / minA
        print(f"swap osmosis({A}=>{B}), penumbra({B} => {A})", oab_pba)
        oba_pab = pab_swap(oba_swap(minB)) / minB
        print(f"swap osmosis({B}=>{A}), penumbra({A} => {B})", oba_pab)

        if oab_pba > (1 + min_diff):
            print(f"potential arb: osmosis({A}=>{B}), penumbra({B} => {A})", oab_pba)
            return True
        elif oba_pab > (1 + min_diff):
            print(f"potential arb: osmosis({B}=>{A}), penumbra({A} => {B})", oba_pab)
            return False
        return None

    # successive approximation with 5 sample points spaces across range
    # recursively search subrange bounded by neighbors of best point
    def solve_func(f, low, high, tol):
        if (high - low) < tol:
            return (low + high) // 2

        def i_to_x(i):
            return low + (i * (high - low)) // 4

        points = [(f(i_to_x(i)), i) for i in range(5)]
        (besty, besti) = max(points)

        return solve_func(
            f, max(low, i_to_x(besti - 1)), min(high, i_to_x(besti + 1)), tol
        )

    # solve A->B->A for max profit in A token
    def solve_A(dir):
        if dir:
            return solve_func(
                lambda x: pba_swap(min(maxPB, oab_swap(x))) - x, minA, maxOA, minA
            )
        else:
            return solve_func(
                lambda x: oba_swap(min(maxOB, pab_swap(x))) - x, minA, maxPA, minA
            )

    # solve B->A (assuming AIn -> EBout) for max balanced profit in A and B token
    def solve_B(dir, AIn, EBOut):
        if dir:
            return solve_func(
                lambda y: (pba_swap(y) - AIn) * (EBOut - y) * (EBOut / AIn),
                minB,
                min(EBOut, maxPB),
                minB,
            )
        else:
            return solve_func(
                lambda y: (pba_swap(y) - AIn) * (EBOut - y) * (EBOut / AIn),
                minB,
                min(EBOut, maxOB),
                minB,
            )

    dir = solve_direction()
    if dir is None:
        print("no arb found")
        print("sleeping 300 seconds")
        time.sleep(300)
        return

    if dir:
        AIn = solve_A(dir)
        print("A", AIn / get_decimals(A))
        EBOut = oab_swap(AIn)
        BIn = solve_B(dir, AIn, EBOut)
        print("B", BIn / get_decimals(B))
        EAOut = pba_swap(BIn)
        EBOut = oab_swap(AIn) #recheck incase prices have changed
        print(
            f"best solve: osmosis({AIn/get_decimals(A)} {A} => {EBOut/get_decimals(B)} {B}), penumbra({BIn/get_decimals(B)} {B} => {EAOut/get_decimals(A)} {A})"
        )
        print(
            "Expected Net Effect: ",
            (EAOut - AIn) / get_decimals(A),
            A,
            (EBOut - BIn) / get_decimals(B),
            B,
        )
        if (EAOut - AIn) > 0 and (EBOut - BIn) > 0:
            BOut = osmosis_swap(A, B, AIn)
            AOut = penumbra_swap(B, A, BIn)
            print(
                "Arb Completed, Net Effect: ",
                (AOut - AIn) / get_decimals(A),
                A,
                (BOut - BIn) / get_decimals(B),
                B,
            )
        else:
            print("Expected Net Effect contains a negative profit, skipping")
    else:
        AIn = solve_A(dir)
        print("A", AIn / get_decimals(A))
        EBOut = pab_swap(AIn)
        BIn = solve_B(dir, AIn, EBOut)
        print("B", BIn / get_decimals(B))
        EAOut = oba_swap(BIn)
        print(
            f"best solve: osmosis({BIn/get_decimals(B)} {B} => {EAOut/get_decimals(A)} {A}), penumbra({AIn/get_decimals(A)} {A} => {EBOut/get_decimals(B)} {B})",
        )
        print(
            "Expected Net Effect: ",
            (EAOut - AIn) / get_decimals(A),
            A,
            (EBOut - BIn) / get_decimals(B),
            B,
        )
        if (EAOut - AIn) > 0 and (EBOut - BIn) > 0:
            AOut = osmosis_swap(B, A, BIn)
            BOut = penumbra_swap(A, B, AIn)
            print(
                "Arb Completed, Net Effect: ",
                (AOut - AIn) / get_decimals(A),
                A,
                (BOut - BIn) / get_decimals(B),
                B,
            )
        else:
            print("Expected Net Effect contains a negative profit, skipping")
