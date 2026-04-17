# Bacon-Shor Code (2x2)

The Bacon-Shor code is a **subsystem code** — a family of quantum error-correcting codes that sits between stabilizer codes and topological codes in terms of structure. It was developed by combining ideas from Dave Bacon's operator quantum error correction with Peter Shor's original 9-qubit code.

What makes subsystem codes special is that they split the codespace into a **logical subsystem** (the information you care about) and a **gauge subsystem** (degrees of freedom you can ignore). This means syndrome extraction only requires measuring *weight-2* operators (two-qubit checks) instead of the higher-weight stabilizers needed by surface codes or Steane codes. Fewer qubits per check means simpler circuits and lower error propagation during syndrome measurement — a significant practical advantage.

## The 2x2 layout

This example implements the smallest non-trivial Bacon-Shor code: a $2 \times 2$ grid of 4 data qubits encoding information in the X basis. The syndrome extraction proceeds in three rounds:

1. **X-stabilizer checks** — multi-Pauli product measurements $X_0 X_2$ and $X_1 X_3$ (rows), decomposed into Hadamard-CNOT-measure-CNOT-Hadamard sequences.
2. **Z-stabilizer checks** — multi-Pauli product measurements $Z_0 Z_1$ and $Z_2 Z_3$ (columns), decomposed into CNOT-measure-CNOT sequences.
3. **Data readout** — X-basis measurement of all 4 data qubits.

The circuit construction follows the decomposition approach from Gidney's [more-bacon-less-threshold](https://github.com/Strilanc/more-bacon-less-threshold) repository.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python bacon_shor_code.py
```

The output parses each 8-bit measurement record into its components (data readout, Z-syndromes, X-syndromes), verifies that X-stabilizer syndromes are clean across all shots, and summarizes the result distribution.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Bacon, D. (2006). *Operator quantum error-correcting subsystems for self-correcting quantum memories.* [arXiv:quant-ph/0506023](https://arxiv.org/abs/quant-ph/0506023)
- Gidney, C. [more-bacon-less-threshold](https://github.com/Strilanc/more-bacon-less-threshold) — circuit construction reference

## License

Apache 2.0 — see [LICENSE](./LICENSE).
