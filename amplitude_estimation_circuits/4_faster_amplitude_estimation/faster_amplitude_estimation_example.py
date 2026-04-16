"""
Faster Amplitude Estimation implementation.

An optimized variant that achieves near-optimal query complexity
with reduced circuit depth compared to canonical amplitude estimation.
"""

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Sampler

from lib.estimation_problem import EstimationProblem
from faster_amplitude_estimation import FasterAmplitudeEstimation


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
    fae = FasterAmplitudeEstimation(
        delta=0.01,  # target accuracy
        maxiter=3,  # maximal Grover power
        sampler=sampler,
    )

    result = fae.estimate(problem)

    ci_lower, ci_upper = result.confidence_interval
    num_second_stage = result.num_steps - result.num_first_state_steps

    print(f"Faster Amplitude Estimation — target p = {p}\n")
    print(f"  Estimated:             {result.estimation:.6f}")
    print(f"  Error:                 {abs(result.estimation - p):.6f}")
    print(f"  CI:                    [{ci_lower:.6f}, {ci_upper:.6f}]  (width {ci_upper - ci_lower:.6f})")
    print(f"  Oracle queries:        {result.num_oracle_queries}")
    print(f"  Success probability:   {result.success_probability:.4f}")
    print(f"  Total iterations:      {result.num_steps}")
    print(f"    First-stage steps:   {result.num_first_state_steps}  (Chernoff-bounded)")
    print(f"    Second-stage steps:  {num_second_stage}  (sin/cos decomposition)")
