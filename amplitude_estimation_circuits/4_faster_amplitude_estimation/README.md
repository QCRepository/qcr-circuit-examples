# Faster Amplitude Estimation (FAE)

Faster Amplitude Estimation, proposed by Kenji Nakaji in 2020, pushes the query complexity of amplitude estimation closer to the theoretical lower bound. Like IQAE, it avoids Quantum Phase Estimation entirely and uses only Grover iterates, but it achieves a tighter constant factor in the query count through a two-stage estimation strategy.

## The two-stage approach

What makes FAE distinct is its split into two phases:

1. **First stage** — a sequence of increasingly powerful Grover circuits (Q^(2⁰), Q^(2¹), …) with Chernoff-bounded confidence intervals on the amplitude angle θₐ ∈ [0, π/2] (where a = sin²(θₐ)). This stage runs until the interval risks wrapping around the cos readout's principal branch, at which point the algorithm locks in a reference angle v.

2. **Second stage** — uses pairs of circuits at carefully chosen powers to resolve the phase ambiguity through a sin/cos decomposition. This allows the algorithm to keep doubling the Grover power without the interval-folding problem that limits simpler approaches.

The result is an estimate with provably near-optimal query complexity of O((1/ε) · log(1/δ)), where ε is the target precision and δ is the failure probability.

## What the example does

This is a **reference implementation** — the algorithm handles any Bernoulli probability, target failure probability, and maximum Grover power. The defaults below are just the out-of-the-box configuration; change them via the CLI to explore the depth/precision tradeoff.

The example uses a **Bernoulli model**: a single-qubit A operator that encodes the target probability p as an amplitude. FAE then runs its two-stage estimation routine, automatically rescaling the problem by a factor of 1/4 to stay in a favorable regime and un-rescaling the final estimate.

## Default parameters

| Parameter | Value |
|-----------|-------|
| Target probability (p) | 0.2 |
| Failure probability (δ) | 0.01 (99% success) |
| Max iterations | 3 (max Grover power = 2^(3−1) = 4) |

With these defaults, FAE typically resolves the estimate in a handful of steps, split between first-stage Chernoff-bounded rounds and second-stage sin/cos decomposition rounds.

> **Why there is no `shots` flag:** FAE derives its shot budget internally from the failure probability δ via the Chernoff bounds that give the algorithm its query-complexity guarantee (1944·ln(2/δ) shots for the first stage, 972·ln(2/δ) for the second). Exposing `--shots` as an independent parameter would break that correctness argument; the `-d/--delta` flag is the correct lever.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python faster_amplitude_estimation_example.py
```

### CLI options

```
python faster_amplitude_estimation_example.py -p 0.35 -d 0.001 -m 4
```

| Flag | Description | Default |
|------|-------------|---------|
| `-p` / `--probability` | Target Bernoulli probability in (0, 1) | 0.2 |
| `-d` / `--delta` | Failure probability — success probability is 1 − δ — in (0, 1) | 0.01 |
| `-m` / `--maxiter` | Number of iterations; the maximal Grover power used is 2^(maxiter−1) (must be ≥ 1) | 3 |

Tighter δ means a higher shot budget per stage (via Chernoff) and therefore more oracle queries. Larger `-m` allows deeper Grover circuits and finer precision at the cost of circuit depth.

## Output

The output reports the estimate, error against the target, confidence interval, total oracle queries, actual success probability, and a breakdown of first-stage (Chernoff-bounded) vs second-stage (sin/cos decomposition) iterations — making the two-stage structure visible in the run log.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Nakaji, K. (2020). *Faster Amplitude Estimation.* [arXiv:2003.02417](https://arxiv.org/abs/2003.02417)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
