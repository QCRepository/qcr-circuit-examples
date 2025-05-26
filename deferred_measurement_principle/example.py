# Deferred measurement principle

# This notebook demonstrates quantum teleportation in two ways: with
# mid-circuit measurements and by applying the deferred measurement principle.
#
# These two circuits produce the same probability distribution.
#
# We use Qiskit's built-in simulators to test our quantum circuit.
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.result import marginal_counts
from qiskit.quantum_info import random_statevector

qr = QuantumRegister(3, name="q")    # Protocol uses 3 qubits
crz = ClassicalRegister(1, name="crz") # and 2 classical bits
crx = ClassicalRegister(1, name="crx") # in 2 different registers
teleportation_circuit_with_mid_circuit_measurements = QuantumCircuit(qr, crz, crx)

def create_bell_pair(qc, a, b):
    """Creates a bell pair in qc using qubits a & b"""
    qc.h(a) # Put qubit a into state |+>
    qc.cx(a,b) # CNOT with a as control and b as target

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_mid_circuit_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_mid_circuit_measurements, 1, 2)

def alice_gates(qc, psi, a):
    qc.cx(psi, a)
    qc.h(psi)

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_mid_circuit_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_mid_circuit_measurements, 1, 2)

teleportation_circuit_with_mid_circuit_measurements.barrier() # Use barrier to separate steps
alice_gates(teleportation_circuit_with_mid_circuit_measurements, 0, 1)

def measure_and_send(qc, a, b):
    """Measures qubits a & b and 'sends' the results to Bob"""
    qc.barrier()
    qc.measure(a,0)
    qc.measure(b,1)

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_mid_circuit_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_mid_circuit_measurements, 1, 2)

teleportation_circuit_with_mid_circuit_measurements.barrier() # Use barrier to separate steps
alice_gates(teleportation_circuit_with_mid_circuit_measurements, 0, 1)

measure_and_send(teleportation_circuit_with_mid_circuit_measurements, 0 ,1)

def bob_gates(qc, qubit, crz, crx):
    # Here we use if_test to control our gates with a classical bit instead of
    # a qubit
    # Apply gates if the registers are in the state '1'
    with qc.if_test((crx, 1)):
        qc.x(qubit)

    with qc.if_test((crz, 1)):
        qc.z(qubit)

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_mid_circuit_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_mid_circuit_measurements, 1, 2)

teleportation_circuit_with_mid_circuit_measurements.barrier() # Use barrier to separate steps
alice_gates(teleportation_circuit_with_mid_circuit_measurements, 0, 1)

measure_and_send(teleportation_circuit_with_mid_circuit_measurements, 0, 1)

teleportation_circuit_with_mid_circuit_measurements.barrier() # Use barrier to separate steps
bob_gates(teleportation_circuit_with_mid_circuit_measurements, 2, crz, crx)

sim = AerSimulator()
sim_job = sim.run(teleportation_circuit_with_mid_circuit_measurements, shots=100000)
result = sim_job.result()
counts = result.get_counts()

# If you want to draw the circuit, uncomment the following line:
# print(teleportation_circuit_with_mid_circuit_measurements.draw())
print(counts)

# 2. circuit - no mid-circuit measurements

qr = QuantumRegister(3, name="q")    # Protocol uses 3 qubits
teleportation_circuit_with_deferred_measurements = QuantumCircuit(qr, crz, crx)

def create_bell_pair(qc, a, b):
    """Creates a bell pair in qc using qubits a & b"""
    qc.h(a) # Put qubit a into state |+>
    qc.cx(a,b) # CNOT with a as control and b as target

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_deferred_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_deferred_measurements, 1, 2)

def alice_gates(qc, psi, a):
    qc.cx(psi, a)
    qc.h(psi)

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_deferred_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_deferred_measurements, 1, 2)

teleportation_circuit_with_deferred_measurements.barrier() # Use barrier to separate steps
alice_gates(teleportation_circuit_with_deferred_measurements, 0, 1)

def measure_and_send(qc, a, b):
    """Measures qubits a & b and 'sends' the results to Bob"""
    qc.barrier()
    qc.measure(a,0)
    qc.measure(b,1)

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_deferred_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_deferred_measurements, 1, 2)

teleportation_circuit_with_deferred_measurements.barrier() # Use barrier to separate steps
alice_gates(teleportation_circuit_with_deferred_measurements, 0, 1)

measure_and_send(teleportation_circuit_with_deferred_measurements, 0 ,1)

qr = QuantumRegister(3, name="q")
crz, crx = ClassicalRegister(1, name="crz"), ClassicalRegister(1, name="crx")
teleportation_circuit_with_deferred_measurements = QuantumCircuit(qr, crz, crx)

create_bell_pair(teleportation_circuit_with_deferred_measurements, 1, 2)

alice_gates(teleportation_circuit_with_deferred_measurements, 0, 1)

# Apply the quantum controlled gates instead of classical control
teleportation_circuit_with_deferred_measurements.cx(0, 2)
teleportation_circuit_with_deferred_measurements.cz(1, 2)

# Measure the qubits at the end of the circuit
measure_and_send(teleportation_circuit_with_deferred_measurements, 0, 1)

sim = AerSimulator()
sim_job = sim.run(teleportation_circuit_with_deferred_measurements, shots=100000)
result = sim_job.result()
counts = result.get_counts()

# If you want to draw the circuit, uncomment the following line:
# print(teleportation_circuit_with_deferred_measurements.draw())
print(counts)
