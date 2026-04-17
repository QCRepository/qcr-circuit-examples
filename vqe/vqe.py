"""
Variational Quantum Eigensolver (VQE) implementation.

Finds the ground state energy of a Hamiltonian using a hybrid
quantum-classical optimization approach.
"""

import time

import numpy as np
from scipy.optimize import minimize

from qiskit_aer import AerSimulator
from qiskit.circuit.library import EfficientSU2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator

def build_callback(ansatz, hamiltonian, estimator, callback_dict):
    """Return callback function that uses Estimator instance,
    and stores intermediate values into a dictionary.

    Parameters:
        ansatz (QuantumCircuit): Parameterized ansatz circuit
        hamiltonian (SparsePauliOp): Operator representation of Hamiltonian
        estimator (Estimator): Estimator primitive instance
        callback_dict (dict): Mutable dict for storing values

    Returns:
        Callable: Callback function object
    """

    def callback(current_vector):
        """Callback function storing previous solution vector,
        computing the intermediate cost value, and displaying number
        of completed iterations and average time per iteration.

        Values are stored in pre-defined 'callback_dict' dictionary.

        Parameters:
            current_vector (ndarray): Current vector of parameters
                                      returned by optimizer
        """
        # Keep track of the number of iterations
        callback_dict["iters"] += 1
        # Set the prev_vector to the latest one
        callback_dict["prev_vector"] = current_vector
        # Compute the value of the cost function at the current vector
        callback_dict["cost_history"].append(
            estimator.run([(ansatz, hamiltonian, current_vector)])
            .result()[0]
        )
        # Grab the current time
        current_time = time.perf_counter()
        # Find the total time of the execute (after the 1st iteration)
        if callback_dict["iters"] > 1:
            callback_dict["_total_time"] += current_time - callback_dict["_prev_time"]
        # Set the previous time to the current time
        callback_dict["_prev_time"] = current_time
        # Compute the average time per iteration and round it
        time_str = (
            round(callback_dict["_total_time"] / (callback_dict["iters"] - 1), 2)
            if callback_dict["_total_time"]
            else "-"
        )
        # Print to screen on single line
        print(
            "Iters. done: {} [Avg. time per iter: {}]".format(
                callback_dict["iters"], time_str
            ),
            end="\r",
            flush=True,
        )

    return callback


def cost_func(params, ansatz, hamiltonian, estimator):
    """Return estimate of energy from estimator

    Parameters:
        params (ndarray): Array of ansatz parameters
        ansatz (QuantumCircuit): Parameterized ansatz circuit
        hamiltonian (SparsePauliOp): Operator representation of Hamiltonian
        estimator (Estimator): Estimator primitive instance

    Returns:
        float: Energy estimate
    """
    energy = (
        estimator.run([(ansatz, hamiltonian, params)]).result()[0].data.evs
    )
    return energy


def run_vqe(initial_parameters, ansatz, operator, estimator, method):
    callback_dict = {
        "prev_vector": None,
        "iters": 0,
        "cost_history": [],
        "_total_time": 0,
        "_prev_time": None,
    }
    callback = build_callback(ansatz, operator, estimator, callback_dict)
    result = minimize(
        cost_func,
        initial_parameters,
        args=(ansatz, operator, estimator),
        method=method,
        callback=callback,
    )
    return result, callback_dict


if __name__ == "__main__":
    # Model Hamiltonian as a sum of Pauli strings on 2 qubits.
    hamiltonian = SparsePauliOp.from_list([
        ("YZ", 0.3980),
        ("ZI", -0.3980),
        ("ZZ", -0.0113),
        ("XX", 0.1810),
    ])

    # Classical reference: the exact ground state energy via direct
    # diagonalization. Possible here because n = 2, but exponentially hard
    # in general — this is the whole reason VQE exists.
    exact_ground_energy = float(np.linalg.eigvalsh(hamiltonian.to_matrix())[0])

    # Variational ansatz: EfficientSU2 with default reps=3
    ansatz = EfficientSU2(hamiltonian.num_qubits)
    num_parameters = ansatz.num_parameters

    backend = AerSimulator()
    rng = np.random.default_rng(seed=42)  # seeded for reproducible runs
    initial_parameters = 2 * np.pi * rng.random(num_parameters)

    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    ansatz_isa = pm.run(ansatz)
    operator_isa = hamiltonian.apply_layout(ansatz_isa.layout)
    estimator = Estimator(backend)

    print("Variational Quantum Eigensolver — finding the ground-state energy\n")
    print(f"  Hamiltonian:   {hamiltonian}")
    print(f"  Qubits:        {hamiltonian.num_qubits}")
    print(f"  Ansatz:        EfficientSU2 (reps=3, {num_parameters} parameters)")
    print(f"  Optimizer:     COBYLA")
    print(f"  Exact ground:  {exact_ground_energy:.6f}  (classical diagonalization)\n")
    print("Running optimization...")

    vqe_result, callback_dict = run_vqe(
        initial_parameters=initial_parameters,
        ansatz=ansatz_isa,
        operator=operator_isa,
        estimator=estimator,
        method="COBYLA",
    )
    print()  # move past the callback's \r line

    # Extract the energy at each tracked iteration (callback stores PubResults).
    cost_history = [float(pub.data.evs) for pub in callback_dict["cost_history"]]
    total_iters = len(cost_history)

    # Show convergence at a few checkpoints: start, quarter, half, three-quarter, end.
    checkpoints = sorted({0, total_iters // 4, total_iters // 2,
                          3 * total_iters // 4, total_iters - 1})

    print(f"\nConvergence (over {total_iters} iterations):")
    print(f"  {'iter':<6}{'energy':<14}{'|E - E_exact|':<14}")
    print(f"  {'-' * 32}")
    for i in checkpoints:
        energy = cost_history[i]
        err = abs(energy - exact_ground_energy)
        print(f"  {i:<6}{energy:<14.6f}{err:<14.6f}")
    print(f"  {'-' * 32}")

    print(f"\nVQE ground-state estimate: {float(vqe_result.fun):.6f}")
    print(f"Exact ground state:        {exact_ground_energy:.6f}")
    print(f"Absolute error:            {abs(float(vqe_result.fun) - exact_ground_energy):.6f}")
