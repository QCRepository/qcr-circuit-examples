# Variational Quantum Eigensolver (VQE)

VQE (Peruzzo et al., 2014) is the workhorse **hybrid quantum-classical algorithm** for finding ground-state energies. Given a Hamiltonian $H$, VQE uses a parameterized quantum circuit $U(\theta)$ to prepare trial states $|\psi(\theta)\rangle = U(\theta)|0\rangle$, evaluates the energy $\langle \psi(\theta)|H|\psi(\theta)\rangle$ on a quantum device, and feeds that energy to a classical optimizer which updates $\theta$. Iterate until convergence.

The variational principle guarantees that the expectation value is always an upper bound on the true ground state energy, so VQE's output is a bound on $E_0$ — tight when the ansatz is expressive enough to cover the ground state manifold.

This is arguably the most-studied quantum algorithm of the NISQ era because it is **shallow by design**: the quantum circuit only needs to be deep enough to prepare a reasonable approximation, and the classical optimizer absorbs the rest of the work. Applications span quantum chemistry (molecular ground states), condensed matter (Ising/Heisenberg models), combinatorial optimization (QAOA is a close cousin), and as a benchmark for near-term hardware.

## What this example does

Finds the ground state energy of a 2-qubit Hamiltonian given as a sum of Pauli strings:

$$H = 0.398 \cdot Y_1 Z_0 - 0.398 \cdot Z_1 I_0 - 0.0113 \cdot Z_1 Z_0 + 0.181 \cdot X_1 X_0$$

Three pieces wire together:

1. **Ansatz:** Qiskit's `EfficientSU2` with default settings (reps = 3) — a hardware-friendly variational circuit with 16 trainable parameters. This is a common generic ansatz when you have no a priori structure.
2. **Estimator:** `qiskit-ibm-runtime`'s `EstimatorV2` backed by the local `AerSimulator`. Each call evaluates $\langle \psi(\theta)|H|\psi(\theta)\rangle$ for the current parameters.
3. **Optimizer:** SciPy's `COBYLA` — a gradient-free trust-region method well-suited to noisy objective functions like those from shot-limited estimators.

Because the system is only 2 qubits, the example also computes the **exact ground state energy classically** (by diagonalizing the $4 \times 4$ Hamiltonian matrix) and reports the VQE result's absolute error. This is the standard way to benchmark VQE in research — without a classical reference, you can't tell whether the optimizer converged to the true ground state or got stuck in a local minimum.

The output shows convergence at a handful of checkpoints (iteration 0, 25%, 50%, 75%, final) so you can see the descent qualitatively.

## Reproducibility

The initial ansatz parameters are drawn from `np.random.default_rng(seed=42)` so runs are deterministic. If you want to see multiple random initializations (e.g., to study convergence variance), change or remove the seed.

## Pre-exported circuit

`assembly/openqasm3/vqe_circuit.qasm` is a specific optimized-parameter instance of the ansatz exported as OpenQASM 3.0 — useful as a reference circuit or for hardware experimentation without re-running the optimizer.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python vqe.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer
- qiskit-ibm-runtime (for `EstimatorV2`)
- NumPy, SciPy

## References

- Peruzzo, A. et al. (2014). *A variational eigenvalue solver on a photonic quantum processor.* Nature Communications 5, 4213. [doi:10.1038/ncomms5213](https://doi.org/10.1038/ncomms5213)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
