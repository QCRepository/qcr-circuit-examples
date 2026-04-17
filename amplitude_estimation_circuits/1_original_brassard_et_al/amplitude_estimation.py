"""
Canonical Amplitude Estimation (Brassard et al.).

Estimates the amplitude a in A|0> = sqrt(1-a)|Psi_0> + sqrt(a)|Psi_1>
using quantum phase estimation on the Grover operator.
"""

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Sampler

from lib.estimation_problem import EstimationProblem
from amplitude_estimation_class import AmplitudeEstimation


class BernoulliA(QuantumCircuit):
    """A circuit representing the Bernoulli A operator."""

    def __init__(self, probability):
        super().__init__(1)
        theta_p = 2 * np.arcsin(np.sqrt(probability))
        self.ry(theta_p, 0)


class BernoulliQ(QuantumCircuit):
    """A circuit representing the Bernoulli Q (Grover) operator."""

    def __init__(self, probability):
        super().__init__(1)
        self._theta_p = 2 * np.arcsin(np.sqrt(probability))
        self.ry(2 * self._theta_p, 0)

    def power(self, k):
        """Efficient implementation of Q^k."""
        q_k = QuantumCircuit(1)
        q_k.ry(2 * k * self._theta_p, 0)
        return q_k


if __name__ == "__main__":
    # Target probability to estimate
    p = 0.2

    A = BernoulliA(p)
    Q = BernoulliQ(p)

    problem = EstimationProblem(
        state_preparation=A,
        grover_operator=Q,
        objective_qubits=[0],
    )

    sampler = Sampler()
    ae = AmplitudeEstimation(num_eval_qubits=3, sampler=sampler)

    result = ae.estimate(problem)

    print(f"Target probability: {p}")
    print(f"Estimated: {result.estimation}")
    print(f"MLE estimate: {result.mle}")
