"""HHL Algorithm — Quantum Linear Systems Solver.

Solves Ax = b by preparing a quantum state |x> proportional to A^{-1}|b>,
from which functions of the solution (observables) can be extracted.

Parameters are defined at the top of this file. Edit and re-run.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import Isometry

from HHL.hhl import HHL
from HHL.matrices import NumPyMatrix, TridiagonalToeplitz, DiscreteLaplacian
from HHL.observables import MatrixFunctional

# --- Parameters ---

A = np.array([
    [2.0, 1.0, 0.0, 0.0],
    [1.0, 2.0, 1.0, 0.0],
    [0.0, 1.0, 2.0, 1.0],
    [0.0, 0.0, 1.0, 2.0],
])
matrix = NumPyMatrix(A)
# Alternatives for matrices with known structure — more efficient Hamiltonian simulation than arbitrary NumPy:
# matrix = TridiagonalToeplitz(num_state_qubits=2, main_diag=2.0, off_diag=1.0, trotter_steps=2)
# matrix = DiscreteLaplacian(nx=2, ny=2, trotter_steps=2)

right_hand_side = [1.0, 0.0, 0.0, 0.0]
observable = MatrixFunctional(1, 1/2)


if __name__ == "__main__":
    rhs = right_hand_side / np.linalg.norm(right_hand_side)

    num_qubits = matrix.num_state_qubits
    qc = QuantumCircuit(num_qubits)
    qc.append(Isometry(rhs, 0, 0), qargs=range(num_qubits))

    solution = HHL().solve(matrix, qc, observable)
    approx_result = solution.observable

    exact_solution = np.linalg.solve(matrix.matrix, right_hand_side)
    exact_result = observable.evaluate_classically(exact_solution)

    print(f"Approximate result (quantum HHL): {approx_result}")
    print(f"Exact result (classical NumPy):   {exact_result}")
    print(f"Exact solution vector:            {exact_solution}")
