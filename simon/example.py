# # Simon's Algorithm

# Created based on the Qiskit textbook from https://github.com/Qiskit/textbook/.

# In this section, we first introduce the Simon problem, and classical and quantum algorithms to solve it. We then implement the quantum algorithm using Qiskit, and run on a simulator and device.

# ## 1. Introduction <a id='introduction'></a>
#
# Simon's algorithm, first introduced in Reference [1], was the first quantum algorithm to show an exponential speed-up versus the best classical algorithm in solving a specific problem. This inspired the quantum algorithms based on the quantum Fourier transform, which is used in the most famous quantum algorithm: Shor's factoring algorithm.
#
# ### 1a. Simon's Problem <a id='problem'> </a>
#
# We are given an unknown blackbox function $f$, which is guaranteed to be either one-to-one ($1:1$) or two-to-one ($2:1$), where one-to-one and two-to-one functions have the following properties:
#
# - **one-to-one**: maps exactly one unique output for every input. An example with a function that takes 4 inputs is:
#
# $$f(1) \rightarrow 1, \quad f(2) \rightarrow 2, \quad f(3) \rightarrow 3, \quad f(4) \rightarrow 4$$
#
# - **two-to-one**: maps exactly two inputs to every unique output. An example with a function that takes 4 inputs is:
#
# $$f(1) \rightarrow 1, \quad f(2) \rightarrow 2, \quad f(3) \rightarrow 1, \quad f(4) \rightarrow 2$$
#
# This two-to-one mapping is according to a hidden bitstring, $b$, where:
#
# $$
# \textrm{given }x_1,x_2: \quad f(x_1) = f(x_2) \\
# \textrm{it is guaranteed }: \quad x_1 \oplus x_2 = b
# $$
#
# Given this blackbox $f$, how quickly can we determine if $f$ is one-to-one or two-to-one? Then, if $f$ turns out to be two-to-one, how quickly can we determine $b$? As it turns out, both cases boil down to the same problem of finding $b$, where a bitstring of $b={000...}$ represents the one-to-one $f$.

# ### 1b. Simon's Algorithm <a id='algorithm'> </a>
#
# #### Classical Solution
#
# Classically, if we want to know what $b$ is with 100% certainty for a given $f$, we have to check up to $2^{n−1}+1$  inputs, where n is the number of bits in the input. This means checking just over half of all the possible inputs until we find two cases of the same output. Much like the Deutsch-Jozsa problem, if we get lucky, we could solve the problem with our first two tries. But if we happen to get an $f$ that is one-to-one, or get _really_ unlucky with an $f$ that’s two-to-one, then we’re stuck with the full $2^{n−1}+1$.
# There are known algorithms that have a lower bound of $\Omega(2^{n/2})$ (see Reference 2 below), but generally speaking the complexity grows exponentially with n.

# #### Quantum Solution
#
# The quantum circuit that implements Simon's algorithm is shown below.
#
# ![image1](https://raw.githubusercontent.com/QCRepository/qcr-circuit-examples/develop/simon/simon_example.png)
#
# Where the query function, $\text{Q}_f$ acts on two quantum registers as:
#
#
# $$ \lvert x \rangle \lvert a \rangle \rightarrow \lvert x \rangle \lvert a \oplus f(x) \rangle $$
#
# In the specific case that the second register is in the state $|0\rangle = |00\dots0\rangle$ we have:
#
# $$ \lvert x \rangle \lvert 0 \rangle \rightarrow \lvert x \rangle \lvert f(x) \rangle $$
#
# The algorithm involves the following steps.
#
# 1. Two $n$-qubit input registers are initialized to the zero state:
#
#    $$\lvert \psi_1 \rangle = \lvert 0 \rangle^{\otimes n} \lvert 0 \rangle^{\otimes n} $$
#
# 2. Apply a Hadamard transform to the first register:
#
#    $$\lvert \psi_2 \rangle = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0,1\}^{n} } \lvert x \rangle\lvert 0 \rangle^{\otimes n}  $$
#
# 3. Apply the query function $\text{Q}_f$:
#
#    $$ \lvert \psi_3 \rangle = \frac{1}{\sqrt{2^n}} \sum_{x \in \{0,1\}^{n} } \lvert x \rangle \lvert f(x) \rangle $$
#
# 4. Measure the second register. A certain value of $f(x)$ will be observed. Because of the setting of the problem, the observed value $f(x)$ could correspond to two possible inputs: $x$ and $y = x \oplus b $. Therefore the first register becomes:
#
#    $$\lvert \psi_4 \rangle = \frac{1}{\sqrt{2}}  \left( \lvert x \rangle + \lvert y \rangle \right)$$
#
#    where we omitted the second register since it has been measured.
#
# 5. Apply Hadamard on the first register:
#
#    $$ \lvert \psi_5 \rangle = \frac{1}{\sqrt{2^{n+1}}} \sum_{z \in \{0,1\}^{n} } \left[  (-1)^{x \cdot z} + (-1)^{y \cdot z} \right]  \lvert z \rangle  $$
#
# 6. Measuring the first register will give an output only if:
#
#    $$ (-1)^{x \cdot z} = (-1)^{y \cdot z} $$
#    which means:
#
#    $$
#    x \cdot z = y \cdot z \\
#    x \cdot z = \left( x \oplus b \right) \cdot z \\
#    x \cdot z = x \cdot z \oplus b \cdot z \\
#    b \cdot z = 0 \text{ (mod 2)}
#    $$
#
#    A string $z$ will be measured, whose inner product with $b = 0$. Thus, repeating the algorithm $\approx n$ times, we will be able to obtain $n$ different values of $z$ and the following system of equation can be written:
#
#    $$ \begin{cases} b \cdot z_1 = 0 \\ b \cdot z_2 = 0 \\ \quad \vdots \\ b \cdot z_n = 0 \end{cases}$$
#
#    From which $b$ can be determined, for example by Gaussian elimination.
#
# So, in this particular problem the quantum algorithm performs exponentially fewer steps than the classical one. Once again, it might be difficult to envision an application of this algorithm (although it inspired the most famous algorithm created by Shor) but it represents the first proof that there can be an exponential speed-up in solving a specific problem by using a quantum computer rather than a classical one.

