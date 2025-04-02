import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import Isometry
from HHL.hhl import HHL
from HHL.matrices import TridiagonalToeplitz
from HHL.observables import MatrixFunctional

matrix = TridiagonalToeplitz(2, 1, 1 / 3, trotter_steps=2)
right_hand_side = [1.0, -2.1, 3.2, -4.3]
observable = MatrixFunctional(1, 1 / 2)
rhs = right_hand_side / np.linalg.norm(right_hand_side)

# Initial state circuit
num_qubits = matrix.num_state_qubits
qc = QuantumCircuit(num_qubits)
qc.append(Isometry(rhs,0,0), qargs=range(num_qubits))

hhl = HHL()
solution = hhl.solve(matrix, qc, observable)
approx_result = solution.observable

exact_solution = np.linalg.solve(matrix.matrix, right_hand_side)
exact_result = observable.evaluate_classically(exact_solution)

print(exact_solution, exact_result)
