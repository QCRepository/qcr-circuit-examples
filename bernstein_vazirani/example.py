"""
Bernstein-Vazirani Algorithm implementation.

Determines a secret bitstring s using a single quantum query,
compared to n classical queries required.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def bernstein_vazirani_circuit(secret: str) -> QuantumCircuit:
    """
    Construct the Bernstein-Vazirani circuit for a given secret string.

    The oracle computes f(x) = s·x mod 2 (bitwise dot product).

    Args:
        secret: Secret bitstring to find (e.g., '110101')

    Returns:
        Complete circuit ready for execution
    """
    n = len(secret)
    circuit = QuantumCircuit(n + 1, n)

    # Initialize ancilla qubit to |1⟩
    circuit.x(n)
    circuit.barrier()

    # Apply Hadamard to all qubits
    circuit.h(range(n + 1))
    circuit.barrier()

    # Oracle: apply CX from qubit i to ancilla where secret[i] = '1'
    for i, bit in enumerate(reversed(secret)):
        if bit == "1":
            circuit.cx(i, n)
    circuit.barrier()

    # Apply Hadamard to input qubits
    circuit.h(range(n + 1))
    circuit.barrier()

    # Measure input qubits
    circuit.measure(range(n), range(n))

    return circuit


if __name__ == "__main__":
    secret = "110101"
    circuit = bernstein_vazirani_circuit(secret)

    simulator = AerSimulator()
    result = simulator.run(circuit, shots=1).result()
    counts = result.get_counts()

    measured = list(counts.keys())[0]
    print(f"Secret: {secret}")
    print(f"Measured: {measured}")
    assert measured == secret, f"Expected {secret}, got {measured}"
