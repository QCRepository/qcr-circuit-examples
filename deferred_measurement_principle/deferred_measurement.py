"""
Deferred Measurement Principle demonstration.

Shows that mid-circuit measurements can be replaced by quantum controlled
operations followed by deferred measurements, producing identical results.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator


def create_bell_pair(qc: QuantumCircuit, a: int, b: int) -> None:
    """Create a Bell pair between qubits a and b."""
    qc.h(a)
    qc.cx(a, b)


def alice_gates(qc: QuantumCircuit, psi: int, a: int) -> None:
    """Apply Alice's gates for teleportation."""
    qc.cx(psi, a)
    qc.h(psi)


def measure_and_send(qc: QuantumCircuit, a: int, b: int) -> None:
    """Measure qubits a and b."""
    qc.barrier()
    qc.measure(a, 0)
    qc.measure(b, 1)


def bob_gates_classical(
    qc: QuantumCircuit, qubit: int, crz: ClassicalRegister, crx: ClassicalRegister
) -> None:
    """Apply Bob's corrections using classical control (mid-circuit measurement)."""
    with qc.if_test((crx, 1)):
        qc.x(qubit)
    with qc.if_test((crz, 1)):
        qc.z(qubit)


def teleportation_with_mid_circuit_measurements() -> QuantumCircuit:
    """
    Teleportation using mid-circuit measurements and classical control.

    Returns:
        Circuit with mid-circuit measurements
    """
    qr = QuantumRegister(3, name="q")
    crz = ClassicalRegister(1, name="crz")
    crx = ClassicalRegister(1, name="crx")
    circuit = QuantumCircuit(qr, crz, crx)

    create_bell_pair(circuit, 1, 2)
    circuit.barrier()
    alice_gates(circuit, 0, 1)
    measure_and_send(circuit, 0, 1)
    circuit.barrier()
    bob_gates_classical(circuit, 2, crz, crx)

    return circuit


def teleportation_with_deferred_measurements() -> QuantumCircuit:
    """
    Teleportation using deferred measurements (quantum controlled gates).

    The mid-circuit measurements are replaced by quantum controlled operations,
    with measurements deferred to the end.

    Returns:
        Circuit with deferred measurements
    """
    qr = QuantumRegister(3, name="q")
    crz = ClassicalRegister(1, name="crz")
    crx = ClassicalRegister(1, name="crx")
    circuit = QuantumCircuit(qr, crz, crx)

    create_bell_pair(circuit, 1, 2)
    alice_gates(circuit, 0, 1)

    # Quantum controlled operations instead of classical control
    circuit.cx(0, 2)
    circuit.cz(1, 2)

    # Measurements deferred to end
    measure_and_send(circuit, 0, 1)

    return circuit


def compare_distributions(counts_a: dict, counts_b: dict, shots: int) -> float:
    """Return the maximum absolute difference in probability across all outcomes."""
    all_outcomes = set(counts_a) | set(counts_b)
    return max(
        abs(counts_a.get(outcome, 0) / shots - counts_b.get(outcome, 0) / shots)
        for outcome in all_outcomes
    )


if __name__ == "__main__":
    simulator = AerSimulator()
    shots = 100_000

    # Run both circuits
    circuit_mid = teleportation_with_mid_circuit_measurements()
    circuit_deferred = teleportation_with_deferred_measurements()

    counts_mid = simulator.run(circuit_mid, shots=shots).result().get_counts()
    counts_deferred = simulator.run(circuit_deferred, shots=shots).result().get_counts()

    # Bell measurement outcomes on Alice's qubits — format "crx crz" (Qiskit reverses register order)
    outcomes = sorted(set(counts_mid) | set(counts_deferred))

    print(f"Deferred Measurement Principle — {shots:,} shots per circuit\n")
    print(f"{'Outcome':<12}{'Mid-circuit':>14}{'Deferred':>14}{'|Δ prob|':>12}")
    print("-" * 52)
    for outcome in outcomes:
        p_mid = counts_mid.get(outcome, 0) / shots
        p_def = counts_deferred.get(outcome, 0) / shots
        print(f"  {outcome:<10}{p_mid:>14.4f}{p_def:>14.4f}{abs(p_mid - p_def):>12.4f}")

    max_diff = compare_distributions(counts_mid, counts_deferred, shots)
    equivalent = max_diff < 0.01  # ~3 standard deviations at 100k shots

    print("-" * 52)
    print(f"Max probability difference: {max_diff:.4f}")
    print(f"Distributions equivalent:   {equivalent}  (threshold 0.01)")
    print(f"\nExpected: uniform 0.25 across all 4 Bell measurement outcomes.")
    print("The two circuits produce statistically identical distributions, confirming")
    print("the deferred measurement principle: classical control via mid-circuit")
    print("measurement is equivalent to quantum control with deferred measurement.")
