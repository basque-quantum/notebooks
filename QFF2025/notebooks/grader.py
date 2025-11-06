from battleship_functions import play_battleship, get_probabilities
from qiskit_aer import AerSimulator

def count_planned_checks(strategy_fn, n: int, cap: int | None = None) -> int:
    """
    Ask the strategy for checks until it says 'I'm done' (returns []).
    We feed it a dummy history so strategies will just list their whole plan.
    Args:
        strategy_fn : Function defining the strategy plan
        n (int) : Size of the grid
        cap (int): Hard stop so we don't loop forever if someone writes a weird strategy.
    Returns:
        int : Number of checks in the plan
    
    """
    if cap is None:
        cap = 4 * n
    history = []
    steps = 0
    for _ in range(cap):
        check_coords = strategy_fn(n, history)
        if not check_coords:
            break
        steps += 1
        # history so the strategy knows we've "used" this check
        history.append({"check_coords": check_coords})
    return steps


def all_placements(n: int) -> list[list[str]]:
    """
    Generates all possible placements of a size-two horizontal ship
    in a n x n battleship grid
    Args:
        n (int) : Size of the grid
    Returns:
        list[list[str]]: List contatining all the possible ship placements
        as combination of coordinates in the grid.
    
    """
    placements = []
    for row in range(1, n + 1):
        for col in range(n - 1):
            col1 = chr(ord('A') + col)
            col2 = chr(ord('A') + col + 1)
            placements.append([f"{col1}{row}", f"{col2}{row}"])
    return placements


def run_one_check(n, ship_coords, check_coords) -> tuple[bool, float, dict[str, int]]:
    """
    Place a battleship game where a ship is placed at `ship_coords` and
    the coordinates in `check_coords` are checked. 
    Args:
        n (int) : Size of the grid
        ship_coords (list) : List containing the coordinates of the grid
        where the ship is placed
        check_coords (list) : List containing the coordinates of the grid
        where the checks are placed
    Returns:
        tuple(bool, float, dict) : Whether a ship was hit or not, the success 
        rate of the check and the resulting counts (merged under mapping)
    
    """
    threshold = 0.4 # kinda worst case performance of the interferometer
    backend = AerSimulator()

    _, grouped_counts = play_battleship(n, ship_coords, check_coords, backend)
    probabilities = get_probabilities(grouped_counts)

    try:
        success_rate = (
            probabilities['Ship detected (no BOOM!)'] /
            probabilities['BOOM!']
        )
    except:
        success_rate = 0

    hit = success_rate >= threshold
    return hit, success_rate, grouped_counts


def grade_strategy(strategy_fn, n: int) -> dict[str, int]:
    """
    Evaluates whether a strategy with a set of checks can work for any
    possible size-2 horizontal ship placement in an n x n grid.
    Args:
        strategy_fn : Function defining the strategy plan
        n (int) : Size of the grid
    Returns:
        dict[str, int] : Information about the success or failure of the 
        strategy
    
    """
    planned_checks = count_planned_checks(strategy_fn, n, cap=4*n)
    max_steps = planned_checks

    all_ships = all_placements(n)

    worst_confidence = 1.0

    for true_ship in all_ships:
        candidates = [tuple(s) for s in all_ships]
        history = []
        solved = False

        for step in range(1, max_steps + 1):
            check_coords = strategy_fn(n, history)
            if not check_coords:
                break

            hit, confidence, grouped = run_one_check(
                n, true_ship, check_coords
            )

            new_candidates = []
            check_set = set(check_coords)
            for cand in candidates:
                cand_set = set(cand)
                cand_hit = bool(check_set & cand_set)
                if cand_hit == hit:
                    new_candidates.append(cand)

            if new_candidates:
                candidates = new_candidates

            history.append({
                "step": step,
                "ship": true_ship,
                "check_coords": check_coords,
                "hit": hit,
                "confidence": confidence,
                "grouped": grouped,
                "remaining_candidates": candidates,
            })

            if len(candidates) == 1:
                solved = True
                if confidence != 0:
                    worst_confidence = min(worst_confidence, confidence)
                break

        if not solved:
            # strategy failed for THIS ship — return just this one last ship
            return {
                "Did the strategy work?": False,
                "Why?": "Could not uniquely identify a ship",
                "Failed ship": true_ship,
                # "failing_history": history,  # can be output for debugging
                "Number of quantum checks": planned_checks,
            }

    # strategy worked for ALL ships
    classical_cost = n * n
    quantum_cost = planned_checks
    P = worst_confidence

    enhancement = (classical_cost / quantum_cost) * P

    return {
        "Did the strategy work?": True,
        "Enhancement score": enhancement,
        "Number of quantum checks": planned_checks,
        "Minimum success rate": worst_confidence,
    }