# ## 2. Example  <a id='example'></a>
#
# Let's see the example of Simon's algorithm for 2 qubits with the secret string $b=11$, so that $f(x) = f(y)$ if $y = x \oplus b$. The quantum circuit to solve the problem is:
#
# ![image2](images/simon_example.png)
#
# 1. Two $2$-qubit input registers are initialized to the zero state:
#
#    $$\lvert \psi_1 \rangle = \lvert 0 0 \rangle_1 \lvert 0 0 \rangle_2 $$
#
# 2. Apply Hadamard gates to the qubits in the first register:
#
#    $$\lvert \psi_2 \rangle = \frac{1}{2} \left( \lvert 0 0 \rangle_1 + \lvert 0 1 \rangle_1 + \lvert 1 0 \rangle_1 + \lvert 1 1 \rangle_1 \right) \lvert 0 0 \rangle_2 $$
#
# 3. For the string $b=11$, the query function can be implemented as `$\text{Q}_f = CX_{1_a 2_a}CX_{1_a 2_b}CX_{1_b 2_a}CX_{1_b 2_b}$` (as seen in the circuit diagram above):
#
#    $$
#    \begin{aligned}
#    \lvert \psi_3 \rangle  = \frac{1}{2} ( \;
#      & \lvert 0 0 \rangle_1 \; \lvert 0\oplus 0 \oplus 0, & 0 \oplus 0 \oplus 0 \rangle_2 &\\[5pt]
#    + & \lvert 0 1 \rangle_1 \; \lvert 0\oplus 0 \oplus 1, & 0 \oplus 0 \oplus 1 \rangle_2 &\\[6pt]
#    + & \lvert 1 0 \rangle_1 \; \lvert 0\oplus 1 \oplus 0, & 0 \oplus 1 \oplus 0 \rangle_2 &\\[6pt]
#    + & \lvert 1 1 \rangle_1 \; \lvert 0\oplus 1 \oplus 1, & 0 \oplus 1 \oplus 1 \rangle_2 & \; )\\
#    \end{aligned}
#    $$
#
#    Thus:
#
#    $$
#    \begin{aligned}
#    \lvert \psi_3 \rangle = \frac{1}{2} ( \quad
#    & \lvert 0 0 \rangle_1  \lvert 0 0 \rangle_2 & \\[6pt]
#    + & \lvert 0 1 \rangle_1 \lvert 1  1 \rangle_2 & \\[6pt]
#    + & \lvert 1 0 \rangle_1 \lvert  1   1  \rangle_2 & \\[6pt]
#    + & \lvert 1 1 \rangle_1 \lvert 0 0 \rangle_2 & \; )\\
#    \end{aligned}
#    $$
#
# 4. We measure the second register. With $50\%$ probability we will see either $\lvert  0   0  \rangle_2$ or $\lvert  1   1  \rangle_2$. For the sake of the example, let us assume that we see $\lvert  1   1  \rangle_2$. The state of the system is then
#    $$ \lvert \psi_4 \rangle = \frac{1}{\sqrt{2}}  \left( \lvert  0   1  \rangle_1 + \lvert  1   0  \rangle_1 \right)  $$
#    where we omitted the second register since it has been measured.
#
# 5. Apply Hadamard on the first register
#    $$ \lvert \psi_5 \rangle = \frac{1}{2\sqrt{2}} \left[ \left( \lvert 0 \rangle + \lvert 1 \rangle \right) \otimes \left( \lvert 0 \rangle - \lvert 1 \rangle \right) + \left( \lvert 0 \rangle - \lvert 1 \rangle \right) \otimes \left( \lvert 0 \rangle + \lvert 1 \rangle \right)  \right] \\
#    =  \frac{1}{2\sqrt{2}} \left[ \lvert 0 0 \rangle - \lvert 0 1 \rangle + \lvert 1 0 \rangle - \lvert 1 1 \rangle    + \lvert 0 0 \rangle + \lvert 0 1 \rangle - \lvert 1 0 \rangle - \lvert 1 1 \rangle \right] \\
#    = \frac{1}{\sqrt{2}} \left( \lvert 0 0 \rangle - \lvert 1 1 \rangle \right)$$
#
# 6. Measuring the first register will give either $\lvert 0 0 \rangle$ or $\lvert 1 1 \rangle$ with equal probability.
#
# 7. If we see $\lvert 1 1 \rangle$, then:
#
#    $$ b \cdot 11 = 0 $$
#
#    which tells us that $b \neq 01$ or $10$, and the two remaining potential solutions are $b = 00$ or $b = 11$. Note that $b = 00$ will always be a trivial solution to our simultaneous equations. If we repeat steps 1-6 many times, we would only measure $|00\rangle$ or $|11\rangle$ as
#
#    $$ b \cdot 11 = 0 $$
#    $$ b \cdot 00 = 0 $$
#
#    are the only equations that satisfy $b=11$. We can verify $b=11$ by picking a random input ($x_i$) and checking    $f(x_i) = f(x_i \oplus b)$. For example:
#
#    $$ 01 \oplus b = 10 $$
#    $$ f(01) = f(10) = 11$$

