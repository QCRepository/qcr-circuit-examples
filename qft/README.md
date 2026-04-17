# Quantum Fourier Transform (QFT)

The Quantum Fourier Transform is the quantum analogue of the classical discrete Fourier transform — and it is arguably the single most important subroutine in quantum computing. It appears inside Shor's factoring algorithm, quantum phase estimation, the HHL linear systems solver, and many quantum simulation methods. Where the classical DFT on $N$ elements takes $O(N \log N)$ operations (the celebrated FFT), the QFT achieves the same transformation in just $O(\log^2 N)$ gates — an exponential improvement.

What the QFT does is transform a quantum state from the **computational basis** ($|0\rangle, |1\rangle, \ldots$) into the **Fourier basis**, where each basis state encodes a frequency component. Concretely, it maps:

$$|j\rangle \mapsto \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i \, jk/N} |k\rangle$$

## How the circuit works

The QFT circuit has an elegant recursive structure:

1. **Hadamard** on the most significant qubit — creates a superposition weighted by $e^{2\pi i \cdot 0.j_n}$.
2. **Controlled phase rotations** — each subsequent qubit applies a $\text{CP}(\pi/2^d)$ gate conditioned on the earlier qubits, refining the phase to encode more bits of the frequency.
3. **Recurse** on the remaining $n-1$ qubits.
4. **Swap** qubits to reverse the bit order (the QFT naturally produces outputs in reversed order).

For $n$ qubits, this requires $n(n-1)/2$ controlled phase gates and $n$ Hadamards.

## What the example does

The example applies the QFT to a 3-qubit register initialized in state $|5\rangle = |101\rangle$. The output statevector is printed, showing the Fourier-transformed amplitudes. Each amplitude's phase encodes the frequency structure of the input — you can verify that $|e^{2\pi i \cdot 5k/8}|$ matches the expected Fourier coefficients.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python qft.py
```

**Expected output:**
```
Input: 5 (binary: 0b101)
QFT output statevector:
[0.354+0.j, 0.354+0.354j, -0.354j, ...]
```

All amplitudes have equal magnitude ($1/\sqrt{8} \approx 0.354$) — only the phases differ, encoding the frequency information.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- NumPy

## References

- Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information.* Cambridge University Press. (Section 5.1)
- Coppersmith, D. (1994). *An approximate Fourier transform useful in quantum computing.* [arXiv:quant-ph/0201067](https://arxiv.org/abs/quant-ph/0201067)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
