import math
from typing import List, Tuple, Optional, Set, Dict
from models.aircraft import Aircraft, AircraftValidationError
from models.conflict import ConflictPair, ThresholdConfig
from algorithms.closest_approach import calculate_closest_approach
from algorithms.state_tracer import AlgorithmStep, ExecutionTracer


def validate_aircraft_dataset(aircraft_list: List[Aircraft]) -> None:
    """Validates the entire aircraft dataset for uniqueness and consistency."""
    if not isinstance(aircraft_list, list):
        raise AircraftValidationError("Aircraft dataset must be a list.")
    
    seen_ids: Set[str] = set()
    for ac in aircraft_list:
        if not isinstance(ac, Aircraft):
            raise AircraftValidationError(f"Expected Aircraft instance, got {type(ac)}.")
        ac.validate()
        if ac.id in seen_ids:
            raise AircraftValidationError(f"Duplicate aircraft ID detected: '{ac.id}'. Aircraft IDs must be unique.")
        seen_ids.add(ac.id)


def detect_conflicts_divide_and_conquer(
    aircraft_list: List[Aircraft],
    config: ThresholdConfig,
    record_steps: bool = False
) -> Tuple[List[ConflictPair], int, Optional[ExecutionTracer]]:
    """Spatial Divide and Conquer Collision Threat Detector.
    
    Algorithm Overview:
        1. Validate aircraft data (unique IDs, finite coordinates, non-negative altitude).
        2. Sort aircraft by X coordinate: O(n log n).
        3. Recursive Divide:
           - Base case: If size <= 3, directly evaluate all candidate pairs.
           - Split at median X index: P_left, P_right at dividing line x_mid.
           - Concurrently/recursively analyze left and right subregions.
        4. Combine Step:
           - Identify aircraft whose projected X-trajectories and threat buffers
             can reach or cross the dividing line x_mid.
           - Strip_L contains left aircraft reaching rightwards across x_mid.
           - Strip_R contains right aircraft reaching leftwards across x_mid.
           - Prune candidates using 1D vertical altitude threshold and Y-trajectory reach.
           - Evaluate kinematic closest approach for all surviving candidate pairs.
        5. Deduplicate and rank all conflict pairs by threat severity and proximity.
    
    Returns:
        (conflicts, total_comparisons, tracer)
    """
    validate_aircraft_dataset(aircraft_list)
    
    tracer = ExecutionTracer() if record_steps else None
    
    if len(aircraft_list) < 2:
        if tracer:
            tracer.add_step(AlgorithmStep(
                step_number=1,
                phase="COMPLETE",
                description=f"Analysis complete: {len(aircraft_list)} aircraft provided. At least 2 required for pairwise conflict analysis.",
                depth=0,
                active_aircraft_ids=[ac.id for ac in aircraft_list],
                comparisons_count=0,
                candidate_pairs_evaluated=0,
                conflicts_found_so_far=[]
            ))
        return [], 0, tracer

    # Global tracking during recursion
    step_counter = [0]
    comparison_counter = [0]
    evaluated_pairs_counter = [0]
    discovered_conflicts: Dict[Tuple[str, str], ConflictPair] = {}

    def get_current_conflicts_list() -> List[ConflictPair]:
        clist = list(discovered_conflicts.values())
        clist.sort(key=lambda c: (
            c.threat_level.rank,
            c.time_to_closest_approach,
            c.horizontal_separation
        ))
        return clist

    # Step 1: Sort aircraft by X coordinate
    sorted_aircraft = sorted(aircraft_list, key=lambda a: a.x)
    
    if tracer:
        step_counter[0] += 1
        tracer.add_step(AlgorithmStep(
            step_number=step_counter[0],
            phase="SORT",
            description=f"Step {step_counter[0]}: Initialized and sorted {len(sorted_aircraft)} aircraft along primary spatial X-axis.",
            depth=0,
            active_aircraft_ids=[a.id for a in sorted_aircraft],
            region_bounds=(
                min(a.x for a in sorted_aircraft),
                max(a.x for a in sorted_aircraft),
                min(a.y for a in sorted_aircraft),
                max(a.y for a in sorted_aircraft)
            ),
            comparisons_count=0,
            candidate_pairs_evaluated=0,
            conflicts_found_so_far=[]
        ))

    def evaluate_pair_internal(ac_a: Aircraft, ac_b: Aircraft, depth: int, phase: str, div_x: Optional[float] = None, strip: Optional[Tuple[float, float]] = None):
        evaluated_pairs_counter[0] += 1
        comparison_counter[0] += 1
        
        pair_conflict = calculate_closest_approach(ac_a, ac_b, config)
        threat_str = "SAFE"
        if pair_conflict is not None:
            discovered_conflicts[pair_conflict.pair_key] = pair_conflict
            threat_str = pair_conflict.threat_level.value

        if tracer:
            step_counter[0] += 1
            desc = (f"Evaluating pair ({ac_a.id}, {ac_b.id}) [Phase: {phase}]: "
                    f"Result={threat_str}")
            if pair_conflict:
                desc += f" (Min Horiz={pair_conflict.horizontal_separation*1000:.0f}m at t={pair_conflict.time_to_closest_approach:.1f}s)"
            
            tracer.add_step(AlgorithmStep(
                step_number=step_counter[0],
                phase="EVALUATE_PAIR",
                description=desc,
                depth=depth,
                active_aircraft_ids=[ac_a.id, ac_b.id],
                dividing_line_x=div_x,
                strip_bounds=strip,
                current_pair=(ac_a.id, ac_b.id),
                comparisons_count=comparison_counter[0],
                candidate_pairs_evaluated=evaluated_pairs_counter[0],
                conflicts_found_so_far=get_current_conflicts_list(),
                active_pair_threat=threat_str
            ))

    def recursive_dac(subset: List[Aircraft], depth: int) -> None:
        n = len(subset)
        if n <= 1:
            return

        min_x = min(a.x for a in subset)
        max_x = max(a.x for a in subset)
        min_y = min(a.y for a in subset)
        max_y = max(a.y for a in subset)
        region = (min_x, max_x, min_y, max_y)

        # Base case: n <= 3
        if n <= 3:
            if tracer:
                step_counter[0] += 1
                tracer.add_step(AlgorithmStep(
                    step_number=step_counter[0],
                    phase="BASE_CASE",
                    description=f"Base Case reached at Depth {depth} (|Region| = {n} aircraft: {', '.join(a.id for a in subset)}). Checking direct candidate pairs.",
                    depth=depth,
                    active_aircraft_ids=[a.id for a in subset],
                    region_bounds=region,
                    comparisons_count=comparison_counter[0],
                    candidate_pairs_evaluated=evaluated_pairs_counter[0],
                    conflicts_found_so_far=get_current_conflicts_list()
                ))

            for i in range(n):
                for j in range(i + 1, n):
                    evaluate_pair_internal(subset[i], subset[j], depth, "BASE_CASE")
            return

        # Divide step: split at median index
        mid_idx = n // 2
        # Dividing line X is the midpoint between left-max and right-min
        dividing_x = (subset[mid_idx - 1].x + subset[mid_idx].x) / 2.0
        left_sub = subset[:mid_idx]
        right_sub = subset[mid_idx:]

        if tracer:
            step_counter[0] += 1
            tracer.add_step(AlgorithmStep(
                step_number=step_counter[0],
                phase="DIVIDE",
                description=f"Divide Step at Depth {depth}: Bisecting {n} aircraft into Left ({len(left_sub)}) and Right ({len(right_sub)}) at X = {dividing_x:.2f} km.",
                depth=depth,
                active_aircraft_ids=[a.id for a in subset],
                dividing_line_x=dividing_x,
                region_bounds=region,
                comparisons_count=comparison_counter[0],
                candidate_pairs_evaluated=evaluated_pairs_counter[0],
                conflicts_found_so_far=get_current_conflicts_list()
            ))

        # Conquer: Recurse on Left
        if tracer:
            step_counter[0] += 1
            tracer.add_step(AlgorithmStep(
                step_number=step_counter[0],
                phase="RECURSE_LEFT",
                description=f"Recursing on Left sub-space ({len(left_sub)} aircraft) at Depth {depth + 1}.",
                depth=depth + 1,
                active_aircraft_ids=[a.id for a in left_sub],
                dividing_line_x=dividing_x,
                region_bounds=(min(a.x for a in left_sub), max(a.x for a in left_sub),
                               min(a.y for a in left_sub), max(a.y for a in left_sub)),
                comparisons_count=comparison_counter[0],
                candidate_pairs_evaluated=evaluated_pairs_counter[0],
                conflicts_found_so_far=get_current_conflicts_list()
            ))
        recursive_dac(left_sub, depth + 1)

        # Conquer: Recurse on Right
        if tracer:
            step_counter[0] += 1
            tracer.add_step(AlgorithmStep(
                step_number=step_counter[0],
                phase="RECURSE_RIGHT",
                description=f"Recursing on Right sub-space ({len(right_sub)} aircraft) at Depth {depth + 1}.",
                depth=depth + 1,
                active_aircraft_ids=[a.id for a in right_sub],
                dividing_line_x=dividing_x,
                region_bounds=(min(a.x for a in right_sub), max(a.x for a in right_sub),
                               min(a.y for a in right_sub), max(a.y for a in right_sub)),
                comparisons_count=comparison_counter[0],
                candidate_pairs_evaluated=evaluated_pairs_counter[0],
                conflicts_found_so_far=get_current_conflicts_list()
            ))
        recursive_dac(right_sub, depth + 1)

        # Combine Step: Cross-boundary Candidate Pair Analysis
        horizon = max(0.0, config.prediction_horizon)
        d_max = config.max_conflict_distance
        h_max = config.low_vert

        # Compute the spatial reach envelope along X for left and right partitions
        # Left reach envelope: minimum and maximum X any left aircraft can reach during [0, horizon]
        left_reach_min = min(min(ac.x, ac.x + ac.vx * horizon) for ac in left_sub)
        left_reach_max = max(max(ac.x, ac.x + ac.vx * horizon) for ac in left_sub)
        
        # Right reach envelope: minimum and maximum X any right aircraft can reach during [0, horizon]
        right_reach_min = min(min(ac.x, ac.x + ac.vx * horizon) for ac in right_sub)
        right_reach_max = max(max(ac.x, ac.x + ac.vx * horizon) for ac in right_sub)

        # Candidate aircraft from Left: can reach within d_max of Right partition's reach
        strip_left: List[Aircraft] = []
        for ac in left_sub:
            ac_x_max = max(ac.x, ac.x + ac.vx * horizon)
            if ac_x_max + d_max >= right_reach_min:
                strip_left.append(ac)

        # Candidate aircraft from Right: can reach within d_max of Left partition's reach
        strip_right: List[Aircraft] = []
        for ac in right_sub:
            ac_x_min = min(ac.x, ac.x + ac.vx * horizon)
            if ac_x_min - d_max <= left_reach_max:
                strip_right.append(ac)

        # Compute dynamic strip bounds for visual highlighting
        strip_min_x = min([ac.x for ac in strip_left], default=dividing_x - d_max)
        strip_max_x = max([ac.x for ac in strip_right], default=dividing_x + d_max)
        strip_bounds = (min(strip_min_x, dividing_x - 1.0), max(strip_max_x, dividing_x + 1.0))

        if tracer:
            step_counter[0] += 1
            tracer.add_step(AlgorithmStep(
                step_number=step_counter[0],
                phase="STRIP_CHECK",
                description=(f"Combine Step at Depth {depth}: Checking boundary strip around X = {dividing_x:.2f} km. "
                             f"Candidates: {len(strip_left)} Left aircraft, {len(strip_right)} Right aircraft."),
                depth=depth,
                active_aircraft_ids=[a.id for a in strip_left + strip_right],
                dividing_line_x=dividing_x,
                strip_bounds=strip_bounds,
                region_bounds=region,
                comparisons_count=comparison_counter[0],
                candidate_pairs_evaluated=evaluated_pairs_counter[0],
                conflicts_found_so_far=get_current_conflicts_list()
            ))

        # Check candidate pairs across strip
        for ac_l in strip_left:
            # Calculate Y-extent for ac_l
            y_l_min = min(ac_l.y, ac_l.y + ac_l.vy * horizon) - d_max
            y_l_max = max(ac_l.y, ac_l.y + ac_l.vy * horizon) + d_max

            for ac_r in strip_right:
                # 1. Vertical altitude filter (prunes impossible conflicts without trig)
                if abs(ac_l.altitude - ac_r.altitude) > h_max:
                    continue

                # 2. Horizontal Y-reach overlap filter
                y_r_min = min(ac_r.y, ac_r.y + ac_r.vy * horizon) - d_max
                y_r_max = max(ac_r.y, ac_r.y + ac_r.vy * horizon) + d_max

                if y_l_max < y_r_min or y_r_max < y_l_min:
                    # Y envelopes do not overlap within horizon + safety buffer
                    continue

                # Surviving cross-boundary candidate pair
                evaluate_pair_internal(ac_l, ac_r, depth, "COMBINE_STRIP", dividing_x, strip_bounds)

    # Launch recursive Divide & Conquer
    recursive_dac(sorted_aircraft, depth=0)

    final_conflicts = get_current_conflicts_list()

    if tracer:
        step_counter[0] += 1
        tracer.add_step(AlgorithmStep(
            step_number=step_counter[0],
            phase="COMPLETE",
            description=(f"Execution Complete: {len(sorted_aircraft)} aircraft evaluated. "
                         f"Found {len(final_conflicts)} potential conflict(s) with {comparison_counter[0]} pairwise comparisons."),
            depth=0,
            active_aircraft_ids=[a.id for a in sorted_aircraft],
            comparisons_count=comparison_counter[0],
            candidate_pairs_evaluated=evaluated_pairs_counter[0],
            conflicts_found_so_far=final_conflicts
        ))
        tracer.to_start()

    return final_conflicts, comparison_counter[0], tracer
