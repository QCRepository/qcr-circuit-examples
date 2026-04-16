"""
3-qubit Repetition Code for quantum bit-flip error correction.

Encodes a single logical qubit into 3 physical qubits, measures two parity
stabilizers (Z0*Z1 and Z0*Z2) using ancilla qubits, and applies a conditional
X correction based on the 2-bit syndrome. This example runs the code against
all 4 error scenarios (no error + each of the 3 single-qubit bit-flips) to
verify that the syndrome correctly identifies the error location and the
correction restores the logical state in every case.
"""

from typing import Optional

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


def build_repetition_code_circuit(error_qubit: Optional[int] = None) -> QuantumCircuit:
    """Build the repetition code circuit with optional bit-flip error injection.

    Args:
        error_qubit: Data qubit index (0, 1, or 2) to flip after encoding,
            or None for no error injection.

    Returns:
        The full repetition code circuit: encode → inject → syndrome → correct → measure.
    """
    qreg_data = QuantumRegister(3, name="data")
    qreg_syndrome = QuantumRegister(2, name="syndrome_ancilla")
    creg_data = ClassicalRegister(3, name="data_out")
    creg_syndrome = ClassicalRegister(2, name="syndrome")
    qc = QuantumCircuit(qreg_data, qreg_syndrome, creg_data, creg_syndrome)

    # Prepare logical |1>: physical qubit 0 flipped to |1>, then copied by CNOTs
    qc.x(qreg_data[0])
    qc.barrier(qreg_data)

    # Encode |1> -> |111> via two CNOTs
    qc.cx(qreg_data[0], qreg_data[1])
    qc.cx(qreg_data[0], qreg_data[2])
    qc.barrier(qreg_data)

    # Inject a bit-flip error on one data qubit (or not)
    if error_qubit is not None:
        qc.x(qreg_data[error_qubit])
    qc.barrier(qreg_data)

    # Measure two parity stabilizers:
    #   syndrome[0] = parity of qubits 0 and 1  (Z0 * Z1)
    #   syndrome[1] = parity of qubits 0 and 2  (Z0 * Z2)
    qc.cx(qreg_data[0], qreg_syndrome[0])
    qc.cx(qreg_data[1], qreg_syndrome[0])
    qc.cx(qreg_data[0], qreg_syndrome[1])
    qc.cx(qreg_data[2], qreg_syndrome[1])
    qc.barrier(*qreg_data, *qreg_syndrome)
    qc.measure(qreg_syndrome, creg_syndrome)

    # Conditional reset of ancilla qubits — since we just measured them we know
    # their state and can flip them back to |0> without another measurement round
    with qc.if_test((creg_syndrome[0], 1)):
        qc.x(qreg_syndrome[0])
    with qc.if_test((creg_syndrome[1], 1)):
        qc.x(qreg_syndrome[1])
    qc.barrier(*qreg_data, *qreg_syndrome)

    # Decode syndrome -> apply X correction on the flipped qubit
    #   syndrome = 11 (int 3)  both parities flipped  ->  qubit 0 is the error
    #   syndrome = 01 (int 1)  only Z0*Z1 flipped     ->  qubit 1 is the error
    #   syndrome = 10 (int 2)  only Z0*Z2 flipped     ->  qubit 2 is the error
    with qc.if_test((creg_syndrome, 3)):
        qc.x(qreg_data[0])
    with qc.if_test((creg_syndrome, 1)):
        qc.x(qreg_data[1])
    with qc.if_test((creg_syndrome, 2)):
        qc.x(qreg_data[2])
    qc.barrier(qreg_data)

    qc.measure(qreg_data, creg_data)
    return qc


def parse_counts(counts: dict) -> tuple[dict, dict]:
    """Split combined counts into syndrome-only and data-only histograms.

    Qiskit formats multi-register counts as "reg_last ... reg_first", space-separated.
    In our circuit that means keys look like "syndrome data" (e.g. "11 111").
    """
    syndrome_hist: dict = {}
    data_hist: dict = {}
    for key, count in counts.items():
        syndrome, data = key.split()
        syndrome_hist[syndrome] = syndrome_hist.get(syndrome, 0) + count
        data_hist[data] = data_hist.get(data, 0) + count
    return syndrome_hist, data_hist


if __name__ == "__main__":
    simulator = AerSimulator()
    shots = 1000

    scenarios = [
        (None, "00", "none"),
        (0, "11", "qubit 0"),
        (1, "01", "qubit 1"),
        (2, "10", "qubit 2"),
    ]

    print(f"3-qubit Repetition Code — bit-flip error correction\n")
    print(f"Logical state |1> encoded as |111>. Running {shots} shots per scenario.\n")
    print(f"{'Injected error':<16}{'Expected syndrome':<20}{'Observed syndrome':<24}"
          f"{'Data readout (post-correction)':<34}{'Recovered?':<12}")
    print("-" * 106)

    all_recovered = True
    for error_qubit, expected_syndrome, label in scenarios:
        qc = build_repetition_code_circuit(error_qubit)
        result = simulator.run(qc, shots=shots).result()
        counts = result.get_counts()
        syndrome_hist, data_hist = parse_counts(counts)

        top_syndrome, syndrome_count = max(syndrome_hist.items(), key=lambda kv: kv[1])
        top_data, data_count = max(data_hist.items(), key=lambda kv: kv[1])

        # Recovery is successful if the data register reads 111 in every shot
        recovered = data_hist.get("111", 0) == shots
        all_recovered &= recovered

        syndrome_str = f"{top_syndrome} ({syndrome_count}/{shots})"
        data_str = f"{top_data} ({data_count}/{shots})"
        recovered_str = "yes" if recovered else "NO"
        print(f"  {label:<14}{expected_syndrome:<20}{syndrome_str:<24}{data_str:<34}{recovered_str:<12}")

    print("-" * 106)
    print(f"\nAll single-qubit errors corrected: {all_recovered}")
    print("\nSyndrome decoding:")
    print("  00 -> no error       01 -> qubit 1 flipped")
    print("  10 -> qubit 2 flipped  11 -> qubit 0 flipped")
    print("\nThe repetition code protects against any single bit-flip but cannot correct")
    print("two or more simultaneous errors (the syndrome aliases with a single-qubit error).")
