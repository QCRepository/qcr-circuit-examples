"""
Steane Code implementation for quantum error correction.

The quantum circuit includes measurements of the generators of the
Steane code to produce the error syndrome.
"""
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, transpile, ClassicalRegister, QuantumRegister

def steane_code_circuit(code_quantum_register):
    """Quantum circuit for measuring the generators of the Steane code.

    The measurements produce the the error syndrome.

    The top six qubits are the ancilla used for the measurement, and the bottom
    seven are the code qubits.

    Args:
        code_quantum_register(QuantumRegister): Quantum register referencing
            the code qubits.

    Returns:
        QuantumCircuit: Steane code circuit with measurements.
    """
    qr_aux = QuantumRegister(6, "aux")
    cr_aux = ClassicalRegister(6, "results")
    qc = QuantumCircuit(qr_aux,code_quantum_register, cr_aux)

    for qubit in qr_aux:
        qc.reset(qubit)

    qc.barrier()

    for qubit in qr_aux:
        qc.h(qubit)

    qc.barrier()

    qc.cx(qr_aux[0],code_quantum_register[[0, 4, 5, 6]])
    qc.barrier()
    qc.cx(qr_aux[1],code_quantum_register[[1, 3, 5, 6]])
    qc.barrier()
    qc.cx(qr_aux[2],code_quantum_register[[2, 3, 4, 5]])
    qc.barrier()

    qc.cz(qr_aux[3],code_quantum_register[[0, 2, 3, 6]])
    qc.barrier()
    qc.cz(qr_aux[4],code_quantum_register[[1, 2, 4, 6]])
    qc.barrier()
    qc.cz(qr_aux[5],code_quantum_register[[0, 1, 2, 5]])
    qc.barrier()

    for qubit in qr_aux:
        qc.h(qubit)

    for idx, qubit in enumerate(qr_aux):
        qc.measure(qubit, cr_aux[idx])

    return qc

# Creating the code quantum register of 7 qubits
# Note: these qubits could be in an arbitrary joint quantum state
code_qr = QuantumRegister(7, "code")
circuit = steane_code_circuit(code_qr)

# use local simulator
simulator = AerSimulator()
sim_job = simulator.run(circuit, shots=1000)
result = sim_job.result()
counts = result.get_counts()
print(counts)

# Uncomment the following line to draw the circuit:
# print(circuit.draw())
