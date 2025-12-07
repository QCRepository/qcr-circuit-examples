"""
Quantum Phase Estimation (QPE) implementation.

Estimates the phase θ in U|ψ⟩ = e^(2πiθ)|ψ⟩ for a unitary U.
A fundamental subroutine for Shor's algorithm and other quantum algorithms.
"""

import math
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import QFT


def qpe_circuit(
    n_counting_qubits: int, unitary_gate, controlled_unitary_name: str = "CU"
) -> QuantumCircuit:
    """
    Construct a Quantum Phase Estimation circuit.

    Args:
        n_counting_qubits: Number of counting qubits (determines precision)
        unitary_gate: The unitary gate to estimate phase of
        controlled_unitary_name: Name for the controlled unitary in circuit

    Returns:
        QPE circuit ready for execution
    """
    # Total qubits: n counting + 1 eigenstate
    qpe = QuantumCircuit(n_counting_qubits + 1, n_counting_qubits)

    # Initialize eigenstate qubit to |1⟩
    qpe.x(n_counting_qubits)

    # Apply Hadamard to counting qubits
    for qubit in range(n_counting_qubits):
        qpe.h(qubit)

    # Apply controlled unitaries with increasing powers
    repetitions = 1
    for counting_qubit in range(n_counting_qubits):
        for _ in range(repetitions):
            qpe.append(
                unitary_gate.control(1, label=controlled_unitary_name),
                [counting_qubit, n_counting_qubits],
            )
        repetitions *= 2

    qpe.barrier()

    # Apply inverse QFT
    qpe = qpe.compose(
        QFT(n_counting_qubits, inverse=True), range(n_counting_qubits)
    )

    qpe.barrier()

    # Measure counting qubits
    qpe.measure(range(n_counting_qubits), range(n_counting_qubits))

    return qpe


def estimate_phase(counts: dict, n_counting_qubits: int) -> float:
    """
    Extract phase estimate from measurement counts.

    Args:
        counts: Measurement results
        n_counting_qubits: Number of counting qubits used

    Returns:
        Estimated phase θ (0 ≤ θ < 1)
    """
    # Get most frequent measurement
    measured_value = int(max(counts, key=counts.get), 2)
    # Convert to phase
    return measured_value / (2**n_counting_qubits)


if __name__ == "__main__":
    # Example: Estimate phase of T-gate
    # T|1⟩ = e^(iπ/4)|1⟩ = e^(2πi·1/8)|1⟩
    # Expected θ = 1/8 = 0.125

    n_counting = 3
    t_gate = QuantumCircuit(1, name="T")
    t_gate.p(math.pi / 4, 0)  # Phase gate with λ = π/4

    circuit = qpe_circuit(n_counting, t_gate.to_gate(), "CT")

    simulator = AerSimulator()
    transpiled = transpile(circuit, simulator)
    result = simulator.run(transpiled, shots=2048).result()
    counts = result.get_counts()

    theta = estimate_phase(counts, n_counting)
    print(f"Measurement counts: {counts}")
    print(f"Estimated phase θ = {theta} (expected: 0.125)")
