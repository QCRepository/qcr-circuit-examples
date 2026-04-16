# Boson Sampling

Boson sampling is a computational problem proposed by Scott Aaronson and Alex Arkhipov in 2011 that gave the field one of its earliest — and strongest — arguments that quantum devices can outperform classical computers at *something*, even without full-blown fault-tolerant quantum computing.

The setup is elegant: send identical photons into a linear optical network (an interferometer described by a unitary matrix), let them interfere, and count where they come out. Predicting the output distribution requires computing the permanent of a matrix — a problem that is #P-hard for classical computers, yet a photonic device solves it naturally by just… being physics.

This makes boson sampling a leading candidate for demonstrating quantum computational advantage with near-term photonic hardware.

## The model

A boson sampling experiment has three ingredients:

1. **Input state** — a Fock state specifying how many photons enter each mode. In this example, one photon enters each of the first 3 out of 7 modes: `[1, 1, 1, 0, 0, 0, 0]`.
2. **Interferometer** — a random unitary matrix drawn from the Haar measure that mixes the modes. Think of it as a network of beamsplitters and phase shifters.
3. **Measurement** — photon-number detection at the output, producing a sample from the distribution whose probabilities relate to matrix permanents.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python boson_sampling.py
```

The output shows labeled samples with photon counts per mode, verifies photon number conservation (total should always equal 3), and reports the number of distinct output configurations. Because the interferometer is randomly generated, exact results differ between runs.

## Dependencies

- Python 3.12
- [Piquasso](https://piquasso.readthedocs.io/) — photonic quantum computing framework
- NumPy, SciPy

## References

- Aaronson, S. & Arkhipov, A. (2011). *The Computational Complexity of Linear Optics.* [arXiv:1011.3245](https://arxiv.org/abs/1011.3245)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
