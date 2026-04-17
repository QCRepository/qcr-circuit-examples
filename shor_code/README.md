# Shor 9-Qubit Code

The Shor code (Peter Shor, 1995) is the original quantum error-correcting code — the first proof that quantum information could be protected against noise at all. It corrects **any** single-qubit error by correcting both X (bit-flip) and Z (phase-flip) errors independently, a non-trivial achievement since the naive extension of classical repetition codes handles only one error type at a time.

The construction is elegantly recursive. Three physical qubits encoded in a bit-flip repetition code catch single bit-flips. Three such "blocks" then wrapped in a phase-flip code catch single phase-flips between blocks. The combined 9-qubit code corrects any single-qubit error — and because any single-qubit operator is a linear combination of $\{I, X, Y, Z\}$, the code handles *every* single-qubit fault, including continuous ones like small rotations.

## Code structure

The encoded logical basis states are:

$$|0\rangle_L = \frac{1}{2\sqrt{2}} (|000\rangle + |111\rangle)^{\otimes 3}$$
$$|1\rangle_L = \frac{1}{2\sqrt{2}} (|000\rangle - |111\rangle)^{\otimes 3}$$

The stabilizer group has 8 generators — all mutually commuting, each with eigenvalue $+1$ on the encoded states:

| Group | Weight | Detects |
|---|---|---|
| $Z_0 Z_1, Z_1 Z_2$ | 2 | X errors in block 0 |
| $Z_3 Z_4, Z_4 Z_5$ | 2 | X errors in block 1 |
| $Z_6 Z_7, Z_7 Z_8$ | 2 | X errors in block 2 |
| $X_0 X_1 X_2 X_3 X_4 X_5$ | 6 | Z errors in blocks 0 or 1 |
| $X_3 X_4 X_5 X_6 X_7 X_8$ | 6 | Z errors in blocks 1 or 2 |

One notable asymmetry: the Z-type stabilizers *localize* X errors to a specific qubit within a block (the two bits distinguish qubits 0/1/2 in the block). The X-type stabilizers only localize Z errors to a **block** — Z errors on different qubits within the same block differ by a stabilizer, so they're equivalent and all corrected by the same Z gate.

## Logical operators

Because of the concatenation structure, the logical operators have a counterintuitive form:

$$Z_L = X_0 X_1 X_2 \quad \text{(any block's X product)}$$
$$X_L = Z_0 Z_3 Z_6 \quad \text{(one Z per block)}$$

The logical $Z_L$ is built from *X* operators, and vice versa — an artifact of wrapping the inner bit-flip code with an outer phase-flip code (the outer layer swaps the X/Z roles between logical and physical).

## Logical $Z_L$ readout with majority-vote correction

To verify that the code actually preserves logical information — not just that syndromes identify errors — the example performs a destructive logical Z readout:

1. Apply $H^{\otimes 9}$ to the data qubits (converts X-basis measurement into Z-basis).
2. Measure all 9 data qubits in the computational basis.
3. For each 3-qubit block, compute its parity (sum mod 2).
4. **Majority vote across the three blocks** gives $Z_L$: even majority → $+1$ ($|0\rangle_L$), odd majority → $-1$ ($|1\rangle_L$).

**Why majority vote acts as correction.** For uncorrupted $|0\rangle_L$, every block deterministically has even parity after the H layer. An $X_q$ error has *no effect* on this readout (the identity $H X_q H = Z_q$ means an X error becomes a sign flip in the rotated basis, which doesn't change measurement outcomes). A $Z_q$ error flips the parity of *one* block; the other two still vote even. So any single-qubit error is absorbed by the majority vote — that *is* the correction, applied classically at readout time. This is exactly how Shor-family codes are decoded in practice: classical post-processing on measurement outcomes.

## What the example does

The example runs the full cycle — encode $|0\rangle_L$ → inject error → extract syndrome → destructive logical readout — against 8 scenarios (no error plus representative X/Z/Y errors across all three blocks). For each scenario it verifies both:

1. The **syndrome** correctly identifies the error ("can we detect what went wrong?")
2. The **logical $|0\rangle_L$ is preserved** in 100% of shots ("did the code actually protect our information?")

The second check is the one that matters — it confirms the code does what it's supposed to, not just that the stabilizer arithmetic works.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python shor_code.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Shor, P. W. (1995). *Scheme for reducing decoherence in quantum computer memory.* Phys. Rev. A 52, R2493(R). [doi:10.1103/PhysRevA.52.R2493](https://doi.org/10.1103/PhysRevA.52.R2493)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
