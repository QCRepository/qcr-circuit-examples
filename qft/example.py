# # Quantum Fourier Transform

# Created based on the Qiskit textbook from https://github.com/Qiskit/textbook/.

# In this tutorial, we introduce the quantum fourier transform (QFT), derive the circuit, and implement it using Qiskit. We show how to run QFT on a simulator and a five qubit device.

# ## 1. Introduction <a id='introduction'></a>
# 
# The Fourier transform occurs in many different versions throughout classical computing, in areas ranging from signal processing to data compression to complexity theory. The quantum Fourier transform (QFT) is the quantum implementation of the discrete Fourier transform over the amplitudes of a wavefunction. It is part of many quantum algorithms, most notably Shor's factoring algorithm and quantum phase estimation. 
# 
# The discrete Fourier transform acts on a vector $(x_0, ..., x_{N-1})$ and maps it to the vector $(y_0, ..., y_{N-1})$ according to the formula
# 
# 
# $$y_k = \frac{1}{\sqrt{N}}\sum_{j=0}^{N-1}x_j\omega_N^{jk}$$
# 
# 
# where $\omega_N^{jk} = e^{2\pi i \frac{jk}{N}}$.
# 
# Similarly, the quantum Fourier transform acts on a quantum state $\vert X\rangle = \sum_{j=0}^{N-1} x_j \vert j \rangle$ and maps it to the quantum state $\vert Y\rangle = \sum_{k=0}^{N-1} y_k \vert k \rangle$ according to the formula
# 
# 
# $$y_k = \frac{1}{\sqrt{N}}\sum_{j=0}^{N-1}x_j\omega_N^{jk}$$
# 
# 
# with $\omega_N^{jk}$ defined as above. Note that only the amplitudes of the state were affected by this transformation.
# 
# This can also be expressed as the map:
# 
# 
# $$\vert j \rangle \mapsto \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1}\omega_N^{jk} \vert k \rangle$$
# 
# 
# 
# Or the unitary matrix:
# 
# 
# $$ U_{QFT} = \frac{1}{\sqrt{N}} \sum_{j=0}^{N-1} \sum_{k=0}^{N-1} \omega_N^{jk} \vert k \rangle \langle j \vert$$
# 
# 

# ## 2. Intuition <a id="intuition"></a>
# 
# The quantum Fourier transform (QFT) transforms between two bases, the computational (Z) basis, and the Fourier basis. The H-gate is the single-qubit QFT, and it transforms between the Z-basis states $|0\rangle$ and $|1\rangle$ to the X-basis states $|{+}\rangle$ and $|{-}\rangle$. In the same way, all multi-qubit states in the computational basis have corresponding states in the Fourier basis. The QFT is simply the function that transforms between these bases.
# 
# $$
# |\text{State in Computational Basis}\rangle \quad \xrightarrow[]{\text{QFT}} \quad |\text{State in Fourier Basis}\rangle
# $$
# 
# $$
# \text{QFT}|x\rangle = |\widetilde{x}\rangle
# $$
# 
# (We often note states in the Fourier basis using the tilde (~)).
# 
# ### 2.1 Counting in the Fourier basis: <a id="counting-fourier"></a>
# 
# In the computational basis, we store numbers in binary using the states $|0\rangle$ and $|1\rangle$:
# 
# ![zbasiscounting](https://raw.githubusercontent.com/QCRepository/qcr-circuit-examples/develop/qft/zbasis-counting.gif)
# 
# Note the frequency with which the different qubits change; the leftmost qubit flips with every increment in the number, the next with every 2 increments, the third with every 4 increments, and so on. In the Fourier basis, we store numbers using different rotations around the Z-axis:
# 
# ![fbasiscounting](https://raw.githubusercontent.com/QCRepository/qcr-circuit-examples/develop/qft/fourierbasis-counting.gif)
# 
# The number we want to store dictates the angle at which each qubit is rotated around the Z-axis. In the state $|\widetilde{0}\rangle$, all qubits are in the state $|{+}\rangle$. As seen in the example above, to encode the state $|\widetilde{5}\rangle$ on 4 qubits, we rotated the leftmost qubit by $\tfrac{5}{2^n} = \tfrac{5}{16}$ full turns ($\tfrac{5}{16}\times 2\pi$ radians). The next qubit is turned double this ($\tfrac{10}{16}\times 2\pi$ radians, or $10/16$ full turns), this angle is then doubled for the qubit after, and so on. 
# 
# Again, note the frequency with which each qubit changes. The leftmost qubit (`qubit 0`) in this case has the lowest frequency, and the rightmost the highest. 
# 

