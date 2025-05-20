import numpy as np

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister 
from qiskit_aer import AerSimulator

from MottonenStatePreparation import state_prep_möttönen

vector = [-0.1, 0.2, -0.3, 0.4, -0.5, 0.6, -0.7, 0.8]
vector = np.asarray(vector)
vector = (1 / np.linalg.norm(vector)) * vector

qubits = int(np.log2(len(vector)))
reg = QuantumRegister(qubits, "reg")
c = ClassicalRegister(qubits, "c")
qc = QuantumCircuit(reg, c, name='state prep')
state_prep_möttönen(qc, vector, reg)

qc = qc.decompose(reps=2)

# You can draw the circuit by uncommenting the following line:
# qc.draw()
