"""
Shor's Algorithm implementation for N=15.

Demonstrates quantum period finding for integer factorization.
Uses a semiclassical QFT approach with qubit recycling.
"""

import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator


def circuit_2mod15(qc: QuantumCircuit, qr: QuantumRegister, cr: ClassicalRegister) -> None:
    """Apply controlled-swap operations for 2^k mod 15."""
    qc.cswap(qr[4], qr[3], qr[2])
    qc.cswap(qr[4], qr[2], qr[1])
    qc.cswap(qr[4], qr[1], qr[0])


def circuit_aperiod15(
    qc: QuantumCircuit, qr: QuantumRegister, cr: ClassicalRegister, a: int
) -> None:
    """
    Construct the period-finding circuit for a^x mod 15.

    Uses semiclassical QFT with measurement-based phase corrections
    and qubit recycling for efficiency.

    Args:
        qc: Quantum circuit
        qr: Quantum register (5 qubits)
        cr: Classical register (5 bits)
        a: Base for modular exponentiation
    """
    # Initialize q[0] to |1>
    qc.x(qr[0])

    # Apply a^4 mod 15 (trivial for a=2)
    qc.h(qr[4])
    qc.h(qr[4])
    qc.measure(qr[4], cr[0])
    qc.reset(qr[4])

    # Apply a^2 mod 15
    qc.h(qr[4])
    qc.cx(qr[4], qr[2])
    qc.cx(qr[4], qr[0])

    with qc.if_test((cr, 1)):
        qc.p(math.pi / 2.0, qr[4])
    qc.h(qr[4])
    qc.measure(qr[4], cr[1])
    qc.reset(qr[4])

    # Apply a mod 15
    qc.h(qr[4])
    circuit_2mod15(qc, qr, cr)
    with qc.if_test((cr, 3)):
        qc.p(3.0 * math.pi / 4.0, qr[4])
    with qc.if_test((cr, 2)):
        qc.p(math.pi / 2.0, qr[4])
    with qc.if_test((cr, 1)):
        qc.p(math.pi / 4.0, qr[4])
    qc.h(qr[4])
    qc.measure(qr[4], cr[2])


def shor_circuit(a: int = 2) -> QuantumCircuit:
    """
    Construct Shor's algorithm circuit for factoring 15.

    Args:
        a: Coprime base (default 2)

    Returns:
        Complete circuit for period finding
    """
    qr = QuantumRegister(5, "q")
    cr = ClassicalRegister(5, "c")
    circuit = QuantumCircuit(qr, cr)
    circuit_aperiod15(circuit, qr, cr, a)
    return circuit


if __name__ == "__main__":
    circuit = shor_circuit(a=2)

    simulator = AerSimulator()
    result = simulator.run(circuit, shots=1024).result()
    counts = result.get_counts()

    print(counts)
