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
    """Parse and display measurement results with syndrome interpretation.

    The 8-bit measurement record (Qiskit little-endian) is structured as:
        rec[0], rec[1]  — X-stabilizer checks (X0*X2, X1*X3)
        rec[2], rec[3]  — Z-stabilizer checks (Z0*Z1, Z2*Z3)
        rec[4..7]       — X-basis data readout of all 4 qubits
    """
    total_shots = sum(counts.values())
    x_syndrome_clean = 0

    print(f"Bacon-Shor 2x2 Code — {total_shots} shots\n")
    print("Measurement record: [data q3 q2 q1 q0 | Z-syndromes | X-syndromes]")
    print("-" * 60)

    for bitstring, count in sorted(counts.items(), key=lambda x: -x[1]):
        # Qiskit bitstring: leftmost = rec[7], rightmost = rec[0]
        x_synd = bitstring[-2:]           # rec[0], rec[1]
        z_synd = bitstring[-4:-2]         # rec[2], rec[3]
        data = bitstring[:-4]             # rec[4..7]

        if x_synd == "00":
            x_syndrome_clean += count

        print(f"  {bitstring}  (data={data}  Z-synd={z_synd}  X-synd={x_synd})  count={count}")

    print("-" * 60)
    print(f"X-stabilizer syndromes clean: {x_syndrome_clean}/{total_shots} "
          f"({x_syndrome_clean / total_shots:.0%})")
    print(f"Distinct outcomes: {len(counts)}")
    print(f"\nExpected: X-syndromes always 00 (qubits initialized in +X eigenstate).")
    print("Z-syndromes and data readout are random (|+> is not a Z eigenstate).")


if __name__ == "__main__":
    qc = load_circuit()

    # Use local simulator
    simulator = AerSimulator()
    sim_job = simulator.run(qc, shots=1000)
    result = sim_job.result()
    counts = result.get_counts()
    interpret_results(counts)
