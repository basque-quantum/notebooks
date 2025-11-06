def group_counts(counts : dict) -> dict:
    """
    Groups counts depending on the bitstring. The input bit strings are assumed to be of the form 
    `d[0] c[0]c[1]...c[n-1]`,where `c`  and `d` are `ClassicalRegisters`.

    The grouped dictionary has three keys:
        - `BOOM!` : Corresponds to the cummulative counts of all bitstrings
                    that contain a 1 in any bit in `c`.
        - `Ship detected (no BOOM!)` : Corresponds to the counts associated to
                    the bitstring `1 00...0`(i.e., all zeros in the `c` register
                    and a one in `d`).
        - `?`: Corresponds to the counts associated to the bitstring `0 00...0` (zeros
                accross all bits in both registers).

    Args:
        counts (dict): The original dictionary.

    Returns:
        dict: The remapped counts dictionary.
    """

    remapped_counts = {
        'Ship detected (no BOOM!)': 0,
        'BOOM!': 0,
        '?': 0
    }

    for bitstring, count in counts.items():
        d_register, c_register = bitstring.split(' ')

        if '1' in c_register:
            remapped_counts['BOOM!'] += count
            continue

        if c_register.count('0') == len(c_register):
            if d_register == '0':
                remapped_counts['?'] += count
                continue

            elif d_register == '1':
                remapped_counts['Ship detected (no BOOM!)'] += count
                continue

    return {k: v for k, v in remapped_counts.items() if v > 0}