# ## 3. Example 1: 1-qubit QFT <a id='example1'></a>
# 
# Consider how the QFT operator as defined above acts on a single qubit state $\vert\psi\rangle = \alpha \vert 0 \rangle + \beta \vert 1 \rangle$. In this case, $x_0 = \alpha$, $x_1 = \beta$, and $N = 2$. Then,
# 
# 
# 
# $$y_0 = \frac{1}{\sqrt{2}}\left(    \alpha \exp\left(2\pi i\frac{0\times0}{2}\right) + \beta \exp\left(2\pi i\frac{1\times0}{2}\right)      \right) = \frac{1}{\sqrt{2}}\left(\alpha + \beta\right)$$
# 
# 
# 
# and
# 
# 
# 
# $$y_1 = \frac{1}{\sqrt{2}}\left(    \alpha \exp\left(2\pi i\frac{0\times1}{2}\right) + \beta \exp\left(2\pi i\frac{1\times1}{2}\right)      \right) = \frac{1}{\sqrt{2}}\left(\alpha - \beta\right)$$
# 
# 
# 
# such that the final result is the state 
# 
# 
# 
# $$U_{QFT}\vert\psi\rangle = \frac{1}{\sqrt{2}}(\alpha + \beta) \vert 0 \rangle + \frac{1}{\sqrt{2}}(\alpha - \beta)  \vert 1 \rangle$$
# 
# 
# 
# This operation is exactly the result of applying the Hadamard operator ($H$) on the qubit:
# 
# 
# 
# $$H = \frac{1}{\sqrt{2}}\begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}$$
# 
# 
# 
# If we apply the $H$ operator to the state $\vert\psi\rangle = \alpha \vert 0 \rangle + \beta \vert 1 \rangle$, we obtain the new state:
# 
# $$\frac{1}{\sqrt{2}}(\alpha + \beta) \vert 0 \rangle + \frac{1}{\sqrt{2}}(\alpha - \beta)  \vert 1 \rangle 
# \equiv \tilde{\alpha}\vert 0 \rangle + \tilde{\beta}\vert 1 \rangle$$
# 
# Notice how the Hadamard gate performs the discrete Fourier transform for $N = 2$ on the amplitudes of the state. 

# ## 4. The Quantum Fourier transform<a id="qfteqn"></a>

# So what does the quantum Fourier transform look like for larger $N$? Let's derive a transformation for $N=2^n$, $QFT_N$ acting on the state $\vert x \rangle = \vert x_1\ldots x_n \rangle$ where $x_1$ is the most significant bit. This maths is here for those that find it useful, if you struggle with it then don’t worry; as long as you understand the intuition in section 2 then you can continue straight to the next section.
# 
# $$
# \begin{aligned}
# QFT_N\vert x \rangle & = \frac{1}{\sqrt{N}} \sum_{y=0}^{N-1}\omega_N^{xy} \vert y \rangle 
# \\
# & = \frac{1}{\sqrt{N}} \sum_{y=0}^{N-1} e^{2 \pi i xy / 2^n} \vert y \rangle ~\text{since}\: \omega_N^{xy} = e^{2\pi i \frac{xy}{N}} \:\text{and}\: N = 2^n 
# \\
# & = \frac{1}{\sqrt{N}} \sum_{y=0}^{N-1} e^{2 \pi i \left(\sum_{k=1}^n y_k/2^k\right) x} \vert y_1 \ldots y_n \rangle \:\text{rewriting in fractional binary notation}\: y = y_1\ldots y_n, y/2^n = \sum_{k=1}^n y_k/2^k 
# \\
# & = \frac{1}{\sqrt{N}} \sum_{y=0}^{N-1} \prod_{k=1}^n e^{2 \pi i x y_k/2^k } \vert y_1 \ldots y_n \rangle \:\text{after expanding the exponential of a sum to a product of exponentials} 
# \\
# & = \frac{1}{\sqrt{N}} \bigotimes_{k=1}^n  \left(\vert0\rangle + e^{2 \pi i x /2^k } \vert1\rangle \right) \:\text{after rearranging the sum and products, and expanding} 
# \sum_{y=0}^{N-1} = \sum_{y_1=0}^{1}\sum_{y_2=0}^{1}\ldots\sum_{y_n=0}^{1} 
# \\
# & = \frac{1}{\sqrt{N}}
# \left(\vert0\rangle + e^{\frac{2\pi i}{2}x} \vert1\rangle\right) 
# \otimes
# \left(\vert0\rangle + e^{\frac{2\pi i}{2^2}x} \vert1\rangle\right) 
# \otimes  
# \ldots
# \otimes
# \left(\vert0\rangle + e^{\frac{2\pi i}{2^{n-1}}x} \vert1\rangle\right) 
# \otimes
# \left(\vert0\rangle + e^{\frac{2\pi i}{2^n}x} \vert1\rangle\right) 
# \end{aligned}
# $$
# 
# This is a mathematical description of the animation we saw in the intuition section:
#
# ![fbasiscounting](https://raw.githubusercontent.com/QCRepository/qcr-circuit-examples/develop/qft/fourierbasis-counting.gif)

