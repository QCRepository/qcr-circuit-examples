import math
import random
import sys
from fractions import Fraction
from builtins import input
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import math

"""
Shor's algorithm example in Qiskit

Given an integer N, find its prime factors.

Circuit example with N = 15 and x = 2 (reference paper: http://science.sciencemag.org/content/351/6277/1068)

where N and x are the coprimes.

The example was created based on the https://github.com/mett29/Shor-s-Algorithm repository.
"""

def circuit_2mod15(qc, qr, cr):
    qc.cswap(qr[4], qr[3], qr[2])
    qc.cswap(qr[4], qr[2], qr[1])
    qc.cswap(qr[4], qr[1], qr[0])

def circuit_aperiod15(qc, qr, cr, a):
    r"""Optimizes the Quantum Fourier Transform (QFT) in Shor's algorithm using Kitaev's approach.

        This method follows the approach described in the paper:  
        [Science, 351(6277), 1068](http://science.sciencemag.org/content/351/6277/1068).  

        Key optimizations:
        
        1. **Semiclassical QFT**:  
           - Replaces a QFT on M qubits with a semiclassical QFT acting repeatedly on a single qubit.  
           - Uses classical feed-forward measurement to control subsequent qubit operations.  
           - Reduces the number of two-qubit gates by leveraging measurement outcomes for adaptive gate application.  
           - Reference: [Phys. Rev. Lett. 76, 3228](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.76.3228).  

        2. **Optimized Conditional Multiplication**:  
           - Instead of performing full multiplications, the algorithm conditionally maps  
             \(|1\rangle \to |a^{2^k} \mod N\rangle\), reducing computational overhead.  
           - This enhances fidelity and performance, as the initial operation’s accuracy  
             impacts all subsequent computations.

        3. **Additional Improvements**:  
           - Requires in-sequence measurements.  
           - Uses qubit recycling to reset measured qubits.  
           - Implements feed-forward gate adjustments based on measurement results.  
           - Incorporates controlled quantum operations.  

        **Note:** A combined experiment implementing all these features has not yet been realized.
    """
    
    # Initialize q[0] to |1> 
    qc.x(qr[0])

    # Apply a**4 mod 15
    # ------------------
    qc.h(qr[4])
    qc.h(qr[4])
    qc.measure(qr[4], cr[0])
    qc.reset(qr[4])

    # Apply a**2 mod 15
    # ------------------
    qc.h(qr[4])
    qc.cx(qr[4], qr[2])
    qc.cx(qr[4], qr[0])
    
    with qc.if_test((cr, 1)):
        qc.p(math.pi / 2., qr[4])
    qc.h(qr[4])
    qc.measure(qr[4], cr[1])
    qc.reset(qr[4])

    # Apply a mod 15
    # ------------------
    qc.h(qr[4])
    circuit_2mod15(qc, qr, cr)
    with qc.if_test((cr, 3)):
        qc.p(3. * math.pi / 4., qr[4])
    with qc.if_test((cr, 2)):
        qc.p(math.pi / 2., qr[4])
    with qc.if_test((cr, 1)):
        qc.p(math.pi / 4., qr[4])
    qc.h(qr[4])
    qc.measure(qr[4], cr[2])

q = QuantumRegister(5, 'q')
c = ClassicalRegister(5, 'c')

shor = QuantumCircuit(q, c)
circuit_aperiod15(shor, q, c, 2)

backend = AerSimulator()
shots = 1024

sim_job = backend.run(shor, shots=shots)
sim_result = sim_job.result()
sim_data = sim_result.get_counts(shor)
print(sim_data)