# # Quantum Amplitude Estimation
# 
# Given an operator $\mathcal{A}$ that acts as
# 
# $$
#     \mathcal{A}|0\rangle = \sqrt{1 - a}|\Psi_0\rangle + \sqrt{a}|\Psi_1\rangle
# $$
# 
# Quantum Amplitude Estimation (QAE) is the task of finding an estimate for the amplitude $a$ of the state $|\Psi_1\rangle$:
# 
# $$
#     a = |\langle\Psi_1 | \Psi_1\rangle|^2.
# $$
# 
# This task has first been investigated by Brassard et al. [1] in 2000 and their algorithm uses a combination of the Grover operator 
# 
# $$
#     \mathcal{Q} = \mathcal{A}\mathcal{S}_0\mathcal{A}^\dagger\mathcal{S}_{\Psi_1}
# $$
# 
# where $\mathcal{S}_0$ and $\mathcal{S}_{\Psi_1}$ are reflections about the $|0\rangle$ and $|\Psi_1\rangle$ states, respectively, and phase estimation. However this algorithm, called [AmplitudeEstimation](https://qiskit-community.github.io/qiskit-algorithms/stubs/qiskit_algorithms.AmplitudeEstimation.html) in [Qiskit Algorithms](https://qiskit-community.github.io/qiskit-algorithms/), requires large circuits and is computationally expensive. Therefore, other variants of QAE have been proposed, which we will showcase in this tutorial for a simple example.
# 
# In our example, $\mathcal{A}$ describes a Bernoulli random variable with (assumed to be unknown) success probability $p$:
# 
# $$
#     \mathcal{A}|0\rangle = \sqrt{1 - p}|0\rangle + \sqrt{p}|1\rangle.
# $$
# 
# On a quantum computer, we can model this operator with a rotation around the $Y$-axis of a single qubit
# 
# $$
# \mathcal{A} = R_Y(\theta_p), \theta_p = 2\sin^{-1}(\sqrt{p}).
# $$
# 
# The Grover operator for this case is particularly simple
# 
# $$
# \mathcal{Q} = R_Y(2\theta_p),
# $$
# 
# whose powers are very easy to calculate: $\mathcal{Q}^k = R_Y(2k\theta_p)$.

# We'll fix the probability we want to estimate to $p = 0.2$.


p = 0.2


# Now we can define circuits for $\mathcal{A}$ and $\mathcal{Q}$. 



import numpy as np
from qiskit.circuit import QuantumCircuit


class BernoulliA(QuantumCircuit):
    """A circuit representing the Bernoulli A operator."""

    def __init__(self, probability):
        super().__init__(1)  # circuit on 1 qubit

        theta_p = 2 * np.arcsin(np.sqrt(probability))
        self.ry(theta_p, 0)


class BernoulliQ(QuantumCircuit):
    """A circuit representing the Bernoulli Q operator."""

    def __init__(self, probability):
        super().__init__(1)  # circuit on 1 qubit

        self._theta_p = 2 * np.arcsin(np.sqrt(probability))
        self.ry(2 * self._theta_p, 0)

    def power(self, k):
        # implement the efficient power of Q
        q_k = QuantumCircuit(1)
        q_k.ry(2 * k * self._theta_p, 0)
        return q_k




A = BernoulliA(p)
Q = BernoulliQ(p)


# ### Amplitude Estimation workflow

# Qiskit Algorithms implements several QAE algorithms that all derive from the [AmplitudeEstimator](https://qiskit-community.github.io/qiskit-algorithms/stubs/qiskit_algorithms.AmplitudeEstimator.html) interface. In the initializer we specify algorithm specific settings and the `estimate` method, which does all the work, takes an [EstimationProblem](https://qiskit-community.github.io/qiskit-algorithms/stubs/qiskit_algorithms.EstimationProblem.html) as input and returns an [AmplitudeEstimationResult](https://qiskit-community.github.io/qiskit-algorithms/stubs/qiskit_algorithms.AmplitudeEstimatorResult.html) object. Since all QAE variants follow the same interface, we can use them all to solve the same problem instance. 
# 
# Next, we'll run all different QAE algorithms. To do so, we first define the estimation problem which will contain the $\mathcal{A}$ and $\mathcal{Q}$ operators as well as how to identify the $|\Psi_1\rangle$ state, which in this simple example is just $|1\rangle$.



from estimation_problem import EstimationProblem

problem = EstimationProblem(
    state_preparation=A,  # A operator
    grover_operator=Q,  # Q operator
    objective_qubits=[0],  # the "good" state Psi1 is identified as measuring |1> in qubit 0
)


# To execute circuits we'll use `Sampler`.


from qiskit.primitives import Sampler

sampler = Sampler()


# ### Canonical AE
# 
# Now let's solve this with the original QAE implementation by Brassard et al. [1].


from amplitude_estimation_class import AmplitudeEstimation

ae = AmplitudeEstimation(
    num_eval_qubits=3,  # the number of evaluation qubits specifies circuit width and accuracy
    sampler=sampler,
)


# With the algorithm defined, we can call the `estimate` method and provide it with the problem to solve.


ae_result = ae.estimate(problem)


# The estimate is available in the `estimation` key:


print(ae_result.estimation)


# We see that this is not a very good estimate for our target of $p=0.2$! That's due to the fact the canonical AE is restricted to a discrete grid, specified by the number of evaluation qubits:


# Note: uncomment the following lines to plot the estimated values
# ----------------------------------------------------------------
#
# import matplotlib.pyplot as plt
# 
# # plot estimated values
# gridpoints = list(ae_result.samples.keys())
# probabilities = list(ae_result.samples.values())
# 
# plt.bar(gridpoints, probabilities, width=0.5 / len(probabilities))
# plt.axvline(p, color="r", ls="--")
# plt.xticks(size=15)
# plt.yticks([0, 0.25, 0.5, 0.75, 1], size=15)
# plt.title("Estimated Values", size=15)
# plt.ylabel("Probability", size=15)
# plt.xlabel(r"Amplitude $a$", size=15)
# plt.ylim((0, 1))
# plt.grid()
# plt.show()


# To improve the estimate we can interpolate the measurement probabilities and compute the maximum likelihood estimator that produces this probability distribution:


print("Interpolated MLE estimator:", ae_result.mle)


# We can have a look at the circuit that AE executes:

# Note: uncomment the following lines to learn more about the circuit
# -------------------------------------------------------------------
#
# ae_circuit = ae.construct_circuit(problem)
# ae_circuit.decompose().draw(
#     "mpl", style="clifford"
# )  # decompose 1 level: exposes the Phase estimation circuit!
# 
# 
# 
# from qiskit import transpile
# 
# 
# basis_gates = ["h", "ry", "cry", "cx", "ccx", "p", "cp", "x", "s", "sdg", "y", "t", "cz"]
# transpile(ae_circuit, basis_gates=basis_gates, optimization_level=2).draw("mpl", style="clifford")

# ### References
# 
# [1] Quantum Amplitude Amplification and Estimation. Brassard et al (2000). https://arxiv.org/abs/quant-ph/0005055
