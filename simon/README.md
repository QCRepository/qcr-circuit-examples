# Simon's Algorithm

Simon's algorithm (1994) holds a special place in the history of quantum computing: it was the **first algorithm to demonstrate an exponential separation** between quantum and classical query complexity, and directly inspired Shor's factoring algorithm the following year. Both solve instances of the **hidden subgroup problem** — Simon's over $(\mathbb{Z}/2\mathbb{Z})^n$, Shor's over $\mathbb{Z}/N\mathbb{Z}$.

## The problem

You're given a black-box function $f : \{0,1\}^n \to \{0,1\}^n$ promised to be either:
- **One-to-one** (all outputs distinct), or
- **Two-to-one with period $b$**, meaning $f(x) = f(y)$ if and only if $y = x \oplus b$ for some hidden non-zero $b$.

The task is to determine $b$ (or conclude the function is one-to-one).

**Classical lower bound:** $\Omega(2^{n/2})$ queries — you essentially need the birthday paradox to collide two inputs.

**Quantum upper bound:** $O(n)$ queries plus $O(n^3)$ classical post-processing.

The gap is exponential, and Simon proved it using an elegant structure that reappears throughout the algorithm zoo: the Hadamard-oracle-Hadamard sandwich.

## How the algorithm works

1. **Prepare** the input register in $|0\rangle^{\otimes n}$ and apply Hadamards to get the uniform superposition.
2. **Query the oracle**, which entangles the input with $f(x)$ in the output register.
3. **Apply Hadamards** to the input register again and measure.

The key lemma: after Hadamards, the measured outcome $z$ is uniform over all vectors satisfying $z \cdot b \equiv 0 \pmod{2}$. After $n - 1$ linearly independent measurements, the null space is 1-dimensional and contains only $\{0, b\}$ — so $b$ is uniquely determined. A single run gives one equation; rerun as many times as needed.

## What the example does

Runs the circuit **one shot at a time** and stops as soon as $b$ is uniquely determined — which is the point a researcher should see, because it directly shows the $O(n)$ query complexity. A 1000-shot batch would work but misleads by suggesting you *need* all those shots. In reality, for $n = 3$ you need about 2 linearly independent non-trivial measurements; the rest are statistical filler.

For each shot, the output shows:

- The measured $z$
- The linear constraint $z \cdot b = 0 \pmod 2$ it imposes (or marks it as trivial when $z = 0$)
- The remaining non-zero $b$ candidates consistent with all observations so far

When the candidate set shrinks to a single value, that is $b$. Typical runs terminate in 2–4 shots for $n = 3$: most queries contribute a new constraint (informative), while occasional $z = 0$ measurements or linearly dependent repeats do not. This closely mirrors real usage — you simply keep querying until the accumulated equations pin $b$ down.

The recovery uses brute-force search over the $2^n - 1$ non-zero candidates for clarity; for large $n$ this should be replaced by Gaussian elimination over GF(2), which reaches the same result in $O(n^3)$ time.

A visualization of the circuit structure is included as `simon_example.png`.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python simon.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Simon, D. R. (1997). *On the Power of Quantum Computation.* SIAM J. Comput. 26, 1474. [doi:10.1137/S0097539796298637](https://doi.org/10.1137/S0097539796298637)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
