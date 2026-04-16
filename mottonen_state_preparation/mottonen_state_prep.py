"""
Mottonen State Preparation implementation.

Prepares an arbitrary quantum state using the algorithm by Mottonen et al.,
which decomposes the state into uniformly controlled rotations.
"""

import numpy as np

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

from MottonenStatePreparation import state_prep_möttönen


if __name__ == "__main__":
    # Target state vector (will be normalized)
    vector = [-0.1, 0.2, -0.3, 0.4, -0.5, 0.6, -0.7, 0.8]
    vector = np.asarray(vector)
    vector = (1 / np.linalg.norm(vector)) * vector

    qubits = int(np.log2(len(vector)))
    reg = QuantumRegister(qubits, "reg")
    c = ClassicalRegister(qubits, "c")
    qc = QuantumCircuit(reg, c, name='state prep')
    state_prep_möttönen(qc, vector, reg)

    qc = qc.decompose(reps=2)

    # Verify by simulating the statevector
    qc_no_meas = qc.remove_final_measurements(inplace=False)
    qc_no_meas.save_statevector()
    simulator = AerSimulator()
    result = simulator.run(qc_no_meas).result()
    statevector = result.get_statevector()

    print(f"Target state:   {np.round(vector, 4)}")
    print(f"Prepared state: {np.round(np.real(statevector), 4)}")

    # You can draw the circuit by uncommenting the following line:
    # print(qc.draw())
