"""
Iterative Amplitude Estimation implementation.

A variant of amplitude estimation that iteratively refines the estimate
without requiring quantum phase estimation, using simpler Grover circuits.
"""

import argparse

import numpy as np
from qiskit.circuit import QuantumCircuit
from qiskit.primitives import Sampler

from lib.estimation_problem import EstimationProblem
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
    parser = argparse.ArgumentParser(
        description="Iterative Quantum Amplitude Estimation on a Bernoulli model."
    )
    parser.add_argument("-p", "--probability", type=float, default=0.2,
                        help="Target probability to estimate, in (0, 1). Default: 0.2")
    parser.add_argument("-e", "--epsilon", type=float, default=0.01,
                        help="Target precision — half-width of the final confidence interval, in (0, 0.5]. Default: 0.01")
    parser.add_argument("-a", "--alpha", type=float, default=0.05,
                        help="Confidence level: the output lies within epsilon with probability >= 1-alpha, in (0, 1). Default: 0.05")
    parser.add_argument("-S", "--shots", type=int, default=100,
                        help="Shots per Grover-power round (must be >= 1). Default: 100")
    args = parser.parse_args()

    if not 0.0 < args.probability < 1.0:
        parser.error(f"probability must be in (0, 1), got {args.probability}")
    if not 0.0 < args.epsilon <= 0.5:
        parser.error(f"epsilon must be in (0, 0.5], got {args.epsilon}")
    if not 0.0 < args.alpha < 1.0:
        parser.error(f"alpha must be in (0, 1), got {args.alpha}")
    if args.shots < 1:
        parser.error(f"shots must be >= 1, got {args.shots}")

    p = args.probability
    epsilon = args.epsilon
    alpha = args.alpha
    shots = args.shots

    A = BernoulliA(p)
    Q = BernoulliQ(p)

    problem = EstimationProblem(
        state_preparation=A,
        grover_operator=Q,
        objective_qubits=[0],
    )

    # IMPORTANT: specify shots so IQAE runs its iterative loop. Without a shot
    # budget the Sampler returns exact statevector quasi-probabilities and the
    # IQAE code takes a shortcut that bypasses the Grover-power iterations —
    # which defeats the whole point of this example.
    sampler = Sampler(options={"shots": shots})
    iae = IterativeAmplitudeEstimation(
        epsilon_target=epsilon,
        alpha=alpha,
        sampler=sampler,
    )

    result = iae.estimate(problem)

    ci_lower, ci_upper = result.confidence_interval
    num_iterations = len(result.powers) - 1  # powers[0] = 0 is initial
    confidence_pct = int(round((1 - alpha) * 100))

    print(f"Iterative Amplitude Estimation — Bernoulli p={p}, ε={epsilon}, α={alpha}, {shots} shots/round\n")
    print(f"  Estimated:              {result.estimation:.6f}")
    print(f"  Error:                  {abs(result.estimation - p):.6f}")
    print(f"  {confidence_pct}% CI:                 [{ci_lower:.6f}, {ci_upper:.6f}]  (width {ci_upper - ci_lower:.6f})")
    print(f"  Target precision (ε):   {epsilon}")
    print(f"  Oracle queries:         {result.num_oracle_queries}")
    print(f"  Iterations:             {num_iterations}")
    print(f"  Grover powers used:     {result.powers[1:]}")
