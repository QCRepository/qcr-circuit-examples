"""
Quantum Teleportation implementation.

Transfers a quantum state from Alice to Bob using a shared Bell pair
and classical communication, without physically sending the qubit.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.result import marginal_counts
from qiskit.quantum_info import random_statevector


def create_bell_pair(qc: QuantumCircuit, a: int, b: int) -> None:
    """
    Create a Bell pair between qubits a and b.

    Args:
        qc: Quantum circuit
        a: First qubit index
        b: Second qubit index
    """
    qc.h(a)
    qc.cx(a, b)


def alice_gates(qc: QuantumCircuit, psi: int, a: int) -> None:
    """
    Apply Alice's gates for teleportation.

    Args:
        qc: Quantum circuit
        psi: Qubit to teleport
        a: Alice's entangled qubit
    """
    qc.cx(psi, a)
    qc.h(psi)


def measure_and_send(qc: QuantumCircuit, a: int, b: int) -> None:
    """
    Measure Alice's qubits and store results for classical communication.

    Args:
        qc: Quantum circuit
        a: First qubit to measure
        b: Second qubit to measure
    """
    qc.barrier()
    qc.measure(a, 0)
    qc.measure(b, 1)


def bob_gates(
    qc: QuantumCircuit, qubit: int, crz: ClassicalRegister, crx: ClassicalRegister
) -> None:
    """
    Apply Bob's conditional gates based on classical measurement results.

    Args:
        qc: Quantum circuit
        qubit: Bob's qubit
        crz: Classical register for Z correction
        crx: Classical register for X correction
    """
    with qc.if_test((crx, 1)):
        qc.x(qubit)
    with qc.if_test((crz, 1)):
        qc.z(qubit)


def teleportation_circuit() -> QuantumCircuit:
    """
    Construct the complete quantum teleportation circuit.

    Returns:
        Complete teleportation circuit with 3 qubits and 2 classical bits
    """
    qr = QuantumRegister(3, name="q")
    crz = ClassicalRegister(1, name="crz")
    crx = ClassicalRegister(1, name="crx")
    circuit = QuantumCircuit(qr, crz, crx)

    # Step 1: Create Bell pair between q1 and q2
    create_bell_pair(circuit, 1, 2)

    # Step 2: Alice's operations on q0 (state to teleport) and q1
    circuit.barrier()
    alice_gates(circuit, 0, 1)

    # Step 3: Alice measures and sends classical bits
    measure_and_send(circuit, 0, 1)

    # Step 4: Bob applies corrections based on classical bits
    circuit.barrier()
    bob_gates(circuit, 2, crz, crx)

    return circuit


if __name__ == "__main__":
    circuit = teleportation_circuit()
    circuit.save_statevector()

    simulator = AerSimulator()
    result = simulator.run(circuit).result()
    statevector = result.get_statevector()

    print(statevector)
