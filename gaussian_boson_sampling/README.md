# Gaussian Boson Sampling

Gaussian Boson Sampling (GBS), proposed by Hamilton et al. in 2017, is a variant of standard boson sampling that replaces single-photon Fock states at the input with **squeezed vacuum states**. This seemingly small change has major practical implications: squeezed states are far easier to prepare reliably in the lab than single photons, making GBS significantly more experimentally accessible.

Where standard boson sampling relates to matrix permanents, GBS connects to **hafnians** — another #P-hard quantity. This retains the classical hardness argument while opening the door to real-world applications that go beyond pure sampling. GBS has found connections to graph problems (dense subgraphs, graph similarity), molecular vibronic spectra, and point processes.

Notably, both the Jiuzhang experiments (2020, 2021) from USTC that claimed quantum computational advantage used the GBS model.

## The model

A GBS experiment differs from standard boson sampling in its input preparation:

1. **Squeezed states** — each mode is initialized with a squeezing operation instead of a definite photon number. Squeezing creates a Gaussian state with quantum uncertainty "squeezed" in one quadrature and expanded in the other. In this example, the first 5 of 7 modes are squeezed at $r = 0.25$, while the remaining 2 stay in vacuum.
2. **Interferometer** — same as standard boson sampling: a Haar-random unitary matrix mixes all modes via beamsplitters and phase shifters.
3. **Photon-number measurement** — detecting how many photons appear at each output port. The photon number is now probabilistic (since squeezed states have indefinite photon number), which is what connects GBS to hafnians.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python gaussian_boson_sampling.py
```

The output shows labeled samples with photon counts per mode, reports mean photon number and vacuum rate, and highlights a key difference from standard boson sampling: photon number is not conserved (squeezed states have indefinite photon number). Because the interferometer is randomly generated, exact results differ between runs.

## Dependencies

- Python 3.12
- [Piquasso](https://piquasso.readthedocs.io/) — photonic quantum computing framework
- NumPy, SciPy

## References

- Hamilton, C. S. et al. (2017). *Gaussian Boson Sampling.* [doi:10.1103/PhysRevLett.119.170501](https://doi.org/10.1103/PhysRevLett.119.170501)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
