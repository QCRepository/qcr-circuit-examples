# Maximum Likelihood Amplitude Estimation (MLAE)

Maximum Likelihood Amplitude Estimation, introduced by Suzuki, Uno, Raymond, Tanaka, Onodera, and Yamamoto in 2019, takes yet another approach to the amplitude estimation problem: instead of phase estimation or iterative refinement, it runs **several Grover circuits at different powers** and combines all the measurement statistics through a maximum likelihood estimator.

The key insight is that each circuit Q^k · A|0⟩ samples from a distribution that depends on the unknown amplitude a in a known way — specifically, the probability of measuring a good state is sin²((2k+1)θₐ). By collecting outcomes from multiple values of k, the algorithm builds an overdetermined system that the MLE solves for θₐ.

## Why this approach

MLAE sits in a sweet spot between the original QAE and IQAE:

- **No ancilla qubits** — like IQAE, it avoids the extra qubits needed by QPE.
- **Non-adaptive** — unlike IQAE, all circuits can be decided upfront and run in parallel, which is a major advantage for batch execution on cloud quantum hardware.
- **Flexible schedules** — the powers of Q can be chosen as an exponential schedule (1, 2, 4, 8, …) or any custom list, allowing the user to trade off between circuit depth and estimation accuracy.

The tradeoff is that the classical post-processing (brute-force grid search over the likelihood function) is heavier, but this is negligible compared to the quantum runtime.

## What the example does

This is a **reference implementation** — the algorithm handles any Bernoulli probability and any exponential evaluation schedule. The defaults below are just the out-of-the-box configuration; change them via the CLI to explore the depth/accuracy tradeoff.

The example uses a **Bernoulli model**: a single-qubit A operator that encodes the target probability p as an amplitude. MLAE runs a set of Grover circuits at different powers in parallel and combines their outcomes via MLE.

## Default parameters

| Parameter | Value |
|-----------|-------|
| Target probability (p) | 0.2 |
| Max power (m) | 3 → evaluation schedule [0, 1, 2, 4] = [I, Q, Q², Q⁴] |
| Shots per circuit | 100 |

With these defaults, MLAE runs 4 circuits in parallel and combines the measurements through a likelihood maximization over θₐ ∈ (0, π/2).

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python max_likelihood_estimation.py
```

### CLI options

```
python max_likelihood_estimation.py -p 0.35 -m 4 -S 500
```

| Flag | Description | Default |
|------|-------------|---------|
| `-p` / `--probability` | Target Bernoulli probability in (0, 1) | 0.2 |
| `-m` / `--max-power` | Exponential schedule length: runs powers [0, 1, 2, …, 2^(m−1)] | 3 |
| `-S` / `--shots` | Shots per Grover-power circuit (must be ≥ 1) | 100 |

Increasing `-m` adds deeper Grover circuits to the schedule, improving the Fisher information per shot but raising peak circuit depth. Increasing `-S` tightens each circuit's contribution to the likelihood.

## Output

The output reports the estimate, error against the target, the 95% Fisher confidence interval, the MLE amplitude angle θₐ (which gives the estimate via sin²(θₐ)), total oracle queries, the evaluation schedule (Grover powers used), good counts per power (the raw measurement data the MLE operates on), and the Fisher information — showing how MLAE combines outcomes from multiple circuits run in parallel.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Suzuki, Y., Uno, S., Raymond, R., Tanaka, T., Onodera, T., & Yamamoto, N. (2019). *Amplitude Estimation without Phase Estimation.* [arXiv:1904.10246](https://arxiv.org/abs/1904.10246)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
