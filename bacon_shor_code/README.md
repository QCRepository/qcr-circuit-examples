# Bacon-Shor Code (2×2)

The Bacon-Shor code is a **subsystem code** — a family of quantum error-correcting codes that sits between stabilizer codes and topological codes in terms of structure. It was developed by combining ideas from Dave Bacon's operator quantum error correction with Peter Shor's original 9-qubit code.

What makes subsystem codes special is that they split the codespace into a **logical subsystem** (the information you care about) and a **gauge subsystem** (degrees of freedom you can ignore). This means syndrome extraction only requires measuring *weight-2* operators (two-qubit checks) instead of the higher-weight stabilizers needed by surface codes or Steane codes. Fewer qubits per check means simpler circuits and lower error propagation during syndrome measurement — a significant practical advantage.

## The 2×2 layout

This example implements the smallest non-trivial Bacon-Shor code: a 2×2 grid of 4 data qubits encoding 1 logical qubit, with code **distance d = 2** — it can *detect* a single error but cannot *correct* any. Actual error correction starts at the 3×3 layout (d = 3). In subsystem-code terminology, the 2×2 code's X-type gauges are the row operators X₀X₂ and X₁X₃; the Z-type gauges are the column operators Z₀Z₁ and Z₂Z₃; and the two stabilizers are the weight-4 products X₀X₁X₂X₃ and Z₀Z₁Z₂Z₃, inferred as products of same-type gauge outcomes.

The example prepares |+⟩ on each data qubit and runs one round of syndrome extraction followed by an X-basis readout:

1. **X-gauge measurements** — weight-2 parity measurements of X₀X₂ and X₁X₃ (row gauges), decomposed into Hadamard-CNOT-measure-CNOT-Hadamard sequences.
2. **Z-gauge measurements** — weight-2 parity measurements of Z₀Z₁ and Z₂Z₃ (column gauges), decomposed into CNOT-measure-CNOT sequences.
3. **Data readout** — X-basis measurement of all 4 data qubits.

The circuit construction follows the decomposition approach from Gidney's [more-bacon-less-threshold](https://github.com/Strilanc/more-bacon-less-threshold) repository.

## What the example does

This is a **reference implementation** of the 2×2 Bacon-Shor syndrome-extraction circuit. The 2×2 layout is structurally fixed — the only runtime knob is the shot count. What you get: a clean gate-level demonstration of how weight-2 parity measurements compose into a functional QEC syndrome-extraction block, with every operation visible in the accompanying OpenQASM 2.0 source.

> **Scope note — what this does NOT demonstrate:** this example shows syndrome *extraction*, not full error correction. Because no noise is injected and the initial state (+X on every data qubit) is an eigenstate of the X-gauges, the X-gauge outcomes are always `00` — by construction, not because errors were corrected. A single syndrome round is run; there's no decoding, no recovery, no multi-round benchmarking. The 2×2 code's distance of 2 also caps what's possible in principle: detection without correction. For error-correction research — multi-round simulation, decoding, threshold analysis — researchers typically reach for [Stim](https://github.com/quantumlib/Stim) + [PyMatching](https://github.com/oscarhiggott/PyMatching).

## Default parameters

| Parameter | Value |
|-----------|-------|
| Layout | 2×2 (4 data qubits) |
| Initial state | +X on each data qubit |
| Shots | 1000 |

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python bacon_shor_code.py
```

### CLI options

```
python bacon_shor_code.py -S 5000
```

| Flag | Description | Default |
|------|-------------|---------|
| `-S` / `--shots` | Shots for the syndrome-extraction circuit (must be ≥ 1) | 1000 |

## Output

Each shot produces an 8-bit measurement record:
- **rec[0], rec[1]** — X-gauge outcomes (X₀X₂, X₁X₃)
- **rec[2], rec[3]** — Z-gauge outcomes (Z₀Z₁, Z₂Z₃)
- **rec[4..7]** — X-basis data readout of the 4 qubits

The script parses each bitstring into those three groups, lists distinct outcomes with counts, and verifies that X-gauge outcomes are clean across all shots. Z-gauge outcomes and data readouts are expected to be random per-bit — +X is not a Z eigenstate. The two stabilizer values can be recovered from the gauge outcomes by taking products: X-stabilizer = rec[0] ⊕ rec[1], Z-stabilizer = rec[2] ⊕ rec[3].

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Bacon, D. (2006). *Operator quantum error-correcting subsystems for self-correcting quantum memories.* [arXiv:quant-ph/0506023](https://arxiv.org/abs/quant-ph/0506023)
- Gidney, C. [more-bacon-less-threshold](https://github.com/Strilanc/more-bacon-less-threshold) — circuit construction reference

## License

Apache 2.0 — see [LICENSE](./LICENSE).
