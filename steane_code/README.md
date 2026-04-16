# Steane 7-Qubit Code

The Steane code (Andrew Steane, 1996) is the **[[7,1,3]] CSS code** derived from the classical Hamming [7,4,3] code. It encodes 1 logical qubit into 7 physical qubits using 3 X-type and 3 Z-type stabilizer generators, and corrects any single-qubit error — just like the Shor 9-qubit code, but with two fewer qubits and much nicer fault-tolerance properties.

What makes Steane special in practice is that the Hamming code is **self-dual** (the same parity check matrix generates both X-type and Z-type stabilizers). This makes the logical Clifford operators — H, S, and CNOT — **transversal**: the encoded H is literally a physical H applied to each of the 7 qubits, and similarly for CNOT between two logical qubits. Transversality is the gold standard for fault-tolerant gates because it cannot spread single-qubit errors into correlated multi-qubit errors.

## Stabilizers

The 6 stabilizer generators (this example uses the Nielsen–Chuang §4.4 convention):

| Generator | Type | Support |
|---|---|---|
| $g_1 = X_0 X_4 X_5 X_6$ | X | 0, 4, 5, 6 |
| $g_2 = X_1 X_3 X_5 X_6$ | X | 1, 3, 5, 6 |
| $g_3 = X_2 X_3 X_4 X_5$ | X | 2, 3, 4, 5 |
| $g_4 = Z_0 Z_2 Z_3 Z_6$ | Z | 0, 2, 3, 6 |
| $g_5 = Z_1 Z_2 Z_4 Z_6$ | Z | 1, 2, 4, 6 |
| $g_6 = Z_0 Z_1 Z_2 Z_5$ | Z | 0, 1, 2, 5 |

All 9 X-Z pairs commute (each pair has exactly 2 common qubits → two anticommutations cancel). All weights are 4, which is standard for Steane.

Every single-qubit Pauli error produces a unique non-zero syndrome — the 3-bit syndrome is a **Hamming-style address** of the error location. Here are the X-error syndromes (the 3-bit output of the Z-type stabilizers, read as $(s_4, s_5, s_6)$):

| X error on qubit | Syndrome |
|---|---|
| 0 | (1, 0, 1) |
| 1 | (0, 1, 1) |
| 2 | (1, 1, 1) |
| 3 | (1, 0, 0) |
| 4 | (0, 1, 0) |
| 5 | (0, 0, 1) |
| 6 | (1, 1, 0) |

Z-error syndromes (read from the X-type stabilizers) follow the analogous pattern. All 7 non-zero syndromes appear, bijectively, giving a lookup-table decoder.

## Logical operators

$$Z_L = Z_1 Z_4 Z_5 \qquad X_L = X_1 X_2 X_3$$

Both are weight-3 — the minimum possible for this distance-3 code. They're obtained from the weight-7 all-Z and all-X operators by multiplying with an appropriate stabilizer.

## Encoding

Preparing $|0\rangle_L$ from $|0\rangle^{\otimes 7}$ uses a direct CSS encoder:

1. Apply $H$ to qubits 0, 1, 2 (the "encoding qubits" — each seeds a distinct X-stabilizer orbit).
2. From each encoding qubit $q$, apply a CNOT into the other qubits of that stabilizer's support.

The resulting state is the uniform superposition of the 8 even-weight Hamming codewords, which is $|0\rangle_L$ — a +1 eigenstate of every stabilizer and of $Z_L$.

## Logical $Z_L$ readout with classical correction

Because $Z_L = Z_1 Z_4 Z_5$ is Z-type, we read it out by **destructively measuring all 7 data qubits in the Z basis** and computing the parity of bits 1, 4, 5.

But a single X error on one of $\{q_1, q_4, q_5\}$ flips the corresponding readout bit, which corrupts the parity. The classical correction is:

1. Read the Z-stabilizer syndrome (aux[3..5]).
2. Look up the X-error location from the syndrome.
3. If that location is in $\{1, 4, 5\}$, flip the readout bit at that position.
4. Compute $Z_L$ as the parity of the (now-corrected) bits 1, 4, 5.

Z errors don't affect the Z-basis readout at all (they add phases, not bit flips), so they need no correction for this measurement. Y errors are handled automatically because the correction only looks at the X-part of the syndrome.

This is the standard Hamming lookup-decoding approach, and it makes every single-qubit Pauli error recoverable at the classical post-processing layer.

## What the example does

Runs the full cycle — encode $|0\rangle_L$ → inject error → extract syndrome → destructive $Z_L$ readout with syndrome-directed correction — across 8 representative scenarios. For each, it verifies both:

1. The **syndrome** decodes to the correct error label.
2. The **logical $|0\rangle_L$** is preserved in 100% of shots.

The error set deliberately covers X errors both inside and outside $Z_L$'s support, Z errors (which shouldn't affect the readout), and a Y error whose X-part requires correction.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python steane_code.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Steane, A. M. (1996). *Error correcting codes in quantum theory.* Phys. Rev. Lett. 77, 793. [doi:10.1103/PhysRevLett.77.793](https://doi.org/10.1103/PhysRevLett.77.793)
- Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information.* Cambridge University Press. (Section 4.4)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
