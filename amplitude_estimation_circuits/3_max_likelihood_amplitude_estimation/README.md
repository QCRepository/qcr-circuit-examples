# Maximum Likelihood Amplitude Estimation (MLAE)

Maximum Likelihood Amplitude Estimation, introduced by Suzuki, Uno, Raymond, Tanaka, Onodera, and Yamamoto in 2019, takes yet another approach to the amplitude estimation problem: instead of phase estimation or iterative refinement, it runs **several Grover circuits at different powers** and combines all the measurement statistics through a maximum likelihood estimator.

The key insight is that each circuit $\mathcal{Q}^k \mathcal{A}|0\rangle$ samples from a distribution that depends on the unknown amplitude $a$ in a known way — specifically, the probability of measuring a good state is $\sin^2((2k+1)\theta_a)$. By collecting outcomes from multiple values of $k$, the algorithm builds an overdetermined system that the MLE solves for $\theta_a$.

## Why this approach

MLAE sits in a sweet spot between the original QAE and IQAE:

- **No ancilla qubits** — like IQAE, it avoids the extra qubits needed by QPE.
- **Non-adaptive** — unlike IQAE, all circuits can be decided upfront and run in parallel, which is a major advantage for batch execution on cloud quantum hardware.
- **Flexible schedules** — the powers of $\mathcal{Q}$ can be chosen as an exponential schedule ($1, 2, 4, 8, \ldots$) or any custom list, allowing the user to trade off between circuit depth and estimation accuracy.

The trade-off is that the classical post-processing (brute-force grid search over the likelihood function) is heavier, but this is negligible compared to the quantum runtime.

## What the example does

The example estimates a Bernoulli probability $p = 0.2$ using an exponential evaluation schedule with `evaluation_schedule=3`, meaning the algorithm runs circuits with Grover powers $[0, 1, 2, 4]$ (i.e., $[I, Q, Q^2, Q^4]$) and combines the results via MLE.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python max_likelihood_estimation.py
```

The output reports the estimate, error, 95% Fisher confidence interval, the MLE angle θ (which gives the estimate via sin²(θ)), the evaluation schedule (Grover powers used), good counts per power (the raw measurement data the MLE operates on), and the Fisher information — showing how MLAE combines outcomes from multiple circuits run in parallel.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Suzuki, Y., Uno, S., Raymond, R., Tanaka, T., Onodera, T., & Yamamoto, N. (2019). *Amplitude Estimation without Phase Estimation.* [arXiv:1904.10246](https://arxiv.org/abs/1904.10246)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