# ## 3. Qiskit Implementation <a id='implementation'></a>
#
# We now implement Simon's algorithm for an example with $3$-qubits and $b=110$.

# importing Qiskit
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, transpile

# import basic plot tools
from qiskit.visualization import plot_histogram

def simon_oracle(b):
    """Returns a Simon oracle for bitstring b.

    Note: this function is used as found in the archived
    ``qiskit-community/qiskit-textbook``:
    ``https://github.com/qiskit-community/qiskit-textbook/blob/master/qiskit-textbook-src/qiskit_textbook/tools/__init__.py``.
    """
    b = b[::-1] # reverse b for easy iteration
    n = len(b)
    qc = QuantumCircuit(n*2)
    # Do copy; |x>|0> -> |x>|x>
    for q in range(n):
        qc.cx(q, q+n)
    if '1' not in b:
        return qc  # 1:1 mapping, so just exit
    i = b.find('1') # index of first non-zero bit in b
    # Do |x> -> |s.x> on condition that q_i is 1
    for q in range(n):
        if b[q] == '1':
            qc.cx(i, (q)+n)
    return qc

# The function `simon_oracle` creates a Simon oracle for the bitstring `b`. This is given without explanation, but we will discuss the method in [section 4](#oracle).
#
# In Qiskit, measurements are only allowed at the end of the quantum circuit. In the case of Simon's algorithm, we actually do not care about the output of the second register, and will only measure the first register.

b = '110'

n = len(b)
simon_circuit = QuantumCircuit(n*2, n)

# Apply Hadamard gates before querying the oracle
simon_circuit.h(range(n))

# Apply barrier for visual separation
simon_circuit.barrier()

simon_circuit = simon_circuit.compose(simon_oracle(b))

# Apply barrier for visual separation
simon_circuit.barrier()

# Apply Hadamard gates to the input register
simon_circuit.h(range(n))

# Measure qubits
simon_circuit.measure(range(n), range(n))

# ### 3a. Experiment with Simulators  <a id='simulation'></a>
#
# We can run the above circuit on the simulator.

# use local simulator
simulator = AerSimulator()
sim_job = simulator.run(simon_circuit, shots=1000)
result = sim_job.result()
counts = result.get_counts()
print(counts)



