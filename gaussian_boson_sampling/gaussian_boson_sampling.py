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

if __name__ == "__main__":
    # Example parameters
    num_modes = 7
    num_shots = 100
    num_squeezed = 5

    # Define squeezing parameters for the modes
    # Here, we use 0.25 squeezing for the first five modes and no squeezing for the rest
    squeezings = np.concatenate([0.25 * np.ones(num_squeezed), np.zeros(num_modes - num_squeezed)])

    # Generate a random example matrix for the interferometer from the unitary group
    interferometer_matrix = unitary_group.rvs(num_modes)

    program = gaussian_boson_sampling_program(num_modes, squeezings, interferometer_matrix)

    simulator = pq.GaussianSimulator(d=num_modes)
    result = simulator.execute(program, shots=num_shots)
    samples = result.samples

    print(f"Gaussian Boson Sampling — {num_modes} modes, {num_shots} shots")
    print(f"Squeezing: r=0.25 on modes 0–{num_squeezed - 1}, vacuum on modes {num_squeezed}–{num_modes - 1}\n")

    # Show first 10 samples
    print("Sample output (photon counts per mode):")
    for i, sample in enumerate(samples[:10]):
        photon_counts = tuple(int(n) for n in sample)
        total = sum(photon_counts)
        print(f"  Shot {i + 1:>3}: {photon_counts}  (total photons: {total})")
    if len(samples) > 10:
        print(f"  ... ({len(samples) - 10} more samples)")

    # Statistics
    photon_totals = [sum(int(n) for n in s) for s in samples]
    vacuum_count = sum(1 for t in photon_totals if t == 0)
    mean_photons = np.mean(photon_totals)

    print(f"\nMean photon number per shot: {mean_photons:.2f}")
    print(f"Vacuum outcomes (0 photons): {vacuum_count}/{num_shots}")
    print(f"Distinct output configurations: {len(set(tuple(int(n) for n in s) for s in samples))}/{num_shots}")
    print(f"\nNote: Unlike standard boson sampling, photon number is NOT conserved in GBS")
    print("(squeezed states have indefinite photon number).")