OPENQASM 2.0;
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
