from typing import List, Tuple
from models.aircraft import Aircraft
from models.conflict import ConflictPair, ThresholdConfig
from algorithms.closest_approach import calculate_closest_approach


def detect_conflicts_brute_force(
    aircraft_list: List[Aircraft],
    config: ThresholdConfig
) -> Tuple[List[ConflictPair], int]:
    """Exhaustive O(n^2) reference algorithm for collision threat detection.
    
    Used strictly for unit-testing correctness, baseline comparisons,
    and ground-truth verification of the Divide and Conquer algorithm.
    
    Returns:
        (conflicts, comparisons_count)
    """
    n = len(aircraft_list)
    conflicts: List[ConflictPair] = []
    comparisons = 0
    seen_pairs = set()

    for i in range(n):
        for j in range(i + 1, n):
            comparisons += 1
            ac_a = aircraft_list[i]
            ac_b = aircraft_list[j]
            pair = calculate_closest_approach(ac_a, ac_b, config)
            if pair is not None:
                key = pair.pair_key
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    conflicts.append(pair)

    # Rank by threat severity (HIGH first, then MEDIUM, then LOW),
    # then by earliest time of closest approach, then minimum horizontal separation
    conflicts.sort(key=lambda c: (
        c.threat_level.rank,
        c.time_to_closest_approach,
        c.horizontal_separation
    ))

    return conflicts, comparisons
