# Bernstein-Vazirani Algorithm

The Bernstein-Vazirani algorithm (1993) solves a clean and satisfying problem: given a black-box function $f(x) = s \cdot x \mod 2$ (bitwise dot product with a secret string $s$), find $s$. Classically, you need $n$ queries — one per bit of $s$. The quantum algorithm finds the entire string in **a single query**.

It is closely related to the Deutsch-Jozsa algorithm (both are built on the same Hadamard-oracle-Hadamard sandwich), but where Deutsch-Jozsa asks a yes/no question ("constant or balanced?"), Bernstein-Vazirani extracts a concrete $n$-bit answer. This makes it a natural stepping stone toward understanding the power of quantum parallelism before tackling more complex algorithms like Simon's or Shor's.

## How it works

The algorithm is beautifully simple:

1. **Prepare** $n$ input qubits in $|0\rangle$ and one ancilla in $|1\rangle$.
2. **Hadamard** all qubits — the input goes into equal superposition, the ancilla into $|-\rangle$.
3. **Query the oracle** — for each position $i$ where $s_i = 1$, a CNOT from qubit $i$ to the ancilla kicks back a phase of $(-1)^{s_i}$ onto the input register.
4. **Hadamard** the input qubits again — the phase pattern constructively interferes to produce exactly $|s\rangle$.
5. **Measure** — the result is the secret string, deterministically, in one shot.

The oracle is the key: phase kickback converts a function evaluation into a phase pattern, and Hadamard transforms convert that phase pattern into a computational basis state. No amplitude amplification needed — the answer appears with probability 1.

## What the example does

The example encodes the secret string `"110101"` (6 qubits), runs the circuit with a single shot on Qiskit's Aer simulator, and asserts that the measured output matches the secret exactly.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python bernstein_vazirani.py
```

**Expected output:**
```
Secret: 110101
Measured: 110101
```

Try changing the `secret` variable to any binary string to see the algorithm recover it in one shot.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Bernstein, E. & Vazirani, U. (1993). *Quantum Complexity Theory.* [doi:10.1137/S0097539796300921](https://doi.org/10.1137/S0097539796300921)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