# Since we know $b$ already, we can verify these results do satisfy $b\cdot z  = 0 \pmod{2}$:

# Calculate the dot product of the results
def bdotz(b, z):
    accum = 0
    for i in range(len(b)):
        accum += int(b[i]) * int(z[i])
    return (accum % 2)

for z in counts:
    print( '{}.{} = {} (mod 2)'.format(b, z, bdotz(b,z)) )


# Using these results, we can recover the value of $b = 110$ by solving this set of simultaneous equations. For example, say we first measured `001`, this tells us:
#
# $$
# \require{cancel}
# \begin{aligned}
# b \cdot 001 &= 0 \\
# (b_2 \cdot 0) + (b_1 \cdot 0) + (b_0 \cdot 1) & = 0 \\
# (\cancel{b_2 \cdot 0}) + (\cancel{b_1 \cdot 0}) + (b_0 \cdot 1) & = 0 \\
# b_0 & = 0\\
# \end{aligned}
# $$
#
# If we next measured `111`, we have:
#
# $$
# \require{cancel}
# \begin{aligned}
# b \cdot 111 &= 0 \\
# (b_2 \cdot 1) + (b_1 \cdot 1) + (\cancel{0 \cdot 1}) & = 0 \\
# (b_2 \cdot 1) + (b_1 \cdot 1) & = 0 \\
# \end{aligned}
# $$
#
# Which tells us either:
#
# $$ b_2 = b_1 = 0, \quad b = 000 $$
#
# or
#
# $$ b_2 = b_1 = 1, \quad b = 110 $$
#
# Of which $b  = 110$ is the non-trivial solution to our simultaneous equations. We can solve these problems in general using [Gaussian elimination](https://mathworld.wolfram.com/GaussianElimination.html), which has a run time of $O(n^3)$.

# ## 4. Oracle <a id='oracle'></a>
#
# The above [example](#example) and [implementation](#implementation) of Simon's algorithm are specifically for specific values of $b$. To extend the problem to other secret bit strings, we need to discuss the Simon query function or oracle in more detail.
#
# The Simon algorithm deals with finding a hidden bitstring $b \in \{0,1\}^n$ from an oracle $f_b$ that satisfies $f_b(x) = f_b(y)$ if and only if $y = x \oplus b$ for all $x \in \{0,1\}^n$.  Here, the $\oplus$ is the bitwise XOR operation. Thus, if $b = 0\ldots 0$, i.e., the all-zero bitstring, then $f_b$ is a 1-to-1 (or, permutation) function. Otherwise, if $b \neq 0\ldots 0$, then $f_b$ is a 2-to-1 function.
#
# In the algorithm, the oracle receives $|x\rangle|0\rangle$ as input. With regards to a predetermined $b$, the oracle writes its output to the second register so that it transforms the input to $|x\rangle|f_b(x)\rangle$ such that $f(x) = f(x\oplus b)$ for all $x \in \{0,1\}^n$.
#
# Such a blackbox function can be realized by the following procedures.
#
# -  Copy the content of the first register to the second register.
# $$
# |x\rangle|0\rangle \rightarrow |x\rangle|x\rangle
# $$
#
# -  **(Creating 1-to-1 or 2-to-1 mapping)** If $b$ is not all-zero, then there is the least index $j$ so that $b_j = 1$. If $x_j = 0$, then XOR the second register with $b$. Otherwise, do not change the second register.
# $$
# |x\rangle|x\rangle \rightarrow |x\rangle|x \oplus b\rangle~\mbox{if}~x_j = 0~\mbox{for the least index j}
# $$
#
# -  **(Creating random permutation)** Randomly permute and flip the qubits of the second register.
# $$
# |x\rangle|y\rangle \rightarrow |x\rangle|f_b(y)\rangle
# $$
#

# ## 5. Problems <a id='problems'></a>
#
# 1. Implement a general Simon oracle using Qiskit.
# 2. Test your general Simon oracle with the secret bitstring $b=1001$, on a simulator and device. Are the results what you expect? Explain why.

# ## 6. References <a id='references'></a>
#
# 1. Daniel R. Simon (1997) "On the Power of Quantum Computation" SIAM Journal on Computing, 26(5), 1474–1483, [doi:10.1137/S0097539796298637](https://doi.org/10.1137/S0097539796298637)
# 2. Guangya Cai and Daowen Qiu. Optimal separation in exact query complexities for Simon's problem. Journal of Computer and System Sciences 97: 83-93, 2018, [https://doi.org/10.1016/j.jcss.2018.05.001](https://doi.org/10.1016/j.jcss.2018.05.001)
