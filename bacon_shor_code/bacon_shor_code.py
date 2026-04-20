"""
Bacon-Shor Code 2x2 implementation in the X basis.

A subsystem code that combines features of Bacon and Shor codes
for fault-tolerant quantum error correction.

Uses the circuit construction from the following repository:
https://github.com/Strilanc/more-bacon-less-threshold

Note: for further generalized constructions of the Bacon-Shor code, refer to
the ``make_bacon_shor_circuit`` and relevant functions in the mentioned
repository. Required packages have to be installed such as ``stim``.
"""

import argparse
import os

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit


def load_circuit() -> QuantumCircuit:
    """Load the Bacon-Shor 2x2 circuit from the assembly QASM file.

    Returns:
        The Bacon-Shor code circuit ready for execution.
    """
    qasm_path = os.path.join(
        os.path.dirname(__file__), "assembly", "openqasm2", "bacon_shor_code.qasm"
    )
    return QuantumCircuit.from_qasm_file(qasm_path)


def interpret_results(counts: dict) -> None:
    """Parse and display measurement results with gauge-outcome interpretation.

    Bacon-Shor is a subsystem code, so the weight-2 parity measurements are
    gauge operators (not stabilizers). The actual stabilizers are the weight-4
    products X0*X1*X2*X3 and Z0*Z1*Z2*Z3, which can be recovered by XORing
    the same-type gauge outcomes.

    The 8-bit measurement record (Qiskit little-endian) is structured as:
        rec[0], rec[1]  — X-gauge outcomes (X0*X2, X1*X3)
        rec[2], rec[3]  — Z-gauge outcomes (Z0*Z1, Z2*Z3)
        rec[4..7]       — X-basis data readout of all 4 qubits
    """
    total_shots = sum(counts.values())
    x_gauge_clean = 0

    print(f"Bacon-Shor 2x2 Code — {total_shots} shots\n")
    print("Measurement record: [data q3 q2 q1 q0 | Z-gauges | X-gauges]")
    print("-" * 60)

    for bitstring, count in sorted(counts.items(), key=lambda x: -x[1]):
        # Qiskit bitstring: leftmost = rec[7], rightmost = rec[0]
        x_gauges = bitstring[-2:]           # rec[0], rec[1]
        z_gauges = bitstring[-4:-2]         # rec[2], rec[3]
        data = bitstring[:-4]               # rec[4..7]

        if x_gauges == "00":
            x_gauge_clean += count

        print(f"  {bitstring}  (data={data}  Z-gauges={z_gauges}  X-gauges={x_gauges})  count={count}")

    print("-" * 60)
    print(f"X-gauge outcomes clean: {x_gauge_clean}/{total_shots} "
          f"({x_gauge_clean / total_shots:.0%})")
    print(f"Distinct outcomes: {len(counts)}")
    print(f"\nExpected: X-gauges always 00 (qubits initialized in +X eigenstate).")
    print("Z-gauges and data readout are random per-bit (|+> is not a Z eigenstate).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Bacon-Shor 2x2 subsystem code on a +X initial state."
    )
    parser.add_argument("-S", "--shots", type=int, default=1000,
                        help="Shots for the syndrome-extraction circuit (must be >= 1). Default: 1000")
    args = parser.parse_args()

    if args.shots < 1:
        parser.error(f"shots must be >= 1, got {args.shots}")

    qc = load_circuit()

    simulator = AerSimulator()
    sim_job = simulator.run(qc, shots=args.shots)
    result = sim_job.result()
    counts = result.get_counts()
    interpret_results(counts)
