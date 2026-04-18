"""
Faster Amplitude Estimation implementation.

An optimized variant that achieves near-optimal query complexity
with reduced circuit depth compared to canonical amplitude estimation.
"""

import argparse

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
    parser = argparse.ArgumentParser(
        description="Faster Amplitude Estimation on a Bernoulli model."
    )
    parser.add_argument("-p", "--probability", type=float, default=0.2,
                        help="Target probability to estimate, in (0, 1). Default: 0.2")
    parser.add_argument("-d", "--delta", type=float, default=0.01,
                        help=("Failure probability — the algorithm succeeds with "
                              "probability 1 - delta, in (0, 1). Default: 0.01"))
    parser.add_argument("-m", "--maxiter", type=int, default=3,
                        help=("Number of iterations; the maximal Grover power used by the "
                              "algorithm is 2^(maxiter-1). E.g. maxiter=3 → max power 4. "
                              "Default: 3"))
    args = parser.parse_args()

    if not 0.0 < args.probability < 1.0:
        parser.error(f"probability must be in (0, 1), got {args.probability}")
    if not 0.0 < args.delta < 1.0:
        parser.error(f"delta must be in (0, 1), got {args.delta}")
    if args.maxiter < 1:
        parser.error(f"maxiter must be >= 1, got {args.maxiter}")

    p = args.probability
    delta = args.delta
    maxiter = args.maxiter

    A = BernoulliA(p)
    Q = BernoulliQ(p)

    problem = EstimationProblem(
        state_preparation=A,
        grover_operator=Q,
        objective_qubits=[0],
    )

    # FAE derives its own shots budget from delta via Chernoff bounds — see
    # faster_amplitude_estimation.py: self._shots = (1944*ln(2/delta), 972*ln(2/delta)).
    # Adding a separate --shots CLI flag would break the algorithm's correctness argument.
    sampler = Sampler()
    fae = FasterAmplitudeEstimation(
        delta=delta,
        maxiter=maxiter,
        sampler=sampler,
    )

    result = fae.estimate(problem)

    ci_lower, ci_upper = result.confidence_interval
    num_second_stage = result.num_steps - result.num_first_state_steps
    success_pct = int(round((1 - delta) * 100))

    print(f"Faster Amplitude Estimation — Bernoulli p={p}, δ={delta}, maxiter={maxiter}\n")
    print(f"  Estimated:             {result.estimation:.6f}")
    print(f"  Error:                 {abs(result.estimation - p):.6f}")
    print(f"  {success_pct}% CI:                [{ci_lower:.6f}, {ci_upper:.6f}]  (width {ci_upper - ci_lower:.6f})")
    print(f"  Oracle queries:        {result.num_oracle_queries}")
    print(f"  Success probability:   {result.success_probability:.4f}")
    print(f"  Total iterations:      {result.num_steps}")
    print(f"    First-stage steps:   {result.num_first_state_steps}  (Chernoff-bounded)")
    print(f"    Second-stage steps:  {num_second_stage}  (sin/cos decomposition)")
