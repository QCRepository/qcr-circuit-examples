# Canonical Amplitude Estimation (Brassard et al.)

The original Quantum Amplitude Estimation algorithm, introduced by Brassard, Hoyer, Mosca, and Tapp in 2000, answers a deceptively simple question: *given a quantum state, how large is the "good" component?*

More precisely, given a unitary $\mathcal{A}$ that prepares:

$$\mathcal{A}|0\rangle = \sqrt{1 - a}\,|\Psi_0\rangle + \sqrt{a}\,|\Psi_1\rangle$$

the algorithm estimates the amplitude $a$ — the probability of measuring the "good" state $|\Psi_1\rangle$.

## Why it matters

Amplitude estimation is one of the most versatile subroutines in quantum computing. It provides a quadratic speedup over classical sampling and serves as the backbone for quantum algorithms in Monte Carlo simulation, option pricing, risk analysis, and combinatorial optimization. If Grover's search is a hammer, amplitude estimation is the measuring tape that tells you how much you found.

## How it works

The algorithm chains together two well-known building blocks:

1. **Grover operator** ($\mathcal{Q}$) — reflects the quantum state to amplify the good component. The eigenvalues of $\mathcal{Q}$ encode the target amplitude $a$.
2. **Quantum Phase Estimation (QPE)** — extracts those eigenvalues using $m$ auxiliary "evaluation" qubits, producing an estimate on a discrete grid of $2^m$ points.

Because the grid is discrete, the raw QPE output snaps to the nearest grid point. A **Maximum Likelihood Estimation (MLE)** post-processing step then refines this to a continuous value, recovering much better precision without additional quantum resources.

This example uses a **Bernoulli model** — the simplest possible amplitude estimation problem — where $a = p = 0.2$ represents the probability of a biased coin.

## Project structure

```
├── amplitude_estimation.py            # Entry point
├── amplitude_estimation_class.py      # Core QAE algorithm (QPE + MLE)
├── lib/                               # Framework base classes
│   ├── algorithm_result.py
│   ├── amplitude_estimator.py
│   ├── estimation_problem.py
│   └── utils.py
└── assembly/
    └── openqasm3/
        └── amplitude_estimation.qasm  # Pre-exported OpenQASM 3.0 circuit
```

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python amplitude_estimation.py
```

**Expected output:**

```
Target probability: 0.2
Estimated: 0.1464466
MLE estimate: 0.2
```

The grid-based estimate snaps to the nearest QPE grid point (`0.146`), while the MLE refines it back to the true value (`0.2`).

## Key parameters

- **`num_eval_qubits`** (default: `3`) — controls grid resolution. With $m = 3$ you get $2^3 = 8$ grid points. Increasing $m$ improves precision but deepens the circuit.
- **`p`** (default: `0.2`) — the target probability to estimate. Try changing this to see how the algorithm adapts.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- NumPy, SciPy

## References

- Brassard, G., Hoyer, P., Mosca, M., & Tapp, A. (2000). *Quantum Amplitude Amplification and Estimation.* [arXiv:quant-ph/0005055](https://arxiv.org/abs/quant-ph/0005055)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2018–2024.
