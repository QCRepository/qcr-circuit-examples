# 3-Qubit Repetition Code

The repetition code is the simplest possible quantum error-correcting code — and the natural starting point for understanding all others. It protects a single logical qubit against **bit-flip errors** (X errors) by encoding it redundantly across 3 physical qubits: $|0\rangle_L = |000\rangle$ and $|1\rangle_L = |111\rangle$. A single bit-flip on any one physical qubit can be detected *and corrected* without ever measuring the logical state.

This code doesn't protect against phase-flip (Z) errors — for that you'd rotate the basis and use a phase-flip repetition code — but as a pedagogical stepping stone it introduces every moving part of stabilizer-based quantum error correction: encoding, syndrome extraction via ancilla qubits, classical decoding, and conditional correction.

## How the circuit works

The example runs a single round of the full QEC cycle:

1. **Encoding** — prepare the logical qubit in $|1\rangle_L$ by flipping data qubit 0 and copying it to qubits 1 and 2 via CNOTs. The encoded state is $|111\rangle$.
2. **Error injection** — apply an X gate on one of the three data qubits (or none) to simulate a bit-flip.
3. **Syndrome extraction** — measure the two parity stabilizers using ancilla qubits:
   - `syndrome[0]` = parity of qubits 0 and 1 ($Z_0 Z_1$)
   - `syndrome[1]` = parity of qubits 0 and 2 ($Z_0 Z_2$)
4. **Correction** — decode the 2-bit syndrome and apply an X on the affected qubit:
   - `00` → no error
   - `01` → qubit 1 flipped
   - `10` → qubit 2 flipped
   - `11` → qubit 0 flipped
5. **Readout** — measure all three data qubits; the result should be `111` in every shot if correction succeeded.

The ancilla qubits are **conditionally reset** after syndrome measurement using the measured values directly — avoiding an extra round of measurement when reusing them for multi-round QEC. This pattern scales to the surface code and other large QEC cycles.

## What the example demonstrates

The example runs the full circuit against **4 scenarios** — no error, and a bit-flip on each of the 3 data qubits — and verifies that:

- The syndrome in each case matches the expected value (uniquely identifying the error location)
- The data register reads `111` in 100% of shots across all scenarios, confirming that correction restored the logical state

This is the full "correction proof" the skeleton version of this circuit was missing: not just the scaffolding, but evidence that the scaffolding works.

## Companion notebook

An accompanying Jupyter notebook, `build-repetition-codes.ipynb`, walks through the construction step-by-step with intermediate visualizations and is useful for teaching or deeper exploration.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python repetition_code.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- NumPy

## References

- Shor, P. W. (1995). *Scheme for reducing decoherence in quantum computer memory.* Phys. Rev. A 52, R2493(R). [doi:10.1103/PhysRevA.52.R2493](https://doi.org/10.1103/PhysRevA.52.R2493)
- Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information.* Cambridge University Press. (Section 10.1)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
