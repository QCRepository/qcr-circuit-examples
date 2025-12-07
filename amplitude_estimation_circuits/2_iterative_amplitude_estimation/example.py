"""
Iterative Amplitude Estimation implementation.

A variant of amplitude estimation that iteratively refines the estimate
without requiring quantum phase estimation, using simpler Grover circuits.
"""

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Sampler

from estimation_problem import EstimationProblem
from iterative_amplitude_estimation import IterativeAmplitudeEstimation


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
    iae = IterativeAmplitudeEstimation(
        epsilon_target=0.01,  # target accuracy
        alpha=0.05,  # confidence interval width
        sampler=sampler,
    )

    result = iae.estimate(problem)

    print(f"Target probability: {p}")
    print(f"Estimated: {result.estimation}")
