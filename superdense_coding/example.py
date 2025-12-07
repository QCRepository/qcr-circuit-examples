"""
Superdense Coding implementation.

Transmits two classical bits using a single qubit and shared entanglement.
Inverse of quantum teleportation: uses 1 qubit to send 2 classical bits.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def create_bell_pair() -> QuantumCircuit:
    """
    Create an entangled Bell pair circuit.

    Returns:
        Circuit producing the Bell state (|00> + |11>)/sqrt(2)
    """
    qc = QuantumCircuit(2)
    qc.h(1)
    qc.cx(1, 0)
    return qc


def encode_message(qc: QuantumCircuit, qubit: int, msg: str) -> QuantumCircuit:
    """
    Encode a two-bit message using superdense coding.

    Encoding rules:
        00 -> I (identity)
        01 -> X
        10 -> Z
        11 -> ZX

    Args:
        qc: Quantum circuit with Bell pair
        qubit: Qubit to encode on (Alice's qubit)
        msg: Two-bit message string ('00', '01', '10', or '11')

    Returns:
        Circuit with encoded message

    Raises:
        ValueError: If message is not a valid two-bit string
    """
    if len(msg) != 2 or not set(msg).issubset({"0", "1"}):
        raise ValueError(f"message '{msg}' is invalid")
    if msg[1] == "1":
        qc.x(qubit)
    if msg[0] == "1":
        qc.z(qubit)
    return qc


def decode_message(qc: QuantumCircuit) -> QuantumCircuit:
    """
    Decode the superdense coded message (Bob's protocol).

    Args:
        qc: Circuit with encoded message

    Returns:
        Circuit ready for measurement
    """
    qc.cx(1, 0)
    qc.h(1)
    return qc


def superdense_coding(message: str) -> QuantumCircuit:
    """
    Complete superdense coding protocol.

    Args:
        message: Two-bit message to transmit

    Returns:
        Complete circuit with measurement
    """
    # Charlie creates Bell pair
    qc = create_bell_pair()
    qc.barrier()

    # Alice encodes message on qubit 1
    qc = encode_message(qc, 1, message)
    qc.barrier()

    # Bob decodes
    qc = decode_message(qc)
    qc.measure_all()

    return qc


if __name__ == "__main__":
    message = "10"
    circuit = superdense_coding(message)

    simulator = AerSimulator()
    result = simulator.run(circuit).result()
    counts = result.get_counts()

    print(f"Sent: {message}")
    print(f"Received: {counts}")
