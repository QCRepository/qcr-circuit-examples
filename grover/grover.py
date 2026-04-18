"""
Grover's Algorithm implementation.

Searches an unstructured database of N items in O(sqrt(N)) time,
providing quadratic speedup over classical search.
"""

from argparse import ArgumentParser, Namespace, BooleanOptionalAction
from qiskit import QuantumCircuit as qc
from qiskit import QuantumRegister as qr
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit.result import Counts
from matplotlib.pyplot import show, subplots, xticks, yticks
from math import pi, sqrt, sin, asin
from heapq import nlargest

class GroversAlgorithm:
    def __init__(self,
                 title: str = "Grover's Algorithm",
                 n_qubits: int = 5,
                 search: set[int] = { 11, 9, 0, 3 },
                 shots: int = 1000,
                 fontsize: int = 10,
                 print_circuits: bool = False,
                 combine_states: bool = False) -> None:
        """
        Simulate Grover's algorithm using Qiskit's AerSimulator.

        Args:
            title (str, optional): Window title. Defaults to "Grover's Algorithm".
            n_qubits (int, optional): Number of qubits. Defaults to 5.
            search (set[int], optional): Set of nonnegative integers to search for using Grover's algorithm. Defaults to { 11, 9, 0, 3 }.
            shots (int, optional): Amount of times the algorithm is simulated. Defaults to 1000.
            fontsize (int, optional): Histogram's font size. Defaults to 10.
            print_circuits (bool, optional): Whether or not to print quantum circuit(s). Defaults to False.
            combine_states (bool, optional): Whether to combine all non-winning states into 1 bar labeled "Others" or not. Defaults to False.
        """
        # Parsing command line arguments
        self._parser: ArgumentParser = ArgumentParser(description = "Run grover's algorithm via command line", add_help = False)
        self._init_parser(title, n_qubits, search, shots, fontsize, print_circuits, combine_states)
        self._args: Namespace = self._parser.parse_args()

        # Set of nonnegative ints to search for
        self.search: set[int] = set(self._args.search)

        # Set of m N-qubit binary strings representing target state(s) (i.e. self.search in base 2)
        self._targets: set[str] = { f"{s:0{self._args.n_qubits}b}" for s in self.search }
        
        # N-qubit quantum register
        self._qubits: qr = qr(self._args.n_qubits, "qubit")

    def _print_circuit(self, circuit: qc, name: str) -> None:
        """Print quantum circuit.

        Args:
            circuit (qc): Quantum circuit to print.
            name (str): Quantum circuit's name.
        """
        print(f"\n{name}:\n{circuit}")

    def _oracle(self, targets: set[str]) -> qc:
        """Mark target state(s) with negative phase.

        Args:
            targets (set[str]): N-qubit binary string(s) representing target state(s).

        Returns:
            qc: Quantum circuit representation of oracle.
        """
        # Create N-qubit quantum circuit for oracle
        oracle = qc(self._qubits, name = "Oracle")
        
        for target in targets:
            # Reverse target state since Qiskit uses little-endian for qubit ordering
            target = target[::-1]
            
            # Flip zero qubits in target
            for i in range(self._args.n_qubits):
                if target[i] == "0":
                    # Pauli-X gate
                    oracle.x(i)

            # Simulate (N - 1)-control Z gate
            # 1. Hadamard gate
            oracle.h(self._args.n_qubits - 1)

            # 2. (N - 1)-control Toffoli gate
            oracle.mcx(list(range(self._args.n_qubits - 1)), self._args.n_qubits - 1)

            # 3. Hadamard gate
            oracle.h(self._args.n_qubits - 1)

            # Flip back to original state
            for i in range(self._args.n_qubits):
                if target[i] == "0":
                    # Pauli-X gate
                    oracle.x(i)

        # Display oracle, if applicable
        if self._args.print_circuits: self._print_circuit(oracle, "ORACLE")

        return oracle

    def _diffuser(self) -> qc:
        """Amplify target state(s) amplitude, which decreases the amplitudes of other states
        and increases the probability of getting the correct solution (i.e. target state(s)).

        Returns:
            qc: Quantum circuit representation of diffuser (i.e. Grover's diffusion operator).
        """
        # Create N-qubit quantum circuit for diffuser
        diffuser = qc(self._qubits, name = "Diffuser")

        # Hadamard gate
        diffuser.h(self._qubits)

        # Oracle with all zero target state
        diffuser.append(self._oracle({"0" * self._args.n_qubits}), list(range(self._args.n_qubits)))

        # Hadamard gate
        diffuser.h(self._qubits)
        
        # Display diffuser, if applicable
        if self._args.print_circuits: self._print_circuit(diffuser, "DIFFUSER")

        return diffuser

    def _grover(self) -> qc:
        """Create quantum circuit representation of Grover's algorithm,
        which consists of 4 parts: (1) state preparation/initialization,
        (2) oracle, (3) diffuser, and (4) measurement of resulting state.
        
        Steps 2-3 are repeated an optimal number of times (i.e. Grover's
        iterate) in order to maximize probability of success of Grover's algorithm.

        Returns:
            qc: Quantum circuit representation of Grover's algorithm.
        """
        # Create N-qubit quantum circuit for Grover's algorithm
        grover = qc(self._qubits, name = "Grover Circuit")
        
        # Intialize qubits with Hadamard gate (i.e. uniform superposition)
        grover.h(self._qubits)
        
        # # Apply barrier to separate steps
        grover.barrier()

        # Apply oracle and diffuser (i.e. Grover operator) optimal number of times
        for _ in range(int((pi / 4) * sqrt((2 ** self._args.n_qubits) / len(self._targets)))):
            grover.append(self._oracle(self._targets), list(range(self._args.n_qubits)))
            grover.append(self._diffuser(), list(range(self._args.n_qubits)))
        
        # Measure all qubits once finished
        grover.measure_all()

        # Display grover circuit, if applicable
        if self._args.print_circuits: self._print_circuit(grover, "GROVER CIRCUIT")

        return grover

    def _outcome(self, winners: list[str], counts: Counts) -> None:
        """Print a structured summary of the Grover run.

        Shows the problem setup (qubits, targets, iterations), the theoretical
        vs measured hit rate, and a per-target frequency table, so a reader can
        see at a glance both what the algorithm did and whether it matched
        theory.

        Args:
            winners: Top-frequency bitstrings (unused here; kept for signature
                compatibility with the surrounding plotting code).
            counts: Each measured state mapped to its shot count.
        """
        n = self._args.n_qubits
        N = 2 ** n
        M = len(self._targets)
        shots = self._args.shots

        # Grover iterations: the integer optimum (π/4 · √(N/M))
        optimal_float = (pi / 4) * sqrt(N / M)
        iterations = int(optimal_float)

        # Theoretical success probability after `iterations` rounds
        theta = asin(sqrt(M / N))
        theoretical_rate = sin((2 * iterations + 1) * theta) ** 2

        # Measured success: shots landing on any target state
        target_shots = sum(counts.get(t, 0) for t in self._targets)
        measured_rate = target_shots / shots

        print(f"\nGrover's Search — {n} qubits (N = {N}), {M} targets, {shots} shots\n")
        print(f"  Targets:              {sorted(self.search)}")
        print(f"  Grover iterations:    {iterations}  "
              f"(optimal: floor of π/4 · √(N/M) = {optimal_float:.2f})")
        print(f"  Theoretical hit rate: {theoretical_rate:.1%}")
        print(f"  Measured hit rate:    {measured_rate:.1%}  "
              f"({target_shots} / {shots} shots landed on a target)")

        print("\n  Target states — measurement frequency:")
        for target_str in sorted(self._targets, key=lambda t: int(t, 2)):
            decimal = int(target_str, 2)
            count = counts.get(target_str, 0)
            print(f"    |{target_str}> ({decimal:>3}) {count:>5} / {shots}")
        non_target_shots = shots - target_shots
        print(f"    (non-targets)    {non_target_shots:>5} / {shots}")

        # Sanity check: all top outcomes should be targets when the algorithm
        # is configured optimally.
        if not all(key in self._targets for key in winners):
            print("\n  Note: some top outcomes are NOT targets — iterations may be suboptimal.")

    def _show_histogram(self, histogram_data) -> None:
        """Print outcome and display histogram of simulation results.

        Args:
            data: Each state and its respective frequency.
        """
        # State(s) with highest count and their frequencies
        winners = { winner : histogram_data.get(winner) for winner in nlargest(len(self._targets), histogram_data, key = histogram_data.get) }

        # Print outcome
        self._outcome(list(winners.keys()), histogram_data)

        # X-axis and y-axis value(s) for winners, respectively
        winners_x_axis = [ str(winner) for winner in [*winners] ]
        winners_y_axis = [ *winners.values() ]

        # All other states (i.e. non-winners) and their frequencies
        others = { state : frequency for state, frequency in histogram_data.items() if state not in winners }

        # X-axis and y-axis value(s) for all other states, respectively
        other_states_x_axis = "Others" if self._args.combine else [*others]
        other_states_y_axis = [ sum([*others.values()]) ] if self._args.combine else [ *others.values() ]

        # Create histogram for simulation results
        figure, axes = subplots(num = "Grover's Algorithm — Results", layout = "constrained")
        axes.bar(winners_x_axis, winners_y_axis, color = "green", label = "Target")
        axes.bar(other_states_x_axis, other_states_y_axis, color = "red", label = "Non-target")
        axes.legend(fontsize = self._args.fontsize)
        axes.grid(axis = "y", ls = "dashed")
        axes.set_axisbelow(True)

        # Set histogram title, x-axis title, and y-axis title respectively
        axes.set_title(f"Outcome of {self._args.shots} Simulations", fontsize = int(self._args.fontsize * 1.45))
        axes.set_xlabel("States (Qubits)", fontsize = int(self._args.fontsize * 1.3))
        axes.set_ylabel("Frequency", fontsize = int(self._args.fontsize * 1.3))

        # Set font properties for x-axis and y-axis labels respectively
        xticks(fontsize = self._args.fontsize, family = "monospace", rotation = 0 if self._args.combine else 70)
        yticks(fontsize = self._args.fontsize, family = "monospace")
        
        # Set properties for annotations displaying frequency above each bar
        annotation = axes.annotate("",
                                xy = (0, 0),
                                xytext = (5, 5),
                                xycoords = "data",
                                textcoords = "offset pixels",
                                ha = "center",
                                va = "bottom",
                                family = "monospace",
                                weight = "bold",
                                fontsize = self._args.fontsize,
                                bbox = dict(facecolor = "white", alpha = 0.4, edgecolor = "None", pad = 0)
                                )
        
        def _hover(event) -> None:
            """Display frequency above each bar upon hovering over it.

            Args:
                event: Matplotlib event.
            """
            visibility = annotation.get_visible()
            if event.inaxes == axes:
                for bars in axes.containers:
                    for bar in bars:
                        cont, _ = bar.contains(event)
                        if cont:
                            x, y = bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height()
                            annotation.xy = (x, y)
                            annotation.set_text(y)
                            annotation.set_visible(True)
                            figure.canvas.draw_idle()
                            return
            if visibility:
                annotation.set_visible(False)
                figure.canvas.draw_idle()
            
        # Display histogram
        id = figure.canvas.mpl_connect("motion_notify_event", _hover)
        show()
        figure.canvas.mpl_disconnect(id)

    def run(self) -> None:
        """
        Run Grover's algorithm simulation.
        """
        # Simulate Grover's algorithm locally
        backend = AerSimulator(method = "density_matrix")

        # Generate optimized grover circuit for simulation
        transpiled_circuit = transpile(self._grover(), backend, optimization_level = 2)

        # Run Grover's algorithm simulation 
        job = backend.run(transpiled_circuit, shots = self._args.shots)

        # Get simulation results
        results = job.result()
        
        # Get each state's histogram data (including frequency) from simulation results
        data = results.get_counts()

        # Display simulation results
        self._show_histogram(data)

    def _init_parser(self,
                     title: str,
                     n_qubits: int,
                     search: set[int],
                     shots: int,
                     fontsize: int,
                     print_circuits: bool,
                     combine_states: bool) -> None:
        """
        Helper method to initialize command line argument parser.

        Args:
            title (str): Window title.
            n_qubits (int): Number of qubits.
            search (set[int]): Set of nonnegative integers to search for using Grover's algorithm.
            shots (int): Amount of times the algorithm is simulated.
            fontsize (int): Histogram's font size.
            print_circuits (bool): Whether or not to print quantum circuit(s).
            combine_states (bool): Whether to combine all non-winning states into 1 bar labeled "Others" or not.
        """
        self._parser.add_argument("-H, --help",
                                  action = "help",
                                  help = "show this help message and exit")

        self._parser.add_argument("-T, --title",
                                  type = str,
                                  default = title,
                                  dest = "title",
                                  metavar = "<title>",
                                  help = f"window title (default: \"{title}\")")

        self._parser.add_argument("-n, --n-qubits",
                                  type = int,
                                  default = n_qubits,
                                  dest = "n_qubits",
                                  metavar = "<n_qubits>",
                                  help = f"number of qubits (default: {n_qubits})")

        self._parser.add_argument("-s, --search",
                                  default = search,
                                  type = int,
                                  nargs = "+",
                                  dest = "search",
                                  metavar = "<search>",
                                  help = f"nonnegative integers to search for with Grover's algorithm (default: {search})")

        self._parser.add_argument("-S, --shots",
                                  type = int,
                                  default = shots,
                                  dest = "shots",
                                  metavar = "<shots>",
                                  help = f"amount of times the algorithm is simulated (default: {shots})")

        self._parser.add_argument("-f, --font-size",
                                  type = int,
                                  default = fontsize,
                                  dest = "fontsize",
                                  metavar = "<font_size>",
                                  help = f"histogram's font size (default: {fontsize})")

        self._parser.add_argument("-p, --print",
                                  action = BooleanOptionalAction,
                                  type = bool,
                                  default = print_circuits,
                                  dest = "print_circuits",
                                  help = f"whether or not to print quantum circuit(s) (default: {print_circuits})")

        self._parser.add_argument("-c, --combine",
                                  action = BooleanOptionalAction,
                                  type = bool,
                                  default = combine_states,
                                  dest = "combine",
                                  help = f"whether to combine all non-winning states into 1 bar labeled \"Others\" or not (default: {combine_states})")

if __name__ == "__main__":
    GroversAlgorithm().run()
