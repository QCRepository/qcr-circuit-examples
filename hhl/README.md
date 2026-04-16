# HHL Algorithm — Quantum Linear Systems Solver

The HHL algorithm (Harrow, Hassidim, Lloyd, 2009) is a quantum algorithm for solving systems of linear equations $A\vec{x} = \vec{b}$. For an $N \times N$ sparse Hermitian matrix with condition number $\kappa$, HHL runs in $O(\log(N) \cdot s^2 \cdot \kappa^2 / \epsilon)$ time — an **exponential speedup** in the system size compared to classical methods like conjugate gradient, which need $O(Ns\kappa\log(1/\epsilon))$.

There is an important catch: HHL doesn't return the full solution vector $\vec{x}$ (reading it out would take $O(N)$ time, killing the speedup). Instead, it prepares a quantum state $|x\rangle$ proportional to $\vec{x}$ from which you can efficiently extract **functions of the solution** — expectation values, norms, inner products — without ever reading every component. This makes HHL most useful when you only need aggregate information about the answer.

## How it works

The algorithm has three stages:

1. **Quantum Phase Estimation (QPE)** — decomposes $|b\rangle$ in the eigenbasis of $A$ and writes the eigenvalues $\lambda_j$ into an ancilla register as binary fractions.

2. **Conditioned rotation** — for each eigenvalue $\lambda_j$, rotates a flag qubit by an angle proportional to $1/\lambda_j$. This is the step that encodes the matrix inversion: large eigenvalues get small rotations, small eigenvalues get large rotations.

3. **Inverse QPE** — uncomputes the eigenvalue register, leaving behind the solution state $|x\rangle \propto A^{-1}|b\rangle$ conditioned on the flag qubit being $|1\rangle$.

The probability of the flag qubit reading $|1\rangle$ gives the norm of the solution, and any observable can be measured on the solution register.

## What the example does

The example solves a 4x4 tridiagonal Toeplitz system (main diagonal 1, off-diagonal 1/3) with right-hand side $[1.0, -2.1, 3.2, -4.3]$. It computes a `MatrixFunctional` observable from the quantum solution and compares it against the exact classical answer via NumPy.

## Project structure

```
├── hhl_example.py                 # Entry point
├── HHL/                           # Algorithm package (derived from Qiskit)
│   ├── __init__.py
│   ├── hhl.py                     # Core HHL algorithm
│   ├── linear_solver.py           # Abstract base + result class
│   ├── numpy_linear_solver.py     # Classical reference implementation
│   ├── matrices/                  # Hamiltonian evolution implementations
│   │   ├── linear_system_matrix.py
│   │   ├── numpy_matrix.py
│   │   ├── tridiagonal_toeplitz.py
│   │   └── discrete_laplacian.py
│   └── observables/               # Solution observables
│       ├── linear_system_observable.py
│       ├── absolute_average.py
│       └── matrix_functional.py
└── assembly/
    ├── openqasm2/
    │   └── hhl_circuit.qasm       # Pre-exported OpenQASM 2.0 (6378 lines)
    └── openqasm3/
        └── hhl_circuit.qasm       # Pre-exported OpenQASM 3.0 (2375 lines)
```

The `HHL/` package is a self-contained implementation derived from Qiskit Algorithms. It includes pluggable matrix types (Toeplitz, Laplacian, arbitrary NumPy) and observables (absolute average, matrix functional), plus a classical NumPy solver for verification.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python hhl_example.py
```

**Expected output:** the approximate quantum result and the exact classical result for the matrix functional observable, which should be close.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- NumPy, SciPy

## References

- Harrow, A. W., Hassidim, A., & Lloyd, S. (2009). *Quantum Algorithm for Linear Systems of Equations.* [doi:10.1103/PhysRevLett.103.150502](https://doi.org/10.1103/PhysRevLett.103.150502)

## License

Apache 2.0 — derived from [Qiskit Algorithms](https://github.com/qiskit-community/qiskit-algorithms) (C) IBM 2020–2021.
