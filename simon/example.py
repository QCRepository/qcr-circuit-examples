"""
Simon's Algorithm implementation.

Finds a hidden bitstring b such that for a function f:
f(x) = f(y) iff y = x XOR b.

Demonstrates exponential quantum speedup over classical algorithms.
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram


def simon_oracle(b: str) -> QuantumCircuit:
    """
    Create a Simon oracle for the given bitstring.

    Args:
        b: Secret bitstring (e.g., '110')

    Returns:
        Oracle circuit implementing f where f(x) = f(x XOR b)
    """
    b = b[::-1]  # Reverse for iteration
    n = len(b)
    qc = QuantumCircuit(n * 2)

    # Copy: |x>|0> -> |x>|x>
    for q in range(n):
        qc.cx(q, q + n)

    if "1" not in b:
        return qc  # 1:1 mapping

    # Apply XOR with b based on first non-zero bit
    i = b.find("1")
    for q in range(n):
        if b[q] == "1":
            qc.cx(i, q + n)

    return qc


def simon_circuit(b: str) -> QuantumCircuit:
    """
    Construct the complete Simon's algorithm circuit.

    Args:
        b: Secret bitstring

    Returns:
        Complete circuit ready for execution
    """
    n = len(b)
    circuit = QuantumCircuit(n * 2, n)

    # Hadamard on input register
    circuit.h(range(n))
    circuit.barrier()

    # Apply oracle
    circuit = circuit.compose(simon_oracle(b))
    circuit.barrier()

    # Hadamard on input register
    circuit.h(range(n))

    # Measure input register
    circuit.measure(range(n), range(n))

    return circuit


def verify_results(b: str, counts: dict) -> bool:
    """
    Verify that all measured results satisfy b.z = 0 (mod 2).

    Args:
        b: Secret bitstring
        counts: Measurement results

    Returns:
        True if all results are valid
    """

    def dot_product(b: str, z: str) -> int:
        return sum(int(b[i]) * int(z[i]) for i in range(len(b))) % 2

    for z in counts:
        result = dot_product(b, z)
        print(f"{b}.{z} = {result} (mod 2)")
        if result != 0:
            return False
    return True


if __name__ == "__main__":
    b = "110"

    circuit = simon_circuit(b)

    simulator = AerSimulator()
    result = simulator.run(circuit, shots=1000).result()
    counts = result.get_counts()

    print(counts)
    assert verify_results(b, counts), "Invalid results detected"
