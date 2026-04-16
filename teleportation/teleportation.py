"""
Quantum Teleportation — transfer a qubit state via shared entanglement + classical bits.

Quantum teleportation (Bennett et al., 1993) lets Alice transmit an arbitrary
unknown quantum state |psi> to Bob using a pre-shared Bell pair plus 2 classical
bits of communication — without ever physically sending the qubit. It is the
dual of superdense coding and a foundational primitive for quantum networks.

This example prepares |psi> = U|0> on Alice's qubit for several test states U,
runs the standard 3-qubit teleportation protocol with mid-circuit measurements
and classical feedback, then VERIFIES the transfer by applying U^dagger to
Bob's qubit and measuring. If teleportation succeeded, Bob's qubit holds |psi>,
so U^dagger |psi> = |0> and the verification measurement yields 0 in every shot.
"""

from typing import Callable

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

# Type: a (circuit, qubit_index) -> None function that applies gates in-place
GateSequence = Callable[[QuantumCircuit, int], None]


def create_bell_pair(qc: QuantumCircuit, a: int, b: int) -> None:
    """Create a |Phi+> Bell pair between qubits a and b."""
    qc.h(a)
    qc.cx(a, b)


def alice_gates(qc: QuantumCircuit, psi: int, a: int) -> None:
    """Apply Alice's Bell-basis rotation: CX(psi, a) then H(psi)."""
    qc.cx(psi, a)
    qc.h(psi)


def bob_corrections(qc: QuantumCircuit, qubit: int,
                    crz: ClassicalRegister, crx: ClassicalRegister) -> None:
    """Classical-feedback X/Z corrections based on Alice's measurement outcomes."""
    with qc.if_test((crx, 1)):
        qc.x(qubit)
    with qc.if_test((crz, 1)):
        qc.z(qubit)


def teleport_and_verify(prep: GateSequence, inverse_prep: GateSequence) -> QuantumCircuit:
    """Run teleportation for |psi> = prep|0> and verify by applying inverse_prep on Bob.

    If teleportation succeeds, Bob's qubit holds |psi> and inverse_prep takes it
    back to |0>, so the verification measurement is always 0. Any deviation
    indicates the protocol failed.
    """
    qr = QuantumRegister(3, name="q")
    crz = ClassicalRegister(1, name="crz")
    crx = ClassicalRegister(1, name="crx")
    verify_cr = ClassicalRegister(1, name="verify")
    qc = QuantumCircuit(qr, crz, crx, verify_cr)

    # Alice prepares |psi> on q[0]
    prep(qc, 0)
    qc.barrier()

    # Shared Bell pair: q[1] goes to Alice, q[2] to Bob
    create_bell_pair(qc, 1, 2)
    qc.barrier()

    # Alice's Bell measurement on (q[0], q[1])
    alice_gates(qc, 0, 1)
    qc.barrier()
    qc.measure(0, crz[0])
    qc.measure(1, crx[0])
    qc.barrier()

    # Bob applies conditional corrections from the classical bits
    bob_corrections(qc, 2, crz, crx)
    qc.barrier()

    # Verification: apply inverse preparation and measure
    inverse_prep(qc, 2)
    qc.measure(2, verify_cr[0])

    return qc


if __name__ == "__main__":
    import math

    # Each test state is |psi> = U|0>. The "prep" function applies U; "inverse"
    # applies U^dagger so that U^dagger |psi> = |0>, giving a direct verification
    # via a single measurement.
    def nop(qc, q): pass
    def apply_x(qc, q): qc.x(q)
    def apply_h(qc, q): qc.h(q)
    def apply_xh(qc, q): qc.x(q); qc.h(q)
    def apply_hx(qc, q): qc.h(q); qc.x(q)
    def apply_ry_pos(qc, q): qc.ry(math.pi / 3, q)
    def apply_ry_neg(qc, q): qc.ry(-math.pi / 3, q)

    test_states = [
        ("|0>",              nop,          nop),
        ("|1> = X|0>",       apply_x,      apply_x),
        ("|+> = H|0>",       apply_h,      apply_h),
        ("|-> = XH|0>",      apply_xh,     apply_hx),
        ("R_y(pi/3)|0>",     apply_ry_pos, apply_ry_neg),
    ]

    simulator = AerSimulator()
    shots = 1000

    print("Quantum Teleportation — state transfer via shared Bell pair + 2 classical bits")
    print(f"Verification: apply U^dagger on Bob's qubit; success <=> measurement is 0.")
    print(f"{shots} shots per state.\n")

    print(f"{'State prepared':<22}{'Verify (Bob)':<22}{'Teleported':<10}")
    print("-" * 54)

    all_success = True
    for label, prep, inv in test_states:
        qc = teleport_and_verify(prep, inv)
        counts = simulator.run(qc, shots=shots).result().get_counts()

        # Multi-register counts: "verify crx crz" (last-declared first, space-separated)
        verify_hist = {0: 0, 1: 0}
        for bitstring, count in counts.items():
            verify_bit = int(bitstring.split(" ")[0])
            verify_hist[verify_bit] += count

        success = verify_hist[0] == shots
        all_success &= success

        verify_display = f"0 ({verify_hist[0]}/{shots})"
        print(f"  {label:<20}{verify_display:<22}{'yes' if success else 'NO':<10}")

    print("-" * 54)
    print(f"\nAll test states teleported successfully: {all_success}")
