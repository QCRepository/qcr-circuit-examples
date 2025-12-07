"""
Deutsch-Jozsa Algorithm implementation.

Determines whether a Boolean function is constant or balanced
using a single quantum query, demonstrating quantum advantage
over classical algorithms.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram


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


if __name__ == "__main__":
    n = 4
    oracle_gate = dj_oracle("balanced", n)
    circuit = dj_algorithm(oracle_gate, n)

    simulator = AerSimulator()
    transpiled = transpile(circuit, simulator)
    results = simulator.run(transpiled).result()
    counts = results.get_counts()

    print(counts)

    # For a balanced oracle, we should never measure all zeros
    assert counts.get("0" * n, 0) == 0, "Balanced oracle incorrectly identified as constant"
