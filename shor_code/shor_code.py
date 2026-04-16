"""
Shor 9-qubit Code — quantum error correction against arbitrary single-qubit errors.

The Shor code (1995) was the first quantum error-correcting code. It concatenates
a 3-qubit phase-flip code (outer layer) with three copies of the 3-qubit bit-flip
code (inner layer), using 9 physical qubits to encode 1 logical qubit. Because it
corrects both X and Z errors on any physical qubit, it corrects any single-qubit
error — the operator space {I, X, Y, Z} is spanned.

This example runs the full QEC round: encode |0>_L, inject a single-qubit Pauli
error, measure all 8 stabilizers to obtain a syndrome, and destructively read out
the logical state via X-basis measurement on the data qubits with block-parity
majority vote (the classical correction step). Across 8 representative error
scenarios it verifies that (a) the syndrome correctly identifies the error, and
(b) the logical |0>_L is preserved in every shot.

Logical operators (for reference):
    Z_L = X_0 X_1 X_2  (or any block's X product — they differ by stabilizers)
    X_L = Z_0 Z_3 Z_6  (one Z per block — counterintuitively Z-typed, a
                        consequence of Shor's phase-flip-outer / bit-flip-inner
                        concatenation swapping logical X <-> Z roles)
"""

from typing import Literal, Optional

from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

ErrorKind = Literal["X", "Y", "Z"]


def encode_shor(qc: QuantumCircuit, code: QuantumRegister) -> None:
    """Encode |0>_L using the phase-flip ⊗ bit-flip concatenation.

    Outer layer (phase-flip): CX's from q[0] to q[3] and q[6], followed by H on
    each block leader — this spreads a single logical qubit across three blocks
    in the |+>/|-> basis.

    Inner layer (bit-flip): two CX's within each block copy the leader into the
    two trailing qubits, protecting against single X errors per block.
    """
    qc.cx(code[0], code[3])
    qc.cx(code[0], code[6])
    qc.h(code[0])
    qc.h(code[3])
    qc.h(code[6])
    for leader in (0, 3, 6):
        qc.cx(code[leader], code[leader + 1])
        qc.cx(code[leader], code[leader + 2])
    qc.barrier(code)


def inject_error(
    qc: QuantumCircuit,
    code: QuantumRegister,
    kind: Optional[ErrorKind],
    qubit: Optional[int],
) -> None:
    """Inject a single-qubit Pauli error after encoding (no-op if kind is None)."""
    if kind is None or qubit is None:
        return
    gate = {"X": qc.x, "Y": qc.y, "Z": qc.z}[kind]
    gate(code[qubit])
    qc.barrier(code)


def extract_syndrome(
    qc: QuantumCircuit,
    code: QuantumRegister,
    aux: QuantumRegister,
    aux_cr: ClassicalRegister,
) -> None:
    """Measure all 8 Shor code stabilizers into the classical register.

    Z-type stabilizers (aux[0..5]) are weight-2 Z_i Z_j products — they detect
    X errors and localize them to a specific qubit within a 3-qubit block.

    X-type stabilizers (aux[6..7]) are weight-6 X products across two blocks —
    they detect Z errors but only localize to the block (Z errors within a
    block are equivalent up to stabilizer multiplication).
    """
    for a in aux:
        qc.h(a)
    qc.barrier()

    # Z-type stabilizers via broadcast CZ
    qc.cz(aux[0], code[[0, 1]])  # Z_0 Z_1
    qc.cz(aux[1], code[[1, 2]])  # Z_1 Z_2
    qc.cz(aux[2], code[[3, 4]])  # Z_3 Z_4
    qc.cz(aux[3], code[[4, 5]])  # Z_4 Z_5
    qc.cz(aux[4], code[[6, 7]])  # Z_6 Z_7
    qc.cz(aux[5], code[[7, 8]])  # Z_7 Z_8
    qc.barrier()

    # X-type stabilizers via broadcast CNOT
    qc.cx(aux[6], code[list(range(6))])   # X_0 X_1 X_2 X_3 X_4 X_5
    qc.cx(aux[7], code[list(range(3, 9))])  # X_3 X_4 X_5 X_6 X_7 X_8
    qc.barrier()

    for a in aux:
        qc.h(a)
    qc.barrier()

    for i, a in enumerate(aux):
        qc.measure(a, aux_cr[i])


def measure_logical_z(
    qc: QuantumCircuit,
    code: QuantumRegister,
    data_cr: ClassicalRegister,
) -> None:
    """Destructively read out logical Z by measuring X on every data qubit.

    Z_L has three equivalent block-local representatives: X_0 X_1 X_2, X_3 X_4 X_5,
    and X_6 X_7 X_8 (each equal to the others modulo X-type stabilizers). We
    measure X on all 9 qubits by applying H and then a computational-basis
    measurement, which lets us compute each block's parity independently and
    take a majority vote classically — a protocol that tolerates any single-qubit
    Pauli error and therefore acts as the correction step for this readout.
    """
    qc.barrier(code)
    for i in range(9):
        qc.h(code[i])
    qc.barrier(code)
    for i in range(9):
        qc.measure(code[i], data_cr[i])


def build_circuit(kind: Optional[ErrorKind] = None,
                  qubit: Optional[int] = None) -> QuantumCircuit:
    """Assemble encode -> inject error -> syndrome extraction -> logical readout."""
    code = QuantumRegister(9, "code")
    aux = QuantumRegister(8, "aux")
    aux_cr = ClassicalRegister(8, "syndrome")
    data_cr = ClassicalRegister(9, "data")
    qc = QuantumCircuit(code, aux, aux_cr, data_cr)
    encode_shor(qc, code)
    inject_error(qc, code, kind, qubit)
    extract_syndrome(qc, code, aux, aux_cr)
    measure_logical_z(qc, code, data_cr)
    return qc