# ## 5. The Circuit that Implements the QFT <a name="circuit"></a>
# 
# The circuit that implements QFT makes use of two gates. The first one is a single-qubit Hadamard gate, $H$, that you already know. From the discussion in [Example 1](#example1) above, you have already seen that the action of $H$ on the single-qubit state $\vert x_k\rangle$ is
# 
# 
# 
# $$H\vert x_k \rangle = \frac{1}{\sqrt{2}}\left(\vert0\rangle + \exp\left(\frac{2\pi i}{2}x_k\right)\vert1\rangle\right)$$
# 
# 
# 
# The second is a two-qubit controlled rotation $CROT_k$ given in block-diagonal form as 
# 
# $$CROT_k = \left[\begin{matrix}
# I&0\\
# 0&UROT_k\\
# \end{matrix}\right]$$
# 
# where 
# 
# $$UROT_k = \left[\begin{matrix}
# 1&0\\
# 0&\exp\left(\frac{2\pi i}{2^k}\right)\\
# \end{matrix}\right]$$
# 
# The action of $CROT_k$ on a two-qubit state $\vert x_l x_j\rangle$ where the first qubit is the control and the second is the target is given by
# 
# 
# 
# $$CROT_k\vert 0x_j\rangle = \vert 0x_j\rangle$$
# 
# 
# and
# 
# 
# $$CROT_k\vert 1x_j\rangle = \exp\left( \frac{2\pi i}{2^k}x_j \right)\vert 1x_j\rangle$$
# 
# 
# 
# Given these two gates, a circuit that implements [an n-qubit QFT](#qfteqn) is shown below.
# 
# ![qft](https://raw.githubusercontent.com/QCRepository/qcr-circuit-examples/develop/qft/qft.png)
# 
# The circuit operates as follows. We start with an n-qubit input state $\vert x_1x_2\ldots x_n\rangle$.
# 
# <ol>
# <li> After the first Hadamard gate on qubit 1, the state is transformed from the input state to 
# 
# $$
# H_1\vert x_1x_2\ldots x_n\rangle = 
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + \exp\left(\frac{2\pi i}{2}x_1\right)\vert1\rangle\right]
# \otimes
# \vert x_2x_3\ldots x_n\rangle
# $$
# 
# <li> After the $UROT_2$ gate on qubit 1 controlled by qubit 2, the state is transformed to
# 
# $$
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + \exp\left(\frac{2\pi i}{2^2}x_2 + \frac{2\pi i}{2}x_1\right)\vert1\rangle\right]
# \otimes
# \vert x_2x_3\ldots x_n\rangle
# $$
# 
# <li> After the application of the last $UROT_n$ gate on qubit 1 controlled by qubit $n$, the state becomes
# 
# $$
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^n}x_n + 
# \frac{2\pi i}{2^{n-1}}x_{n-1} + 
# \ldots + 
# \frac{2\pi i}{2^2}x_2 + 
# \frac{2\pi i}{2}x_1
# \right)
# \vert1\rangle\right]
# \otimes
# \vert x_2x_3\ldots x_n\rangle
# $$
# 
# Noting that 
# 
# $$
# x = 2^{n-1}x_1 + 2^{n-2}x_2 + \ldots + 2^1x_{n-1} + 2^0x_n
# $$
# 
# we can write the above state as 
# 
# $$
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^n}x 
# \right)
# \vert1\rangle\right]
# \otimes
# \vert x_2x_3\ldots x_n\rangle
# $$
# 
# <li> After the application of a similar sequence of gates for qubits $2\ldots n$, we find the final state to be:
# 
# $$
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^n}x 
# \right)
# \vert1\rangle\right]
# \otimes
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^{n-1}}x 
# \right)
# \vert1\rangle\right]
# \otimes
# \ldots
# \otimes
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^{2}}x 
# \right)
# \vert1\rangle\right]
# \otimes
# \frac{1}{\sqrt{2}}
# \left[\vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^{1}}x 
# \right)
# \vert1\rangle\right]
# $$
# 
# which is exactly the QFT of the input state as derived <a href="#qfteqn">above</a> with the caveat that the order of the qubits is reversed in the output state.
# </ol>

