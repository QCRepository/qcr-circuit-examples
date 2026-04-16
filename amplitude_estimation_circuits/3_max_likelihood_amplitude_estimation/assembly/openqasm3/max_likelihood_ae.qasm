OPENQASM 3.0;
include "stdgates.inc";
bit[1] meas;
qubit[1] q;
u3(0.9272952180016122, 0, 0) q[0];
u3(7.4183617440128975, 0, 0) q[0];
barrier q[0];
meas[0] = measure q[0];
