"""
Maximum Likelihood Amplitude Estimation implementation.

Estimates amplitude without phase estimation by using maximum likelihood
estimation on measurement outcomes from multiple Grover iterations.
"""

import argparse

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
    parser = argparse.ArgumentParser(
        description="Maximum Likelihood Amplitude Estimation on a Bernoulli model."
    )
    parser.add_argument("-p", "--probability", type=float, default=0.2,
                        help="Target probability to estimate, in (0, 1). Default: 0.2")
    parser.add_argument("-m", "--max-power", type=int, default=3,
                        help=("Integer form of the evaluation schedule. Uses an exponential "
                              "schedule [0, 1, 2, ..., 2^(m-1)] — e.g. m=3 runs Grover powers "
                              "[I, Q, Q^2, Q^4]. Default: 3"))
    parser.add_argument("-S", "--shots", type=int, default=100,
                        help="Shots per Grover-power circuit (must be >= 1). Default: 100")
    args = parser.parse_args()

    if not 0.0 < args.probability < 1.0:
        parser.error(f"probability must be in (0, 1), got {args.probability}")
    if args.max_power < 0:
        parser.error(f"max-power must be >= 0, got {args.max_power}")
    if args.shots < 1:
        parser.error(f"shots must be >= 1, got {args.shots}")

    p = args.probability
    max_power = args.max_power
    shots = args.shots

    A = BernoulliA(p)
    Q = BernoulliQ(p)

    problem = EstimationProblem(
        state_preparation=A,
        grover_operator=Q,
        objective_qubits=[0],
    )

    # Pass an explicit shots budget: with the default shots=None the Sampler returns
    # exact statevector probabilities, which makes MLAE collapse its CI to zero width.
    sampler = Sampler(options={"shots": shots})
    mlae = MaximumLikelihoodAmplitudeEstimation(
        evaluation_schedule=max_power,
        sampler=sampler,
    )

    result = mlae.estimate(problem)

    ci_lower, ci_upper = result.confidence_interval

    print(f"Maximum Likelihood Amplitude Estimation — Bernoulli p={p}, max-power={max_power}, {shots} shots/circuit\n")
    print(f"  Estimated:           {result.estimation:.6f}")
    print(f"  Error:               {abs(result.estimation - p):.6f}")
    print(f"  95% CI (Fisher):     [{ci_lower:.6f}, {ci_upper:.6f}]  (width {ci_upper - ci_lower:.6f})")
    print(f"  MLE angle theta:     {result.theta:.6f}  (estimate = sin^2(theta) = {np.sin(result.theta) ** 2:.6f})")
    print(f"  Oracle queries:      {result.num_oracle_queries}")
    print(f"  Evaluation schedule: {result.evaluation_schedule}  (Grover powers)")
    print(f"  Good counts / shots: {[f'{c}/{result.shots}' for c in result.good_counts]}")
    print(f"  Fisher information:  {result.fisher_information:.2f}")
