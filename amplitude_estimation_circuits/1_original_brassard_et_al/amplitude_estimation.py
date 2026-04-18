"""
Canonical Amplitude Estimation (Brassard et al.).

Estimates the amplitude a in A|0> = sqrt(1-a)|Psi_0> + sqrt(a)|Psi_1>
using quantum phase estimation on the Grover operator.
"""

import argparse

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
    parser = argparse.ArgumentParser(
        description="Canonical Quantum Amplitude Estimation on a Bernoulli model."
    )
    parser.add_argument("-p", "--probability", type=float, default=0.2,
                        help="Target probability to estimate, in (0, 1). Default: 0.2")
    parser.add_argument("-m", "--eval-qubits", type=int, default=3,
                        help="Number of evaluation qubits (grid resolution 2^m). Default: 3")
    parser.add_argument("-S", "--shots", type=int, default=1000,
                        help="Shots for the QPE circuit (must be >= 1). Default: 1000")
    args = parser.parse_args()

    if not 0.0 < args.probability < 1.0:
        parser.error(f"probability must be in (0, 1), got {args.probability}")
    if args.eval_qubits < 1:
        parser.error(f"eval-qubits must be >= 1, got {args.eval_qubits}")
    if args.shots < 1:
        parser.error(f"shots must be >= 1, got {args.shots}")

    p = args.probability
    m = args.eval_qubits
    shots = args.shots

    A = BernoulliA(p)
    Q = BernoulliQ(p)

    problem = EstimationProblem(
        state_preparation=A,
        grover_operator=Q,
        objective_qubits=[0],
    )

    # Pass an explicit shots budget: with the default shots=None the Sampler returns
    # exact statevector probabilities, and MLE recovers the target noiselessly —
    # which hides the stochastic nature of real amplitude estimation.
    sampler = Sampler(options={"shots": shots})
    ae = AmplitudeEstimation(num_eval_qubits=m, sampler=sampler)

    result = ae.estimate(problem)

    ci_lower, ci_upper = result.confidence_interval

    print(f"Canonical Amplitude Estimation — Bernoulli p={p}, {m} evaluation qubits, {shots} shots\n")
    print(f"  Target probability:    {p}")
    print(f"  Grid-based estimate:   {result.estimation:.6f}  (snaps to nearest of 2^{m} = {2 ** m} points)")
    print(f"  MLE-refined estimate:  {result.mle:.6f}")
    print(f"  Absolute error (MLE):  {abs(result.mle - p):.6f}")
    print(f"  95% CI (Fisher):       [{ci_lower:.6f}, {ci_upper:.6f}]  (width {ci_upper - ci_lower:.6f})")
