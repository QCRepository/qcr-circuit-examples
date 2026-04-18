"""
Deutsch-Jozsa Algorithm implementation.

Determines whether a Boolean function is constant or balanced
using a single quantum query, demonstrating quantum advantage
over classical algorithms.
"""

import argparse

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def dj_oracle(case: str, n: int) -> QuantumCircuit:
    """
    Create a Deutsch-Jozsa oracle.

    Args:
        case: Either 'balanced' or 'constant'
        n: Number of input qubits

    Returns:
        Oracle as a quantum gate
    """
    oracle_qc = QuantumCircuit(n + 1)

    if case == "balanced":
        # Random bit string determines X-gate placement
        b = np.random.randint(1, 2**n)
        b_str = format(b, "0" + str(n) + "b")

        # Apply X-gates based on bit string
        for qubit in range(len(b_str)):
            if b_str[qubit] == "1":
                oracle_qc.x(qubit)

        # CNOT from each input qubit to output
        for qubit in range(n):
            oracle_qc.cx(qubit, n)

        # Apply X-gates again to complete the oracle
        for qubit in range(len(b_str)):
            if b_str[qubit] == "1":
                oracle_qc.x(qubit)

    elif case == "constant":
        # Randomly output 0 or 1 for all inputs
        output = np.random.randint(2)
        if output == 1:
            oracle_qc.x(n)

    oracle_gate = oracle_qc.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate


def dj_algorithm(oracle, n: int) -> QuantumCircuit:
    """
    Construct the Deutsch-Jozsa circuit.

    Args:
        oracle: The oracle gate to query
        n: Number of input qubits

    Returns:
        Complete Deutsch-Jozsa circuit
    """
    dj_circuit = QuantumCircuit(n + 1, n)

    # Initialize output qubit to |->
    dj_circuit.x(n)
    dj_circuit.h(n)

    # Initialize input qubits to |+>
    for qubit in range(n):
        dj_circuit.h(qubit)

    # Apply oracle
    dj_circuit.append(oracle, range(n + 1))

    # Apply Hadamard to input qubits and measure
    for qubit in range(n):
        dj_circuit.h(qubit)

    for i in range(n):
        dj_circuit.measure(i, i)

    return dj_circuit


def classify(counts: dict, n: int) -> str:
    """Classify the oracle based on measurement outcomes.

    If all-zeros dominates, the function is constant; otherwise balanced.
    """
    all_zeros = "0" * n
    zero_prob = counts.get(all_zeros, 0) / sum(counts.values())
    return "constant" if zero_prob > 0.5 else "balanced"


def run_oracle(case: str, n: int, simulator: AerSimulator, shots: int = 1024) -> dict:
    """Build and simulate the Deutsch-Jozsa circuit for a given oracle type."""
    oracle_gate = dj_oracle(case, n)
    circuit = dj_algorithm(oracle_gate, n)
    transpiled = transpile(circuit, simulator)
    return simulator.run(transpiled, shots=shots).result().get_counts()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Deutsch-Jozsa algorithm.")
    parser.add_argument("-n", "--n-qubits", type=int, default=4,
                        help="Number of input qubits (default: 4)")
    parser.add_argument("-S", "--shots", type=int, default=1024,
                        help="Number of simulation shots (default: 1024)")
    args = parser.parse_args()

    n = args.n_qubits
    shots = args.shots
    simulator = AerSimulator()

    print(f"Deutsch-Jozsa — {n} input qubits, {shots} shots\n")

    for case in ("balanced", "constant"):
        counts = run_oracle(case, n, simulator, shots)
        top_outcome, top_count = max(counts.items(), key=lambda kv: kv[1])
        verdict = classify(counts, n)

        print(f"Oracle: {case}")
        print(f"  Top outcome:     |{top_outcome}>  ({top_count}/{shots} shots)")
        match = "[OK]" if verdict == case else "[MISMATCH]"
        print(f"  Verdict:         {verdict}  {match}")
        print(f"  All-zeros count: {counts.get('0' * n, 0)}/{shots}")
        print()

    # Sanity check: balanced oracle must never produce all-zeros
    balanced_counts = run_oracle("balanced", n, simulator, shots)
    assert balanced_counts.get("0" * n, 0) == 0, "Balanced oracle incorrectly identified as constant"
