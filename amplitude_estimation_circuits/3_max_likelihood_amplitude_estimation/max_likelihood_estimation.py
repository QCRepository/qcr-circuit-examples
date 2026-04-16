"""
Maximum Likelihood Amplitude Estimation implementation.

Estimates amplitude without phase estimation by using maximum likelihood
estimation on measurement outcomes from multiple Grover iterations.
"""

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Sampler

from lib.estimation_problem import EstimationProblem
from max_likelihood_amplitude_estimation import MaximumLikelihoodAmplitudeEstimation


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
    mlae = MaximumLikelihoodAmplitudeEstimation(
        evaluation_schedule=3,  # log2 of maximal Grover power
        sampler=sampler,
    )

    result = mlae.estimate(problem)

    ci_lower, ci_upper = result.confidence_interval

    print(f"Maximum Likelihood Amplitude Estimation — target p = {p}\n")
    print(f"  Estimated:           {result.estimation:.6f}")
    print(f"  Error:               {abs(result.estimation - p):.6f}")
    print(f"  95% CI (Fisher):     [{ci_lower:.6f}, {ci_upper:.6f}]  (width {ci_upper - ci_lower:.6f})")
    print(f"  MLE angle theta:     {result.theta:.6f}  (estimate = sin^2(theta) = {np.sin(result.theta) ** 2:.6f})")
    print(f"  Oracle queries:      {result.num_oracle_queries}")
    print(f"  Evaluation schedule: {result.evaluation_schedule}  (Grover powers)")
    print(f"  Good counts / shots: {[f'{c}/{result.shots}' for c in result.good_counts]}")
    print(f"  Fisher information:  {result.fisher_information:.2f}")
