# Superdense Coding

Superdense coding (Bennett & Wiesner, 1992) is a small but striking result about how much classical information you can push through a single qubit. The plain answer — by Holevo's bound — is **one classical bit per qubit**. But if Alice and Bob share an entangled pair *beforehand*, Alice can send two classical bits by transmitting just one qubit. The entanglement isn't magic; it's a pre-distributed resource that amplifies the capacity of the later transmission.

This is the **dual** of quantum teleportation: teleportation uses two classical bits plus shared entanglement to transmit one qubit; superdense coding uses one qubit plus shared entanglement to transmit two classical bits. Both protocols are foundational to quantum communication and quantum networks.

## The protocol

1. **Setup.** A third party prepares a Bell pair $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$ and gives one qubit to Alice, one to Bob.
2. **Encode.** Alice applies one of 4 gates to *her* qubit — $I$, $X$, $Z$, or $ZX$ — depending on the 2-bit message she wants to send. These four operations map the shared state to the four orthogonal Bell states:

   | Message | Gate | Resulting Bell state |
   |---|---|---|
   | 00 | $I$ | $\|\Phi^+\rangle = (\|00\rangle + \|11\rangle)/\sqrt{2}$ |
   | 01 | $X$ | $\|\Psi^+\rangle = (\|01\rangle + \|10\rangle)/\sqrt{2}$ |
   | 10 | $Z$ | $\|\Phi^-\rangle = (\|00\rangle - \|11\rangle)/\sqrt{2}$ |
   | 11 | $ZX$ | $\|\Psi^-\rangle = (\|01\rangle - \|10\rangle)/\sqrt{2}$ |

3. **Transmit.** Alice sends her single qubit to Bob.
4. **Decode.** Bob now holds both qubits. He performs a **Bell measurement** (CNOT followed by H on one qubit, then measures both in the computational basis), which distinguishes the four Bell states. The measurement outcome is Alice's original 2-bit message.

Because the four Bell states are mutually orthogonal, Bob recovers the message with probability 1.

## What the example does

Runs the full protocol for all four messages `00, 01, 10, 11` with 1000 shots each. For each message, the output shows:

- Alice's encoding gate
- The resulting Bell state
- Bob's most frequent measurement outcome
- A match check against the sent message

Since the protocol is deterministic, every shot should reproduce the sent message exactly — 1000/1000 across all four messages.

A diagram of the protocol is included as `superdense.jpg`.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python superdense_coding.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Bennett, C. H. & Wiesner, S. J. (1992). *Communication via one- and two-particle operators on Einstein-Podolsky-Rosen states.* Phys. Rev. Lett. 69, 2881. [doi:10.1103/PhysRevLett.69.2881](https://doi.org/10.1103/PhysRevLett.69.2881)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
