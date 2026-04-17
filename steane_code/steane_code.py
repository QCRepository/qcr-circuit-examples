"""
Steane 7-qubit Code — [[7,1,3]] CSS code correcting any single-qubit error.

The Steane code (Andrew Steane, 1996) is the CSS code built from the classical
Hamming [7,4,3] code. It encodes 1 logical qubit into 7 physical qubits using
6 stabilizer generators (3 X-type + 3 Z-type). Because the Hamming code is
self-dual, Steane's logical Clifford gates (H, S, CNOT) are *transversal* —
they consist of the same single-qubit gate applied to each physical qubit
independently — making it a staple of fault-tolerant quantum computing
research.

This example runs the full QEC cycle: encode |0>_L, inject a Pauli error,
measure all 6 stabilizers, and destructively read out logical Z with
syndrome-directed classical correction. Across 8 representative scenarios it
verifies both that (a) each 6-bit syndrome uniquely identifies the error
location, and (b) logical |0>_L is preserved in every shot.

Stabilizer layout (mutually commuting, +1 on the code space):
    X-type (aux[0..2], detect Z errors):
        g1 = X_0 X_4 X_5 X_6        g2 = X_1 X_3 X_5 X_6
        g3 = X_2 X_3 X_4 X_5
    Z-type (aux[3..5], detect X errors):
        g4 = Z_0 Z_2 Z_3 Z_6        g5 = Z_1 Z_2 Z_4 Z_6
        g6 = Z_0 Z_1 Z_2 Z_5

Logical operators (weight-3 representatives modulo stabilizers):
    Z_L = Z_1 Z_4 Z_5      X_L = X_1 X_2 X_3
"""

from typing import Literal, Optional

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

ErrorKind = Literal["X", "Y", "Z"]

# Each X-stabilizer is identified by its support (the qubits the X's act on).
# The first qubit in each tuple is the encoding qubit — it starts in |+> and
# seeds the orbit of that stabilizer on |0>^7.
X_STABILIZER_SUPPORTS = ((0, 4, 5, 6), (1, 3, 5, 6), (2, 3, 4, 5))
Z_STABILIZER_SUPPORTS = ((0, 2, 3, 6), (1, 2, 4, 6), (0, 1, 2, 5))

# Qubits in the support of Z_L = Z_1 Z_4 Z_5. An X error on any of these
# flips a readout bit that Z_L's parity depends on.
Z_L_SUPPORT = (1, 4, 5)

# Syndrome decoders: the 7 non-zero values of each 3-bit stabilizer-syndrome
# map bijectively to one of the 7 qubit positions (Hamming-style addressing).
X_ERROR_FROM_Z_STAB_SYNDROME = {
    (1, 0, 1): 0, (0, 1, 1): 1, (1, 1, 1): 2,
    (1, 0, 0): 3, (0, 1, 0): 4, (0, 0, 1): 5, (1, 1, 0): 6,
}
Z_ERROR_FROM_X_STAB_SYNDROME = {
    (1, 0, 0): 0, (0, 1, 0): 1, (0, 0, 1): 2,
    (0, 1, 1): 3, (1, 0, 1): 4, (1, 1, 1): 5, (1, 1, 0): 6,
}


def encode_steane(qc: QuantumCircuit, code: QuantumRegister) -> None:
    """Encode |0>_L into the 7 code qubits (assumed to start in |0>^7).

    Put qubits 0, 1, 2 in |+>, then CNOT each one into the remaining members of
    its X-stabilizer's support. The resulting state is the uniform superposition
    of the 8 even-weight Hamming [7,4] codewords — a +1 eigenstate of all six
    Steane stabilizers and a +1 eigenstate of Z_L.
    """
    for control in (0, 1, 2):
        qc.h(code[control])
    for control, support in zip((0, 1, 2), X_STABILIZER_SUPPORTS):
        for target in support:
            if target != control:
                qc.cx(code[control], code[target])
    qc.barrier(code)


def inject_error(
    qc: QuantumCircuit,
    code: QuantumRegister,
    kind: Optional[ErrorKind],
    qubit: Optional[int],
) -> None:
    """Inject a single-qubit Pauli error on the encoded state (no-op if kind=None)."""
    if kind is None or qubit is None:
        return
    {"X": qc.x, "Y": qc.y, "Z": qc.z}[kind](code[qubit])
    qc.barrier(code)


def extract_syndrome(
    qc: QuantumCircuit,
    code: QuantumRegister,
    aux: QuantumRegister,
    syndrome_cr: ClassicalRegister,
) -> None:
    """Measure all 6 Steane stabilizers into the classical syndrome register.

    Each stabilizer is measured by putting an ancilla in |+>, applying broadcast
    controlled gates (CX for X-type, CZ for Z-type) from the ancilla into the
    stabilizer's support, rotating back to the computational basis with H, and
    measuring.
    """
    for a in aux:
        qc.h(a)
    qc.barrier()

    # X-type stabilizers: broadcast CNOT from each ancilla to its support
    for i, support in enumerate(X_STABILIZER_SUPPORTS):
        qc.cx(aux[i], [code[q] for q in support])
    qc.barrier()

    # Z-type stabilizers: broadcast CZ from each ancilla to its support
    for i, support in enumerate(Z_STABILIZER_SUPPORTS, start=3):
        qc.cz(aux[i], [code[q] for q in support])
    qc.barrier()

    for a in aux:
        qc.h(a)
    for i, a in enumerate(aux):
        qc.measure(a, syndrome_cr[i])


