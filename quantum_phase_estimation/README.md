# Quantum Phase Estimation (QPE)

Quantum Phase Estimation answers a deceptively general question: *given a unitary $U$ and one of its eigenvectors $|\psi\rangle$, what is the phase?* Concretely, if $U|\psi\rangle = e^{2\pi i \theta}|\psi\rangle$, QPE returns an estimate of $\theta$ to any desired precision.

This single primitive is the beating heart of a huge swath of quantum computing. Shor's factoring algorithm is phase estimation of a modular exponentiation operator. The HHL linear systems algorithm is phase estimation of $e^{iAt}$. Quantum chemistry energy calculations are phase estimation of $e^{-iHt}$ where $H$ is the Hamiltonian. Once you understand QPE, you understand the skeleton of most "exponentially faster" quantum algorithms.

## How it works

QPE uses two registers:

1. **Counting register** (`n` qubits) — stores the binary fraction representation of $\theta$. More qubits → finer precision ($2^n$ grid points).
2. **Eigenstate register** — holds $|\psi\rangle$, which is preserved through the algorithm.

The circuit has three stages:

1. **Superposition** — Hadamard the counting register to put it in an equal superposition.
2. **Controlled-$U^{2^k}$ cascade** — for each counting qubit $k$, apply $U$ to the eigenstate register $2^k$ times, controlled on that counting qubit. This writes the phase into the counting register via phase kickback.
3. **Inverse QFT + measure** — the counting register now encodes $\theta$ in the Fourier basis; inverse QFT converts it back to the computational basis for readout.

With $n$ counting qubits, the output is an $n$-bit integer $y$ such that $\theta \approx y/2^n$. If $\theta$ is an exact multiple of $1/2^n$, QPE returns it with probability 1; otherwise, the distribution peaks at the nearest grid point and spreads out.

## What the example does

The example estimates the phase of the **T-gate** acting on $|1\rangle$. Since $T|1\rangle = e^{i\pi/4}|1\rangle = e^{2\pi i \cdot 1/8}|1\rangle$, the true phase is $\theta = 1/8 = 0.125$. With 3 counting qubits, the grid resolution is exactly $1/8$, so QPE recovers the phase perfectly — the measured outcome $|001\rangle$ (integer 1, phase $1/8$) dominates with near-unit probability.

The output shows the top 3 measurement outcomes with their corresponding phase candidates and probabilities, followed by the final estimate and absolute error against the true value.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python quantum_phase_estimation.py
```

## Key parameters

- **`n_counting`** (default: `3`) — number of counting qubits. Precision is $1/2^n$; depth grows linearly with $n$.
- **Unitary** (default: T-gate) — swap in any single-qubit unitary. For non-dyadic phases (e.g., S-gate composed with itself irregularly), QPE will produce an approximate answer with a spread distribution.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- NumPy

## References

- Kitaev, A. Y. (1995). *Quantum measurements and the Abelian Stabilizer Problem.* [arXiv:quant-ph/9511026](https://arxiv.org/abs/quant-ph/9511026)
- Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information.* Cambridge University Press. (Section 5.2)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
