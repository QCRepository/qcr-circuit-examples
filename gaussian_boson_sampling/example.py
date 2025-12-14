"""Example of the Gaussian Boson Sampling scheme proposed by Craig S. Hamilton et al. using Piquasso.

For more details on Gaussian Boson Sampling, see:
- Gaussian Boson Sampling (original publication): https://doi.org/10.1103/PhysRevLett.119.170501
- Piquasso Documentation page: https://piquasso.readthedocs.io/en/latest/tutorials/gaussian-boson-sampling.html
"""

import piquasso as pq
import numpy as np
from scipy.stats import unitary_group

def gaussian_boson_sampling_program(num_modes, squeezings, interferometer_matrix):
    """Construct a Gaussian Boson Sampling quantum program using a given squeezing and interferometer matrix.

    Args:
        num_modes (int): The number of modes for the Gaussian Boson Sampling circuit
        squeezings (list): The squeezing parameters for the Gaussian Boson Sampling circuit
        interferometer_matrix (ndarray): Unitary matrix representing the interferometer transformation

    Returns:
        pq.Program: A Piquasso quantum program for Gaussian Boson Sampling
    """
    with pq.Program() as program:
        for i in range(num_modes):
            pq.Q(i) | pq.Squeezing(squeezings[i])

        pq.Q() | pq.Interferometer(interferometer_matrix)
        pq.Q() | pq.ParticleNumberMeasurement()
    return program

# Example parameters
num_modes = 7
num_shots = 100

# Define squeezing parameters for the modes
# Here, we use 0.25 squeezing for the first five modes and no squeezing for the rest
squeezings = np.concatenate([0.25 * np.ones(5), np.zeros(5)])

# Generate a random example matrix for the interferometer from the unitary group
interferometer_matrix = unitary_group.rvs(num_modes)

program = gaussian_boson_sampling_program(num_modes, squeezings, interferometer_matrix)

simulator = pq.GaussianSimulator(d=num_modes)
result = simulator.execute(program, shots=num_shots)
print(result.samples)