def measure_logical_z(
    qc: QuantumCircuit,
    code: QuantumRegister,
    data_cr: ClassicalRegister,
) -> None:
    """Destructive Z-basis readout of all 7 data qubits (Z_L is Z-type, no H needed)."""
    qc.barrier(code)
    for i in range(7):
        qc.measure(code[i], data_cr[i])


def build_circuit(kind: Optional[ErrorKind] = None,
                  qubit: Optional[int] = None) -> QuantumCircuit:
    """Assemble encode -> inject error -> syndrome extraction -> logical readout."""
    code = QuantumRegister(7, "code")
    aux = QuantumRegister(6, "aux")
    syndrome_cr = ClassicalRegister(6, "syndrome")
    data_cr = ClassicalRegister(7, "data")
    qc = QuantumCircuit(code, aux, syndrome_cr, data_cr)
    encode_steane(qc, code)
    inject_error(qc, code, kind, qubit)
    extract_syndrome(qc, code, aux, syndrome_cr)
    measure_logical_z(qc, code, data_cr)
    return qc


def decode_syndrome(syndrome_bits_str: str) -> str:
    """Human-readable error label from the 6-bit syndrome (Qiskit little-endian)."""
    bits = [int(b) for b in reversed(syndrome_bits_str)]  # bits[i] = aux[i]
    x_stab_synd = tuple(bits[0:3])  # aux[0..2] = X-stabilizers (detect Z errors)
    z_stab_synd = tuple(bits[3:6])  # aux[3..5] = Z-stabilizers (detect X errors)

    z_error = Z_ERROR_FROM_X_STAB_SYNDROME.get(x_stab_synd)
    x_error = X_ERROR_FROM_Z_STAB_SYNDROME.get(z_stab_synd)

    if x_error is not None and z_error is not None:
        if x_error == z_error:
            return f"Y on q[{x_error}]"
        return f"X on q[{x_error}] + Z on q[{z_error}]"
    if x_error is not None:
        return f"X on q[{x_error}]"
    if z_error is not None:
        return f"Z on q[{z_error}]"
    return "no error"


def expected_label(kind: Optional[ErrorKind], qubit: Optional[int]) -> str:
    if kind is None:
        return "no error"
    return f"{kind} on q[{qubit}]"


def logical_readout(data_bits_str: str, syndrome_bits_str: str) -> int:
    """Compute Z_L eigenvalue from the 7-bit data readout with classical correction.

    Returns 0 for |0>_L (Z_L = +1) and 1 for |1>_L (Z_L = -1).

    An X error on a qubit in Z_L's support (q1, q4, q5) flips the corresponding
    readout bit, which would corrupt the parity unless undone. The syndrome
    tells us the error location; if it falls in Z_L's support we flip it back
    before computing parity. Z errors don't affect Z-basis readout and need
    no correction here.
    """
    data = [int(b) for b in reversed(data_bits_str)]
    synd = [int(b) for b in reversed(syndrome_bits_str)]

    z_stab_synd = tuple(synd[3:6])
    x_error = X_ERROR_FROM_Z_STAB_SYNDROME.get(z_stab_synd)
    if x_error in Z_L_SUPPORT:
        data[x_error] ^= 1

    return sum(data[i] for i in Z_L_SUPPORT) % 2


if __name__ == "__main__":
    simulator = AerSimulator()
    shots = 1000

    scenarios: list[tuple[Optional[ErrorKind], Optional[int]]] = [
        (None, None),
        ("X", 0), ("X", 3), ("X", 5),   # X on q5 requires readout correction
        ("Z", 0), ("Z", 3), ("Z", 5),   # Z errors are invisible to Z-basis readout
        ("Y", 5),                         # Y = iXZ — the X-part requires correction
    ]

    print("Steane 7-qubit Code — syndrome verification and logical state preservation")
    print(f"Logical |0>_L encoded. {shots} shots per scenario.\n")
    print(f"{'Injected':<14}{'Syndrome (aux[5..0])':<22}"
          f"{'Decoded':<22}{'Logical readout':<22}{'Verified':<10}")
    print("-" * 90)

    all_verified = True
    for kind, qubit in scenarios:
        qc = build_circuit(kind, qubit)
        counts = simulator.run(qc, shots=shots).result().get_counts()

        # Multi-register counts: "data_bits syndrome_bits" (last-declared-first).
        syndrome_hist: dict[str, int] = {}
        logical_hist = {0: 0, 1: 0}
        for bitstring, count in counts.items():
            data_part, syndrome_part = bitstring.split(" ")
            syndrome_hist[syndrome_part] = syndrome_hist.get(syndrome_part, 0) + count
            logical_hist[logical_readout(data_part, syndrome_part)] += count

        top_syndrome, top_syndrome_count = max(syndrome_hist.items(), key=lambda kv: kv[1])
        decoded = decode_syndrome(top_syndrome)
        syndrome_ok = decoded == expected_label(kind, qubit)
        logical_ok = logical_hist[0] == shots
        verified = syndrome_ok and logical_ok
        all_verified &= verified

        injected = "no error" if kind is None else f"{kind} on q[{qubit}]"
        synd_display = f"{top_syndrome} ({top_syndrome_count}/{shots})"
        logical_display = f"|0>_L ({logical_hist[0]}/{shots})"
        print(f"  {injected:<12}{synd_display:<22}{decoded:<22}"
              f"{logical_display:<22}{'yes' if verified else 'NO':<10}")

    print("-" * 90)
    print(f"\nAll scenarios verified (correct decode + logical |0>_L preserved): {all_verified}")
