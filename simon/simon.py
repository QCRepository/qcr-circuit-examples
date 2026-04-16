"""
Simon's Algorithm — finding a hidden period with exponential speedup.

Simon's problem: given a black-box function f: {0,1}^n -> {0,1}^n promised to
be either one-to-one, or two-to-one with f(x) = f(y) iff y = x XOR b for some
hidden bitstring b, determine b. Classically this requires O(sqrt(2^n)) queries
(the birthday bound). Simon's algorithm needs only O(n) quantum queries plus
O(n^3) classical post-processing — the first problem to show an exponential
quantum-over-classical separation.

Each quantum measurement produces a z satisfying z · b = 0 (mod 2). After
collecting enough linearly independent z's, b is uniquely determined as the
non-zero vector orthogonal to all of them. This example constructs an oracle
for a chosen secret b, runs the quantum circuit, and reconstructs b from the
measurement results.
"""

from typing import Optional

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def simon_oracle(b: str) -> QuantumCircuit:
    """Build an oracle circuit implementing a 2-to-1 function with period b.

    Copy |x>|0> -> |x>|x>, then (if b != 0) XOR a "period mark" into the output
    register so that f(x) = f(x XOR b) for all x.
    """
    b_reversed = b[::-1]  # iterate from LSB
    n = len(b_reversed)
    qc = QuantumCircuit(n * 2)

    # Copy the input register into the output register
    for q in range(n):
        qc.cx(q, q + n)

    if "1" in b_reversed:
        # XOR from the first set bit of b into every output qubit where b is 1
        i = b_reversed.find("1")
        for q in range(n):
            if b_reversed[q] == "1":
                qc.cx(i, q + n)

    return qc


def simon_circuit(b: str) -> QuantumCircuit:
    """Full Simon circuit: H on input register, oracle, H again, measure input."""
    n = len(b)
    qc = QuantumCircuit(n * 2, n)
    qc.h(range(n))
    qc.barrier()
    qc = qc.compose(simon_oracle(b))
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def dot_product_mod2(b: str, z: str) -> int:
    """Inner product of two n-bit strings, modulo 2."""
    return sum(int(b[i]) * int(z[i]) for i in range(len(b))) % 2


def candidates_consistent_with(observed_zs: set[str], n: int) -> list[str]:
    """All non-zero b values satisfying z · b = 0 (mod 2) for every observed z."""
    return [
        format(b_int, f"0{n}b")
        for b_int in range(1, 2 ** n)
        if all(dot_product_mod2(format(b_int, f"0{n}b"), z) == 0 for z in observed_zs)
    ]


def z_as_constraint(z: str) -> str:
    """Render the equation z · b = 0 in human-readable form (b[i] indexed positionally)."""
    terms = [f"b[{i}]" for i, bit in enumerate(z) if bit == "1"]
    if not terms:
        return "(trivial)"
    return " + ".join(terms) + " = 0"


if __name__ == "__main__":
    b_secret = "110"
    n = len(b_secret)
    max_queries = 50  # safety cap; expected ~n shots in practice

    circuit = simon_circuit(b_secret)
    simulator = AerSimulator()

    print(f"Simon's Algorithm — secret b = {b_secret} (n = {n})")
    print("Each shot is one quantum query; stopping when b is uniquely determined")
    print(f"by the accumulated linear constraints (mod 2).\n")

    header = f"{'Shot':<6}{'z':<6}{'Constraint':<22}{'b candidates (non-zero)':<30}"
    print(header)
    print("-" * len(header))

    observed_zs: set[str] = set()
    informative_count = 0
    prev_candidates = 2 ** n - 1  # all non-zero b's are initial candidates
    shot = 0
    recovered: Optional[str] = None

    while shot < max_queries:
        shot += 1
        z = next(iter(simulator.run(circuit, shots=1).result().get_counts()))
        observed_zs.add(z)
        candidates = candidates_consistent_with(observed_zs, n)
        if len(candidates) < prev_candidates:
            informative_count += 1
        prev_candidates = len(candidates)

        cand_display = (
            f"{len(candidates)} left: " + ", ".join(candidates)
            if len(candidates) <= 4
            else f"{len(candidates)} of {2 ** n - 1}"
        )
        print(f"  {shot:<4}{z:<6}{z_as_constraint(z):<22}{cand_display:<30}")

        if len(candidates) == 1:
            recovered = candidates[0]
            break

    print("-" * len(header))
    if recovered is None:
        print(f"\nNo unique recovery after {max_queries} shots (extremely unlikely).")
    else:
        print(f"\nRecovered b = {recovered} after {shot} queries "
              f"({informative_count} informative, {shot - informative_count} redundant).")
        print(f"Secret b    = {b_secret}")
        print(f"Match: {'yes' if recovered == b_secret else 'NO'}")
