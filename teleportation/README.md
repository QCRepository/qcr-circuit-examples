# Quantum Teleportation

Quantum teleportation (Bennett, Brassard, Crépeau, Jozsa, Peres, Wootters; 1993) is one of the foundational results of quantum information — and arguably its most famously named. It lets Alice transmit an **unknown** quantum state $|\psi\rangle$ to Bob using **no quantum channel at all**, provided they share a pre-distributed Bell pair and can send 2 classical bits between them.

The qubit never physically traverses the gap. The no-cloning theorem is respected: Alice's copy of $|\psi\rangle$ is destroyed during the protocol. Only the *information* is transferred. This is the dual of superdense coding (which sends 2 classical bits using 1 qubit + entanglement).

## The protocol

Three qubits, one Bell pair, two classical bits:

1. **Setup.** A Bell pair $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$ is shared between Alice and Bob (Alice holds $q_1$, Bob holds $q_2$). Alice also has the mystery qubit $q_0$ in state $|\psi\rangle$.
2. **Alice's Bell measurement.** Alice applies CNOT($q_0$, $q_1$) followed by H($q_0$), then measures both $q_0$ and $q_1$ in the computational basis. The two outcomes form a 2-bit classical message.
3. **Classical transmission.** Alice sends the 2 bits to Bob through a classical channel.
4. **Bob's correction.** Depending on the 2 bits, Bob applies $I$, $X$, $Z$, or $ZX$ to his qubit $q_2$. The result is that $q_2$ is now in state $|\psi\rangle$ (up to global phase).

The specific correction table:

| Alice's outcome ($q_0$, $q_1$) | Bob's correction |
|---|---|
| (0, 0) | $I$ |
| (0, 1) | $X$ |
| (1, 0) | $Z$ |
| (1, 1) | $ZX$ |

## Verification via inverse preparation

A careful way to verify teleportation is: prepare $|\psi\rangle = U|0\rangle$ for some known $U$, run the protocol, then apply $U^\dagger$ to Bob's qubit. If teleportation succeeded, $U^\dagger|\psi\rangle = |0\rangle$ and the verification measurement yields 0 deterministically. Any deviation means the protocol failed.

This is stronger than comparing statevectors (which is fragile under mid-circuit measurements and classical feedback), and it works for any test state.

## What the example does

Runs teleportation for 5 representative test states and verifies each with the inverse-preparation trick:

- $|0\rangle$ — trivial baseline
- $|1\rangle = X|0\rangle$ — other computational basis state
- $|+\rangle = H|0\rangle$ — equal superposition
- $|-\rangle = XH|0\rangle$ — equal superposition with a phase
- $R_y(\pi/3)|0\rangle$ — arbitrary non-Clifford superposition

For each, the verification measurement should read 0 in every shot if teleportation works correctly.

A schematic of the protocol is included as `tele1.jpg`.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python teleportation.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Bennett, C. H., Brassard, G., Crépeau, C., Jozsa, R., Peres, A., & Wootters, W. K. (1993). *Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels.* Phys. Rev. Lett. 70, 1895. [doi:10.1103/PhysRevLett.70.1895](https://doi.org/10.1103/PhysRevLett.70.1895)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
