"""
Shor's Algorithm implementation for N=15.

Demonstrates quantum period finding for integer factorization.
Uses a semiclassical QFT approach with qubit recycling.
"""

import math
from fractions import Fraction
from math import gcd
from typing import Optional

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


def candidate_period(measured_int: int, precision_bits: int, max_period: int) -> int:
    """Recover a candidate period r from the measured phase integer via continued fractions.

    The measured value m corresponds to phase m/2^n. Shor's post-processing finds
    the best rational approximation m/2^n ≈ s/r with denominator r ≤ N, then
    returns r as the period candidate. Returns 0 if no useful period is found.
    """
    if measured_int == 0:
        return 0
    approx = Fraction(measured_int, 2 ** precision_bits).limit_denominator(max_period)
    return approx.denominator


def try_factor(N: int, a: int, r: int) -> Optional[tuple[int, int]]:
    """Given candidate period r, apply Shor's gcd trick to recover factors of N.

    If r is even, compute x = a^(r/2) mod N and check gcd(x ± 1, N) for non-trivial
    factors. Returns (p, q) with p*q = N if successful, else None.
    """
    if r % 2 != 0 or r == 0:
        return None
    x = pow(a, r // 2, N)
    for candidate in (gcd(x - 1, N), gcd(x + 1, N)):
        if 1 < candidate < N:
            return (candidate, N // candidate)
    return None


if __name__ == "__main__":
    N = 15
    a = 2
    precision_bits = 3  # 3-bit phase register via qubit recycling
    shots = 1024

    circuit = shor_circuit(a=a)
    simulator = AerSimulator()
    counts = simulator.run(circuit, shots=shots).result().get_counts()

    print(f"Shor's Algorithm — factoring N={N} with base a={a}")
    print(f"Phase precision: {precision_bits} bits ({2 ** precision_bits} grid points)")
    print(f"Shots: {shots}\n")

    header = f"{'Bitstring':<12}{'m':<5}{'phase':<8}{'candidate r':<14}{'Factors':<14}{'Count':<7}"
    print(header)
    print("-" * len(header))

    successful_shots = 0
    for bitstring, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        # Qiskit's bit ordering happens to match the semiclassical QFT phase-integer
        # for this circuit: int(bitstring, 2) == m directly.
        m = int(bitstring.replace(" ", ""), 2)
        phase = Fraction(m, 2 ** precision_bits)
        r = candidate_period(m, precision_bits, N)
        factors = try_factor(N, a, r)

        if factors is not None:
            successful_shots += count
        factors_str = f"{factors[0]} x {factors[1]}" if factors else "—"
        r_str = str(r) if r else "—"

        print(f"  {bitstring:<10}{m:<5}{str(phase):<8}{r_str:<14}{factors_str:<14}{count:<7}")

    print("-" * len(header))
    print(f"\nShots yielding a non-trivial factorization: "
          f"{successful_shots}/{shots}  ({successful_shots / shots:.1%})")
    print(f"True period of 2^x mod 15 is r=4; gcd(2^2 - 1, 15)=3, gcd(2^2 + 1, 15)=5.")
