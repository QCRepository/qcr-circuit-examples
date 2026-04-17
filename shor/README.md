# Shor's Algorithm — Factoring N = 15

Shor's algorithm (1994) is the quantum algorithm that launched the field — and the reason "quantum computing" appears in the threat models of most modern cryptography. It factors an $n$-bit integer in polynomial time $O((\log N)^3)$, an exponential speedup over the best-known classical algorithm (the general number field sieve, which is sub-exponential but still super-polynomial). Since RSA's security rests on the classical difficulty of factoring, a sufficiently large quantum computer running Shor's algorithm would break it.

The quantum core of Shor's algorithm is **period finding**: given a coprime base $a$, find the smallest $r$ such that $a^r \equiv 1 \pmod{N}$. If $r$ is even and $a^{r/2} \not\equiv -1 \pmod{N}$, then $\gcd(a^{r/2} \pm 1, N)$ yields a non-trivial factor of $N$. Everything else — choosing $a$, running the algorithm, post-processing — is classical.

## What the example does

Factors $N = 15$ using $a = 2$. The order of 2 mod 15 is $r = 4$ (since $2^4 = 16 \equiv 1$), and $\gcd(2^2 \pm 1, 15) = \{3, 5\}$. The circuit is a **heavily compiled** version of Shor's algorithm specialized for this case — it would not generalize to larger $N$ as written.

The example runs the full factoring pipeline:

1. **Quantum period finding** — a 5-qubit circuit (4 data qubits + 1 recycled counting qubit) that produces a measurement $m$ encoding the phase $s/r$ for some $s \in \{0, 1, \ldots, r-1\}$.
2. **Continued fractions** — given $m$ and the phase precision, find the best rational approximation $s/r$ with $r \leq N$.
3. **gcd factor recovery** — apply $\gcd(a^{r/2} \pm 1, N)$ and check for non-trivial factors.

The output shows every measured outcome, its inferred period, and whether that period successfully factors 15 — giving a concrete success rate across 1024 shots.

## Circuit design notes

This example uses two optimizations that are worth understanding because they appear in many compiled Shor implementations:

**Semiclassical QFT (Kitaev-style iterative phase estimation).** A standard QPE for 3 bits of phase would need 3 dedicated counting qubits plus an inverse QFT circuit. Here, a single counting qubit (`qr[4]`) is measured and reset between rounds, with the inverse QFT reduced to classical feed-forward phase corrections (`if_test(cr, k)`). This cuts the qubit count but requires hardware support for mid-circuit measurement and classical control.

**Modular arithmetic compilation.** The operation $x \mapsto ax \bmod 15$ is implemented by hand as a specific sequence of CSWAPs and CNOTs rather than a general controlled-modular-exponentiation circuit. This is only possible because for $N = 15$ and $a = 2$, the modular multiplication happens to coincide with simple qubit permutations and bit-flips. Real Shor's on cryptographically relevant $N$ requires general modular exponentiation circuits (Beauregard 2002 describes a $2n + 3$ qubit construction).

## Interpreting the output

For $r = 4$ with 3 bits of phase precision, the 4 possible peaks are at $m \in \{0, 2, 4, 6\}$ (corresponding to $s \in \{0, 1, 2, 3\}$). Each produces different post-processing outcomes:

| $m$ | phase $m/8$ | continued fraction | period $r$ | factors |
|---|---|---|---|---|
| 0 | 0 | — | — | none (no info) |
| 2 | 1/4 | 1/4 | 4 | 3 × 5 |
| 4 | 1/2 | 1/2 | 2 | 3 × 5 (via aliasing) |
| 6 | 3/4 | 3/4 | 4 | 3 × 5 |

The $m = 4$ case is interesting: continued fractions return $r = 2$, which is an *alias* of the true period 4. The gcd trick still recovers factors because $\gcd(2^1 + 1, 15) = \gcd(3, 15) = 3$ happens to be non-trivial. About 75% of shots yield factors; the remaining 25% ($m = 0$) are useless and would be retried in practice.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
python shor.py
```

## Dependencies

- Python 3.12
- [Qiskit](https://qiskit.org/) (< 2.0)
- Qiskit Aer

## References

- Shor, P. W. (1997). *Polynomial-time algorithms for prime factorization and discrete logarithms on a quantum computer.* SIAM J. Comput. 26, 1484. [doi:10.1137/S0097539795293172](https://doi.org/10.1137/S0097539795293172)
- Beauregard, S. (2003). *Circuit for Shor's algorithm using 2n+3 qubits.* Quantum Inf. Comput. 3, 175. [arXiv:quant-ph/0205095](https://arxiv.org/abs/quant-ph/0205095)

## License

Apache 2.0 — see [LICENSE](./LICENSE).