# ## 6. Example 2: 3-qubit QFT <a id='example2'></a>
# 
# The steps to creating the circuit for $\vert y_3y_2y_1\rangle = QFT_8\vert x_3x_2x_1\rangle$ would be:
# 
# <ol>
# <li> Apply a Hadamard gate to $\vert x_1 \rangle$
# 
# $$
# |\psi_1\rangle = 
# \vert x_3\rangle
# \otimes
# \vert x_2\rangle
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(\frac{2\pi i}{2}x_1\right) 
# \vert1\rangle\right]
# $$
# 
# <li> Apply a $UROT_2$ gate to $\vert x_1\rangle$ depending on $\vert x_2\rangle$
# 
# $$
# |\psi_2\rangle = 
# \vert x_3\rangle
# \otimes
# \vert x_2\rangle
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^2}x_2 + \frac{2\pi i}{2}x_1
# \right) 
# \vert1\rangle\right]
# $$
# 
# <li> Apply a $UROT_3$ gate to $\vert x_1\rangle$ depending on $\vert x_3\rangle$
# 
# $$
# |\psi_3\rangle = 
# \vert x_3\rangle
# \otimes
# \vert x_2\rangle
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^3}x_3 + \frac{2\pi i}{2^2}x_2 + \frac{2\pi i}{2}x_1
# \right) 
# \vert1\rangle\right]
# $$
# 
# <li> Apply a Hadamard gate to $\vert x_2 \rangle$
# 
# $$
# |\psi_4\rangle = 
# \vert x_3\rangle
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2}x_2
# \right) 
# \vert1\rangle\right]
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^3}x_3 + \frac{2\pi i}{2^2}x_2 + \frac{2\pi i}{2}x_1
# \right) 
# \vert1\rangle\right]
# $$
# 
# <li> Apply a $UROT_2$ gate to $\vert x_2\rangle$ depending on $\vert x_3\rangle$
# 
# $$
# |\psi_5\rangle = 
# \vert x_3\rangle
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^2}x_3 + \frac{2\pi i}{2}x_2
# \right) 
# \vert1\rangle\right]
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^3}x_3 + \frac{2\pi i}{2^2}x_2 + \frac{2\pi i}{2}x_1
# \right) 
# \vert1\rangle\right]
# $$
# 
# <li> Apply a Hadamard gate to $\vert x_3\rangle$
# 
# $$
# |\psi_6\rangle = 
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2}x_3
# \right) 
# \vert1\rangle\right]
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^2}x_3 + \frac{2\pi i}{2}x_2
# \right) 
# \vert1\rangle\right]
# \otimes
# \frac{1}{\sqrt{2}}
# \left[
# \vert0\rangle + 
# \exp\left(
# \frac{2\pi i}{2^3}x_3 + \frac{2\pi i}{2^2}x_2 + \frac{2\pi i}{2}x_1
# \right) 
# \vert1\rangle\right]
# $$
# 
# 
# <li> Keep in mind the reverse order of the output state relative to the desired QFT. Therefore, we must reverse the order of the qubits (in this case swap $y_1$ and $y_3$).

# ## 7. Some Notes About the Form of the QFT Circuit <a id="formnote"></a>

