# Möttönen State Preparation

Preparing an arbitrary quantum state from $|0\rangle^{\otimes n}$ is a fundamental primitive — it appears in everything from amplitude encoding for quantum machine learning to initializing quantum simulations. The Möttönen method (2004) solves this efficiently by decomposing any $n$-qubit state into a cascade of **uniformly controlled rotations**.

The idea: any complex $2^n$-dimensional vector can be described by its amplitudes (magnitudes) and phases (angles). Möttönen's algorithm separates these into two independent cascades:

1. **Y-rotations** — prepare the correct magnitudes by working qubit-by-qubit from the most significant to the least, with each rotation conditioned on the state of all preceding qubits.
2. **Z-rotations** — imprint the correct phases using the same cascade structure.

Each cascade consists of $n$ layers of uniformly controlled rotations, where the angles are computed from the target state vector via a matrix transform related to the Gray code. The result is a circuit with $O(2^n)$ CNOT gates — optimal for generic state preparation.

## What the example does

The example prepares the normalized version of the 8-dimensional vector $[-0.1, 0.2, -0.3, 0.4, -0.5, 0.6, -0.7, 0.8]$ on 3 qubits. After decomposition, the circuit is simulated and the output statevector is compared against the target to verify correctness.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python mottonen_state_prep.py
```

**Expected output:** the target and prepared statevectors printed side by side — they should match to several decimal places.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- NumPy, SciPy
- [SymPy](https://www.sympy.org/) (for Gray code generation in the uniform rotation decomposition)

## References

- Möttönen, M., Vartiainen, J. J., Bergholm, V., & Salomaa, M. M. (2004). *Transformation of quantum states using uniformly controlled rotations.* [arXiv:quant-ph/0407010](https://arxiv.org/abs/quant-ph/0407010)

## License

Apache 2.0 — implementation by Carsten Blank (2018). See [LICENSE](./LICENSE).
