from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
import numpy as np
from utils import group_counts

def get_probabilities(counts : dict) -> dict:
    """
    Computes the success probabilities of the different
    outcomes of the experiment
    Args:
        counts (dict): The grouped dictionary.

    Returns:
        dict: The same dictionary but the values have been
            changed to probabilities (from 0 to 100 percent).
    """
    probabilities = {}
    for (key, value) in counts.items():
        probabilities[key] = value/sum(counts.values()) * 100
    return probabilities

def map_labels(n : int) -> tuple[QuantumRegister, dict]:
    """
    Maps the different squares in a nxn (square) grid
    to qubits in the register squares.
    Args:
        n (int): Size of the grid.

    Returns:
        tuple[QuantumRegister, dict]: The `QuantumRegister`
        containing the qubits representing the squares of the grid
        and a `dict` with `keys` refering to coordinates in the grid
        in string format (for example, `'A0'`), and `values` equal to the
        qubit representing that square.
    """
    squares = QuantumRegister(n*n, 'q')
    label_map = {}
    for row in range(1, n + 1):
        for col in range(n):
            col_label = chr(ord('A') + col)  # A, B, C...
            idx = (row - 1) * n + col  # row-major order
            label_map[f"{col_label}{row}"] = squares[idx]

    return squares, label_map

def place_ships(squares : QuantumRegister, label_map : dict, ship_coords : list) -> tuple[QuantumCircuit, ClassicalRegister]:
    """
    Places ships on positions `ship_coords[0]`, `ship_coords[1]`, ...
    Ex. `ship_coords = ['A1']` would place a bomb in `squares[0]`.

    Args:
        squares (QuantumRegister): Register containing the qubits
        representing the squares of the grid.

        label_map (dict): Dictionary containing the mapping of the grid
        into qubits contaned in `squares`.

        ship_coords (list): List containing the coordinates of the grid
        where the player wishes to place a ship (ex. ['A1', 'A2'])

    Returns:
        tuple[QuantumCircuit, ClassicalRegister]: The `QuantumCircuit`
        containing grid with the ships placed and the `ClassicalRegister`
        containing the measurement results of the ships
    """

    creg = ClassicalRegister(len(ship_coords), 'c')
    filled_grid = QuantumCircuit(squares, creg)

    for (idx, position) in enumerate(ship_coords):
        qubit = label_map[position]
        filled_grid.measure(qubit, creg[idx])

    return filled_grid, creg

def place_check(squares : QuantumRegister, label_map : dict, check_coords : list) -> tuple[QuantumCircuit, QuantumCircuit, QuantumRegister, ClassicalRegister]:
    """
    Places "checks" on the squares [check_coords[0], check_coords[1], ...]
    in squares to look out for ships. 

    Args:
        squares (QuantumRegister): Register containing the qubits
        representing the squares of the grid.

        label_map (dict): Dictionary containing the mapping of the grid
        into qubits contaned in `squares`.

        check_coords (list): List containing the coordinates of the grid
        where the player wishes to check for a ship (ex. ['A1', 'A2'])

    Returns:
        tuple[QuantumCircuit, QuantumCircuit, QuantumRegister, ClassicalRegister]: The `QuantumCircuit`
        objects representing both halves of the interferometer, the `QuantumRegister` representing
        the probe qubit and the `ClassicalRegister` storing the result of the detection.
    """

    p_reg = QuantumRegister(1, 'p')
    detect_reg = ClassicalRegister(1, 'd')
    first_half = QuantumCircuit(p_reg, detect_reg, squares)

    probe = p_reg[0]
    
    angle = np.pi/3
  
    first_half.rx(angle, probe)
    for position in check_coords:
        qubit = label_map[position]
        first_half.cx(probe, qubit)
    first_half.rx(-np.pi, probe)

    second_half = first_half.inverse()
    second_half.measure(probe, detect_reg[0])

    return first_half, second_half, p_reg, detect_reg

def play_battleship(n: int, ship_coords : list, check_coords : list, backend):
    """
    Creates an nxn battleship grid, with ships placed in 
    ship_coords[0], ship_coords[1], ... and checks the squares
    check_coords[0], check_coords[1], ... for possible ships. Returns whether or not
    a ship has been found along all checks squares (does not specify).
    """
    
    squares, label_map = map_labels(n)
    filled_grid, creg = place_ships(squares, label_map, ship_coords)
    first_half, second_half, p_reg, detect_reg = place_check(squares, label_map, check_coords)

    qc = QuantumCircuit(p_reg, squares, creg, detect_reg)
    qc.compose(first_half, qubits = [p_reg[0]] +  squares[::], clbits = [detect_reg[0]], inplace = True)
    qc.barrier()
    qc.compose(filled_grid, qubits = squares[::], clbits = creg[::], inplace = True)
    qc.barrier()
    qc.compose(second_half, qubits = [p_reg[0]] + squares[::], clbits = [detect_reg[0]], inplace = True)

    isa_qc = transpile(qc, backend)

    # Run and get counts
    result = backend.run(isa_qc, shots=1_000).result()
    counts = result.get_counts()
    custom_counts = group_counts(counts)

    # if 'Ship detected (no BOOM!)' in custom_counts.keys():
    #     probabilities = get_probabilities(custom_counts)
    #     try:
    #         sucess_rate = probabilities['Ship detected (no BOOM!)']/probabilities['BOOM!'] * 100
    #         print(f'At least one ship detected in positions {check_coords} with a {sucess_rate:.2f}% confidence level')
    #     except:
    #         print(f'Success rate is not well defined for this battleship run. Try again')
    # else:
    #     print(f'No ship detected in positions {check_coords}')

    return qc, custom_counts
