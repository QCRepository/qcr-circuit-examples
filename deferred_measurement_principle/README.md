# Deferred Measurement Principle

The deferred measurement principle states that **measurements can always be moved to the end of a quantum circuit** without changing the probability distribution of the results. Any mid-circuit measurement followed by a classically controlled operation can be replaced by a quantum controlled gate with the measurement postponed to the final step.

This is not just a theoretical curiosity — it is a core tool in quantum circuit compilation. Many hardware platforms do not natively support mid-circuit measurements or classical feedforward, so the ability to defer measurements is essential for transpiling circuits to run on real devices.

## Demonstration: quantum teleportation

This example uses quantum teleportation as the vehicle to illustrate the principle, implementing the same protocol in two equivalent ways:

### Version 1 — Mid-circuit measurements

The textbook teleportation protocol:
1. Alice and Bob share a Bell pair.
2. Alice entangles her qubit with the state to teleport and measures both qubits **immediately**.
3. Based on the two classical bits, Bob applies X and/or Z corrections using classical control (`if_test`).

### Version 2 — Deferred measurements

The same protocol, rewritten without mid-circuit measurements:
1. Alice and Bob share a Bell pair.
2. Alice entangles her qubit with the state to teleport.
3. Instead of measuring and classically controlling, the corrections are applied as **quantum controlled** CNOT and CZ gates.
4. All measurements happen at the end.

Both versions are simulated with 100,000 shots and produce statistically identical output distributions — demonstrating that deferring measurements preserves the physics.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python deferred_measurement.py
```

The output shows a side-by-side probability table for each Bell measurement outcome across both circuits, along with the per-outcome absolute difference in probability and the maximum difference overall. Both distributions should land near uniform 0.25 with a max difference well under 0.01 at 100,000 shots — confirming the two approaches are statistically equivalent.

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Nielsen, M. A. & Chuang, I. L. (2010). *Quantum Computation and Quantum Information.* Cambridge University Press. (Section 4.4)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
