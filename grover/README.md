# Grover's Search Algorithm

Grover's algorithm (1996) is arguably the most famous quantum algorithm after Shor's. It solves the unstructured search problem — finding a marked item in an unsorted database of $N$ elements — in $O(\sqrt{N})$ queries, a provably optimal quadratic speedup over any classical algorithm, which needs $O(N)$ queries in the worst case.

Beyond database search, Grover's algorithm serves as a universal subroutine: any problem that can be framed as "find an input satisfying a given condition" can be accelerated quadratically. This includes constraint satisfaction, optimization, cryptographic key search, and more.

## How it works

The algorithm repeatedly applies two operations — the **Grover iterate** — to amplify the probability of measuring the target state(s):

1. **Oracle** — marks the target states by flipping their phase. For each target $|t\rangle$, the oracle applies $|t\rangle \mapsto -|t\rangle$ while leaving all other states unchanged. This is implemented via X gates on zero-qubits followed by a multi-controlled Z gate.

2. **Diffuser** (amplitude amplification) — reflects all amplitudes about their mean. Concretely: Hadamard all qubits, apply the oracle for the all-zeros state, Hadamard again. This "pushes" amplitude from non-target states toward target states.

After approximately $\frac{\pi}{4}\sqrt{N/M}$ iterations (where $M$ is the number of target states), the targets have near-unit probability.

## What the example does

This implementation supports multiple simultaneous search targets and includes a full CLI interface for experimentation. By default it searches for items `{0, 3, 9, 11}` in a 5-qubit ($N = 32$) space, running 1000 shots and displaying an interactive matplotlib histogram of results. The target states should appear with high frequency (green bars), while all other states are suppressed (red bars).

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python grover.py
```

### CLI options

```
python grover.py -n 4 -s 5 7 -S 2000 -c
```

| Flag | Description | Default |
|------|-------------|---------|
| `-n` | Number of qubits | 5 |
| `-s` | Target integers to search for | 11 9 0 3 |
| `-S` | Number of simulation shots | 1000 |
| `-p` / `--no-p` | Print circuit diagrams | off |
| `-c` / `--no-c` | Combine non-target bars into "Others" | off |
| `-f` | Histogram font size | 10 |

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- NumPy, Matplotlib

## References

- Grover, L. K. (1996). *A Fast Quantum Mechanical Algorithm for Database Search.* [arXiv:quant-ph/9605043](https://arxiv.org/abs/quant-ph/9605043)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
