# Bacon-Shor code 2x2 example in the X basis
#
# Uses the circuit construction from the following repository:
#
# https://github.com/Strilanc/more-bacon-less-threshold
#
# Note: for further generalized constructions of the Bacon-Shor code, refer to
# the ``make_bacon_shor_circuit`` and relevant functions in the mentioned
# repository. Required packages have to be installed such as ``stim``.
from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit, transpile

qc_str = """OPENQASM 2.0;
include "qelib1.inc";

qreg q[4];
creg rec[8];

reset q[0]; h q[0]; // decomposed RX
reset q[1]; h q[1]; // decomposed RX
reset q[2]; h q[2]; // decomposed RX
reset q[3]; h q[3]; // decomposed RX
barrier q;

// --- begin decomposed MPP X0*X2 X1*X3
h q[0];
h q[2];
h q[1];
h q[3];
cx q[2], q[0];
cx q[3], q[1];
measure q[0] -> rec[0];
measure q[1] -> rec[1];
cx q[2], q[0];
cx q[3], q[1];
h q[0];
h q[2];
h q[1];
h q[3];
// --- end decomposed MPP
barrier q;

barrier q;

// --- begin decomposed MPP Z0*Z1 Z2*Z3
cx q[1], q[0];
cx q[3], q[2];
measure q[0] -> rec[2];
measure q[2] -> rec[3];
cx q[1], q[0];
cx q[3], q[2];
// --- end decomposed MPP
barrier q;

barrier q;

h q[0]; measure q[0] -> rec[4]; h q[0]; // decomposed MX
h q[1]; measure q[1] -> rec[5]; h q[1]; // decomposed MX
h q[2]; measure q[2] -> rec[6]; h q[2]; // decomposed MX
h q[3]; measure q[3] -> rec[7]; h q[3]; // decomposed MX
barrier q;

"""
qc = QuantumCircuit.from_qasm_str(qc_str)

# use local simulator
simulator = AerSimulator()
sim_job = simulator.run(qc, shots=1000)
result = sim_job.result()
counts = result.get_counts()
print(counts)

# Uncomment the following line to draw the circuit:
# print(qc.draw())
