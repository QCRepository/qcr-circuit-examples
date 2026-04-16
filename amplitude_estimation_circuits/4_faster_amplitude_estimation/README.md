# Faster Amplitude Estimation (FAE)

Faster Amplitude Estimation, proposed by Kenji Nakaji in 2020, pushes the query complexity of amplitude estimation closer to the theoretical lower bound. Like IQAE, it avoids Quantum Phase Estimation entirely and uses only Grover iterates, but it achieves a tighter constant factor in the query count through a two-stage estimation strategy.

## The two-stage approach

What makes FAE distinct is its split into two phases:

1. **First stage** — a sequence of increasingly powerful Grover circuits ($\mathcal{Q}^{2^0}, \mathcal{Q}^{2^1}, \ldots$) with Chernoff-bounded confidence intervals. This stage runs until the confidence interval for $\theta$ grows large enough that it risks wrapping around, at which point the algorithm locks in a reference angle $v$.

2. **Second stage** — uses pairs of circuits at carefully chosen powers to resolve the phase ambiguity through a $\sin$/$\cos$ decomposition. This allows the algorithm to keep doubling the Grover power without the interval-folding problem that limits simpler approaches.

The result is an estimate with provably near-optimal query complexity of $O(1/\epsilon \cdot \log(1/\delta))$, where $\epsilon$ is the target precision and $\delta$ is the failure probability.

## What the example does

The example estimates a Bernoulli probability $p = 0.2$ with `delta=0.01` (99% success probability) and `maxiter=3` (maximum Grover power $2^2 = 4$). The algorithm automatically rescales the problem by a factor of 1/4 to stay in a favorable regime, then un-rescales the final estimate.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python faster_amplitude_estimation_example.py
```

The output reports the estimate, error, confidence interval, oracle query count, success probability, and a breakdown of first-stage (Chernoff-bounded) vs second-stage (sin/cos decomposition) iterations — making the two-stage structure visible in the run log.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Nakaji, K. (2020). *Faster Amplitude Estimation.* [arXiv:2003.02417](https://arxiv.org/abs/2003.02417)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
