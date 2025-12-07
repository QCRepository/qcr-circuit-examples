"""
Quantum Fourier Transform (QFT) implementation.

The QFT transforms between computational (Z) and Fourier bases,
enabling quantum algorithms like Shor's factoring and phase estimation.
"""

import numpy as np
from numpy import pi
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector


def qft_rotations(circuit: QuantumCircuit, n: int) -> None:
    """
    Apply QFT rotations to the first n qubits (without final swaps).

    Uses recursive application of Hadamard and controlled phase gates.

    Args:
        circuit: Quantum circuit to apply rotations to
        n: Number of qubits for QFT
    """
    if n == 0:
        return
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi / 2 ** (n - qubit), qubit, n)
    qft_rotations(circuit, n)


def swap_registers(circuit: QuantumCircuit, n: int) -> QuantumCircuit:
    """
    Swap qubit order to match QFT output convention.

    Args:
        circuit: Quantum circuit
        n: Number of qubits

    Returns:
        Circuit with swapped registers
    """
    for qubit in range(n // 2):
        circuit.swap(qubit, n - qubit - 1)
    return circuit


def qft(circuit: QuantumCircuit, n: int) -> QuantumCircuit:
    """
    Apply Quantum Fourier Transform to the first n qubits.

    Args:
        circuit: Quantum circuit
        n: Number of qubits for QFT

    Returns:
        Circuit with QFT applied
    """
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit


def create_qft_circuit(n: int, input_state: int = 0) -> QuantumCircuit:
    """
    Create a complete QFT circuit with an encoded input state.

    Args:
        n: Number of qubits
        input_state: Integer to encode in computational basis

    Returns:
        QFT circuit with encoded input
    """
    circuit = QuantumCircuit(n)

    # Encode input state in binary
    for i in range(n):
        if (input_state >> i) & 1:
            circuit.x(i)

    qft(circuit, n)
    return circuit


if __name__ == "__main__":
    n_qubits = 3
    input_value = 5  # Binary: 101

    circuit = create_qft_circuit(n_qubits, input_value)
    circuit.save_statevector()

    simulator = AerSimulator()
    result = simulator.run(circuit).result()
    statevector = result.get_statevector()

    print(f"Input: {input_value} (binary: {bin(input_value)})")
    print(f"QFT output statevector:\n{statevector}")
