# Iterative Amplitude Estimation (IQAE)

Iterative Quantum Amplitude Estimation, proposed by Grinko, Gacon, Zoufal, and Woerner in 2019, reimagines how amplitude estimation can work by **removing the need for Quantum Phase Estimation entirely**. Instead of the deep QPE circuits used in the canonical algorithm, IQAE applies carefully chosen powers of the Grover operator in sequence, narrowing a confidence interval for the target amplitude with each round.

This is a significant practical advantage: QPE requires many ancilla qubits and controlled operations that are expensive on near-term hardware. IQAE needs only the problem qubits themselves, making it far more hardware-friendly while maintaining the same quadratic query complexity.

## How it differs from canonical QAE

In the original Brassard et al. algorithm, all the work happens in one shot — a single deep QPE circuit produces a grid-locked estimate. IQAE takes a fundamentally different approach:

1. **Start with a wide confidence interval** for the amplitude angle θₐ ∈ [0, π/2] (which encodes the amplitude via a = sin²(θₐ)).
2. **Choose a Grover power k** such that the scaled interval (4k+2) · [θₐ_lo, θₐ_hi] fits entirely inside one half-circle of length π — this is required so that the cos((4k+2)·θₐ) readout uniquely determines θₐ within the running interval.
3. **Run the circuit** Q^k · A|0⟩, measure, and use Clopper-Pearson (or Chernoff) confidence intervals to tighten the bounds.
4. **Repeat** until the confidence interval width drops below the target precision ε.

The result is an estimate that, with probability at least 1 − α, lies within ε of the true amplitude. No ancilla qubits, no inverse QFT — just a classical feedback loop choosing the next Grover power based on the running confidence interval.

## What the example does

This is a **reference implementation** — the algorithm handles any Bernoulli probability, target precision, and confidence level. The defaults below are just the out-of-the-box configuration; change them via the CLI to study the precision/query tradeoff.

The example uses a **Bernoulli model**: a single-qubit A operator that encodes the target probability p as an amplitude. IQAE adaptively selects Grover powers round by round until the confidence interval tightens below ε.

## Default parameters

| Parameter | Value |
|-----------|-------|
| Target probability (p) | 0.2 |
| Target precision (ε) | 0.01 |
| Confidence level (1 − α) | 95% (α = 0.05) |
| Shots per round | 100 |

With these defaults, IQAE typically terminates in a handful of iterations, spending far fewer oracle queries than canonical QAE for equivalent precision.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python iterative_amplitude_estimation_example.py
```

### CLI options

```
python iterative_amplitude_estimation_example.py -p 0.35 -e 0.005 -a 0.01 -S 500
```

| Flag | Description | Default |
|------|-------------|---------|
| `-p` / `--probability` | Target Bernoulli probability in (0, 1) | 0.2 |
| `-e` / `--epsilon` | Target precision (confidence-interval half-width) in (0, 0.5] | 0.01 |
| `-a` / `--alpha` | Confidence level (output within ε with probability ≥ 1−α) in (0, 1) | 0.05 |
| `-S` / `--shots` | Shots per Grover-power round (must be ≥ 1) | 100 |

Tighter ε or α produces more iterations and a higher oracle-query count — the core precision/complexity tradeoff of IQAE. More shots per round means tighter per-round confidence intervals and therefore fewer iterations, but higher query cost per round.

## Output

The output reports the estimate, error against the target, the confidence interval, total oracle queries (the main complexity metric), number of iterations, and the sequence of Grover powers chosen adaptively at each iteration — illustrating how IQAE refines the interval round by round without ever using QPE.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Grinko, D., Gacon, J., Zoufal, C., & Woerner, S. (2019). *Iterative Quantum Amplitude Estimation.* [arXiv:1912.05559](https://arxiv.org/abs/1912.05559)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