def decode_syndrome(syndrome: str) -> str:
    """Classically decode an 8-bit syndrome string into a human-readable error label.

    Expected input format: Qiskit little-endian bitstring (rightmost char = aux[0]).

    Within a 3-qubit block, the (aux[k], aux[k+1]) pair maps as:
        (1, 0) -> first qubit of block   (1, 1) -> middle qubit
        (0, 1) -> last qubit of block    (0, 0) -> no X error in this block

    The (aux[6], aux[7]) pair maps as:
        (1, 0) -> Z error in block 0     (1, 1) -> Z error in block 1
        (0, 1) -> Z error in block 2     (0, 0) -> no Z error
    """
    bits = [int(b) for b in reversed(syndrome)]  # bits[i] = aux[i]
    z_stab = bits[:6]
    x_stab = (bits[6], bits[7])

    x_error_qubit: Optional[int] = None
    for block_idx in range(3):
        b0, b1 = z_stab[2 * block_idx], z_stab[2 * block_idx + 1]
        if (b0, b1) == (1, 0):
            x_error_qubit = 3 * block_idx
        elif (b0, b1) == (1, 1):
            x_error_qubit = 3 * block_idx + 1
        elif (b0, b1) == (0, 1):
            x_error_qubit = 3 * block_idx + 2

    z_error_block = {(1, 0): 0, (1, 1): 1, (0, 1): 2}.get(x_stab)

    if x_error_qubit is not None and z_error_block is not None:
        if x_error_qubit // 3 == z_error_block:
            return f"Y on q[{x_error_qubit}]"
        return f"X on q[{x_error_qubit}] + Z on block {z_error_block}"
    if x_error_qubit is not None:
        return f"X on q[{x_error_qubit}]"
    if z_error_block is not None:
        return f"Z on block {z_error_block}"
    return "no error"


def expected_label(kind: Optional[ErrorKind], qubit: Optional[int]) -> str:
    """Expected decoded label given what we injected."""
    if kind is None:
        return "no error"
    if kind == "X":
        return f"X on q[{qubit}]"
    if kind == "Y":
        return f"Y on q[{qubit}]"
    if kind == "Z":
        # Z errors are only localized to a block
        return f"Z on block {qubit // 3}"
    return "?"


def logical_readout(data_bits: str) -> int:
    """Decode the logical Z eigenvalue from a 9-bit data register reading.

    Returns 0 for Z_L = +1 (|0>_L) and 1 for Z_L = -1 (|1>_L).

    Each 3-qubit block gives an independent estimate of Z_L via its X-basis
    parity (measured as Z after the H layer). Majority vote across the three
    blocks tolerates any single-qubit error — this is the classical correction
    step, combined with the readout.
    """
    # Qiskit format: leftmost char = data_cr[8], rightmost = data_cr[0].
    # Reverse so the i-th character corresponds to data_cr[i] (qubit i).
    bits_by_qubit = data_bits[::-1]
    block_parities = [
        sum(int(bits_by_qubit[3 * block + i]) for i in range(3)) % 2
        for block in range(3)
    ]
    return 1 if sum(block_parities) >= 2 else 0


if __name__ == "__main__":
    simulator = AerSimulator()
    shots = 1000

    scenarios: list[tuple[Optional[ErrorKind], Optional[int]]] = [
        (None, None),
        ("X", 0), ("X", 4), ("X", 8),
        ("Z", 2), ("Z", 5), ("Z", 8),
        ("Y", 4),
    ]

    print("Shor 9-qubit Code — syndrome verification and logical state preservation")
    print(f"Logical |0>_L encoded. {shots} shots per scenario.\n")
    print(f"{'Injected':<16}{'Syndrome (aux[7..0])':<24}"
          f"{'Decoded':<18}{'Logical readout':<22}{'Verified':<10}")
    print("-" * 90)

    all_verified = True
    for kind, qubit in scenarios:
        qc = build_circuit(kind, qubit)
        counts = simulator.run(qc, shots=shots).result().get_counts()

        # Multi-register counts are space-separated "data_cr syndrome_cr"
        # (Qiskit lists last-declared register first in the bitstring).
        syndrome_hist: dict[str, int] = {}
        logical_hist = {0: 0, 1: 0}
        for bitstring, count in counts.items():
            data_part, syndrome_part = bitstring.split(" ")
            syndrome_hist[syndrome_part] = syndrome_hist.get(syndrome_part, 0) + count
            logical_hist[logical_readout(data_part)] += count

        top_syndrome, top_syndrome_count = max(syndrome_hist.items(), key=lambda kv: kv[1])
        decoded = decode_syndrome(top_syndrome)
        syndrome_ok = decoded == expected_label(kind, qubit)
        logical_ok = logical_hist[0] == shots  # every shot recovers |0>_L
        verified = syndrome_ok and logical_ok
        all_verified &= verified

        injected = "no error" if kind is None else f"{kind} on q[{qubit}]"
        synd_display = f"{top_syndrome} ({top_syndrome_count}/{shots})"
        logical_display = f"|0>_L ({logical_hist[0]}/{shots})"
        print(f"  {injected:<14}{synd_display:<24}{decoded:<18}"
              f"{logical_display:<22}{'yes' if verified else 'NO':<10}")

    print("-" * 90)
    print(f"\nAll scenarios verified (correct decode + logical |0>_L preserved): {all_verified}")
    print("Note: Z errors within a block are equivalent up to stabilizers, so the")
    print("decoder localizes them to a block; the majority-vote readout corrects them anyway.")
