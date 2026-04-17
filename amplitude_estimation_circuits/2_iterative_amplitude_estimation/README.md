# Iterative Amplitude Estimation (IQAE)

Iterative Quantum Amplitude Estimation, proposed by Grinko, Gacon, Zoufal, and Woerner in 2019, reimagines how amplitude estimation can work by **removing the need for Quantum Phase Estimation entirely**. Instead of the deep QPE circuits used in the canonical algorithm, IQAE applies carefully chosen powers of the Grover operator in sequence, narrowing a confidence interval for the target amplitude with each round.

This is a significant practical advantage: QPE requires many ancilla qubits and controlled operations that are expensive on near-term hardware. IQAE needs only the problem qubits themselves, making it far more hardware-friendly while maintaining the same quadratic query complexity.

## How it differs from canonical QAE

In the original Brassard et al. algorithm, all the work happens in one shot — a single deep QPE circuit produces a grid-locked estimate. IQAE takes a fundamentally different approach:

1. **Start with a wide confidence interval** for the angle $\theta$ (which encodes the amplitude).
2. **Choose a Grover power** $k$ such that the scaled interval $(4k+2) \cdot [\theta_l, \theta_u]$ fits entirely in one half-circle — this ensures the measurement statistics are unambiguous.
3. **Run the circuit** $\mathcal{Q}^k \mathcal{A}|0\rangle$, measure, and use Clopper-Pearson (or Chernoff) confidence intervals to tighten the bounds.
4. **Repeat** until the confidence interval width drops below the target precision $\epsilon$.

The result is an estimate that, with probability at least $1 - \alpha$, lies within $\epsilon$ of the true amplitude.

## What the example does

The example estimates a Bernoulli probability $p = 0.2$ with target precision $\epsilon = 0.01$ and confidence level 95% ($\alpha = 0.05$). The algorithm iteratively refines its estimate without ever building a QPE circuit.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python iterative_amplitude_estimation_example.py
```

The output reports the estimate, error against the target, 95% confidence interval, number of oracle queries (the complexity metric), and the sequence of Grover powers chosen adaptively at each iteration — illustrating how IQAE refines the interval round by round without ever using QPE.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Grinko, D., Gacon, J., Zoufal, C., & Woerner, S. (2019). *Iterative Quantum Amplitude Estimation.* [arXiv:1912.05559](https://arxiv.org/abs/1912.05559)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
