from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from models.conflict import ConflictPair


@dataclass
class AlgorithmStep:
    """Represents a single granular state snapshot of the Divide and Conquer execution."""
    step_number: int
    phase: str  # 'SORT', 'DIVIDE', 'RECURSE_LEFT', 'RECURSE_RIGHT', 'BASE_CASE', 'STRIP_CHECK', 'EVALUATE_PAIR', 'COMPLETE'
    description: str
    depth: int
    active_aircraft_ids: List[str]
    dividing_line_x: Optional[float] = None
    strip_bounds: Optional[Tuple[float, float]] = None  # (strip_min_x, strip_max_x)
    current_pair: Optional[Tuple[str, str]] = None     # Pair currently being evaluated
    region_bounds: Optional[Tuple[float, float, float, float]] = None  # (min_x, max_x, min_y, max_y)
    comparisons_count: int = 0
    candidate_pairs_evaluated: int = 0
    conflicts_found_so_far: List[ConflictPair] = field(default_factory=list)
    active_pair_threat: Optional[str] = None  # 'HIGH', 'MEDIUM', 'LOW', or 'SAFE'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "phase": self.phase,
            "description": self.description,
            "depth": self.depth,
            "active_aircraft_count": len(self.active_aircraft_ids),
            "dividing_line_x": round(self.dividing_line_x, 2) if self.dividing_line_x is not None else None,
            "strip_bounds": (round(self.strip_bounds[0], 2), round(self.strip_bounds[1], 2)) if self.strip_bounds else None,
            "current_pair": self.current_pair,
            "comparisons_count": self.comparisons_count,
            "conflicts_count": len(self.conflicts_found_so_far),
        }


class ExecutionTracer:
    """Records and manages algorithm step history for interactive replay."""
    def __init__(self):
        self.steps: List[AlgorithmStep] = []
        self.current_step_index: int = -1

    def add_step(self, step: AlgorithmStep) -> None:
        self.steps.append(step)

    def clear(self) -> None:
        self.steps.clear()
        self.current_step_index = -1

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    @property
    def current_step(self) -> Optional[AlgorithmStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def seek(self, index: int) -> Optional[AlgorithmStep]:
        if not self.steps:
            return None
        self.current_step_index = max(0, min(index, len(self.steps) - 1))
        return self.steps[self.current_step_index]

    def next(self) -> Optional[AlgorithmStep]:
        if not self.steps:
            return None
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
        return self.steps[self.current_step_index]

    def prev(self) -> Optional[AlgorithmStep]:
        if not self.steps:
            return None
        if self.current_step_index > 0:
            self.current_step_index -= 1
        return self.steps[self.current_step_index]

    def to_start(self) -> Optional[AlgorithmStep]:
        return self.seek(0)

    def to_end(self) -> Optional[AlgorithmStep]:
        if not self.steps:
            return None
        return self.seek(len(self.steps) - 1)