# The example above demonstrates a very useful form of the QFT for $N=2^n$. Note that only the last qubit depends on the values of all the other input qubits and each further bit depends less and less on the input qubits. This becomes important in physical implementations of the QFT, where nearest-neighbor couplings are easier to achieve than distant couplings between qubits.
# 
# Additionally, as the QFT circuit becomes large, an increasing amount of time is spent doing increasingly slight rotations. It turns out that we can ignore rotations below a certain threshold and still get decent results, this is known as the approximate QFT. This is also important in physical implementations, as reducing the number of operations can greatly reduce decoherence and potential gate errors.  

# ## 8. Qiskit Implementation<a id='implementation'></a>
# 
# In Qiskit, the implementation of the $CROT$ gate used in the discussion above is a controlled phase rotation gate. This gate is defined in [OpenQASM](https://github.com/QISKit/openqasm) as
# 
# $$
# CP(\theta) =
# \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & e^{i\theta}\end{bmatrix}
# $$
# 
# Hence, the mapping from the $CROT_k$ gate in the discussion above into the $CP$ gate is found from the equation
# 
# $$
# \theta = 2\pi/2^k = \pi/2^{k-1}
# $$


import numpy as np
from numpy import pi
# importing Qiskit
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Uncomment the following line for visualization
from qiskit.visualization import plot_histogram, plot_bloch_multivector


# ### 8.2 General QFT Function <a id="generalqft"></a>
# 
# We will now create a general circuit for the QFT in Qiskit. Creating large general circuits like this is really where Qiskit shines. 
# 
# It is easier to build a circuit that implements the QFT with the qubits upside down, then swap them afterwards; we will start off by creating the function that rotates our qubits correctly. We need to correctly rotate the second most significant qubit. Then we must deal with the third most significant, and so on. When we get to the end of our `qft_rotations()` function, we can use the same code to repeat the process on the next `n-1` qubits:


def qft_rotations(circuit, n):
    """Performs qft on the first n qubits in circuit (without swaps)"""
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(pi/2**(n-qubit), qubit, n)
    # At the end of our function, we call the same function again on
    # the next qubits (we reduced n by one earlier in the function)
    qft_rotations(circuit, n)

# Let's see how it looks:
qc = QuantumCircuit(4)
qft_rotations(qc,4)

# Uncomment the following line for drawing the circuit
# qc.draw()


# That was easy! Process in which a function calls itself directly or indirectly is called _recursion._ It can greatly simplify code.

# Finally, we need to add the swaps at the end of the QFT function to match the definition of the QFT. We will combine this into the final function `qft()`:


def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

# Let's see how it looks:
qc = QuantumCircuit(4)
qft(qc,4)

# Uncomment the following line for drawing the circuit
# qc.draw()


# This is the generalised circuit for the quantum Fourier transform.


# We now want to demonstrate this circuit works correctly. To do this we must first encode a number in the computational basis. We can see the number 5 in binary is `101`:


bin(5)


# (The `0b` just reminds us this is a binary number). Let's encode this into our qubits:


# Create the circuit
qc = QuantumCircuit(3)

# Encode the state 5
qc.x(0)
qc.x(2)

# Uncomment the following line for drawing the circuit
# qc.draw()


# And let's check the qubit's states using the aer simulator:


sim = AerSimulator()

qc_init = qc.copy()
qc_init.save_statevector()
statevector = sim.run(qc_init).result().get_statevector()

# Uncomment the following line for plotting the vector on the Bloch sphere
# plot_bloch_multivector(statevector)


# Finally, let's use our QFT function and view the final state of our qubits:


qft(qc,3)

# Uncomment the following line for drawing the circuit
# qc.draw()


qc.save_statevector()
statevector = sim.run(qc).result().get_statevector()
print(statevector)

# Uncomment the following line for plotting the vector on the Bloch sphere
# plot_bloch_multivector(statevector)


# We can see out QFT function has worked correctly. Compared the state $|\widetilde{0}\rangle = |{+}{+}{+}\rangle$, Qubit 0 has been rotated by $\tfrac{5}{8}$ of a full turn, qubit 1 by $\tfrac{10}{8}$ full turns (equivalent to $\tfrac{1}{4}$ of a full turn), and qubit 2 by $\tfrac{20}{8}$ full turns (equivalent to $\tfrac{1}{2}$ of a full turn).

# ## 9. References<a id="references"></a>

# 1. M. Nielsen and I. Chuang, Quantum Computation and Quantum Information, Cambridge Series on Information and the Natural Sciences (Cambridge University Press, Cambridge, 2000).
