import math
from typing import List, Optional, Tuple, Dict, Callable
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.patches as patches
import customtkinter as ctk

from models.aircraft import Aircraft
from models.conflict import ConflictPair, ThreatLevel, ThresholdConfig
from algorithms.state_tracer import AlgorithmStep
from ui.theme import (
    RADAR_CANVAS_BG, RADAR_GRID_COLOR, RADAR_RING_COLOR, RADAR_AXIS_COLOR,
    RADAR_CROSSHAIR_COLOR, RADAR_DIVIDE_LINE, RADAR_STRIP_FILL, RADAR_STRIP_LINE,
    COLOR_SAFE, COLOR_LOW, COLOR_MEDIUM, COLOR_HIGH, ACCENT_CYAN, BG_PANEL, BG_CARD
)


class RadarCanvas(ctk.CTkFrame):
    """Interactive Matplotlib-powered Air Traffic Radar Canvas."""
    def __init__(
        self,
        master,
        on_aircraft_selected: Optional[Callable[[Aircraft], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color=BG_PANEL, **kwargs)
        self.on_aircraft_selected = on_aircraft_selected

        self.aircraft_list: List[Aircraft] = []
        self.conflicts: List[ConflictPair] = []
        self.config: ThresholdConfig = ThresholdConfig()
        self.active_step: Optional[AlgorithmStep] = None
        self.selected_aircraft_id: Optional[str] = None
        self.selected_pair: Optional[Tuple[str, str]] = None

        # Build Matplotlib figure
        self.fig = Figure(figsize=(7, 6), dpi=100, facecolor=RADAR_CANVAS_BG)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(RADAR_CANVAS_BG)

        # Remove default matplotlib padding
        self.fig.subplots_adjust(left=0.08, right=0.96, top=0.95, bottom=0.08)

        # Tkinter canvas embed
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Connect click event
        self.canvas.mpl_connect("button_press_event", self._on_canvas_click)

        # Initial render
        self.render()

    def update_data(
        self,
        aircraft_list: List[Aircraft],
        conflicts: List[ConflictPair],
        config: ThresholdConfig,
        active_step: Optional[AlgorithmStep] = None
    ) -> None:
        """Updates radar state and triggers redraw."""
        self.aircraft_list = aircraft_list
        self.conflicts = conflicts
        self.config = config
        self.active_step = active_step
        self.render()

    def set_selected_aircraft(self, aircraft_id: Optional[str]) -> None:
        self.selected_aircraft_id = aircraft_id
        self.render()

    def set_selected_pair(self, pair: Optional[Tuple[str, str]]) -> None:
        self.selected_pair = pair
        self.render()

    def _on_canvas_click(self, event):
        """Detect click near aircraft point."""
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        click_x, click_y = event.xdata, event.ydata
        best_dist = 4.0  # Click tolerance in km
        closest_ac: Optional[Aircraft] = None

        for ac in self.aircraft_list:
            dist = math.hypot(ac.x - click_x, ac.y - click_y)
            if dist < best_dist:
                best_dist = dist
                closest_ac = ac

        if closest_ac:
            self.selected_aircraft_id = closest_ac.id
            if self.on_aircraft_selected:
                self.on_aircraft_selected(closest_ac)
            self.render()

    def render(self) -> None:
        """Draws the radar grid, range rings, aircraft vectors, trajectories,
        threat lines, and Divide and Conquer algorithm execution artifacts.
        """
        self.ax.clear()
        self.ax.set_facecolor(RADAR_CANVAS_BG)

        # Calculate coordinate bounds
        max_coord = 45.0
        if self.aircraft_list:
            horizon = max(0.0, self.config.prediction_horizon)
            all_x = [ac.x for ac in self.aircraft_list] + [ac.x + ac.vx * horizon for ac in self.aircraft_list]
            all_y = [ac.y for ac in self.aircraft_list] + [ac.y + ac.vy * horizon for ac in self.aircraft_list]
            span = max(max(abs(min(all_x)), abs(max(all_x))), max(abs(min(all_y)), abs(max(all_y))))
            max_coord = max(35.0, span * 1.25)

        self.ax.set_xlim(-max_coord, max_coord)
        self.ax.set_ylim(-max_coord, max_coord)
        self.ax.set_aspect("equal", adjustable="box")

        # 1. Concentric Range Rings (Aviation Radar Standard)
        ring_step = 10.0 if max_coord <= 60.0 else 20.0
        r = ring_step
        while r <= max_coord:
            circle = patches.Circle((0, 0), r, fill=False, edgecolor=RADAR_RING_COLOR,
                                    linestyle=":", linewidth=0.8, alpha=0.7)
            self.ax.add_patch(circle)
            self.ax.text(0.5, r + 0.5, f"{int(r)} km", color=RADAR_AXIS_COLOR,
                         fontsize=7, fontfamily="sans-serif", alpha=0.8)
            r += ring_step

        # 2. Crosshair grid lines
        self.ax.axhline(0, color=RADAR_CROSSHAIR_COLOR, linestyle="--", linewidth=0.7, alpha=0.5)
        self.ax.axvline(0, color=RADAR_CROSSHAIR_COLOR, linestyle="--", linewidth=0.7, alpha=0.5)

        # 3. Heading Compass Rose (North Indicator)
        self.ax.annotate("N", xy=(0, max_coord * 0.94), color=ACCENT_CYAN,
                         fontsize=11, fontweight="bold", ha="center", va="center")
        self.ax.annotate("▲", xy=(0, max_coord * 0.98), color=ACCENT_CYAN,
                         fontsize=9, ha="center", va="center")

        # 4. Divide and Conquer Execution Highlights
        if self.active_step:
            step = self.active_step

            # Active Subregion bounding box
            if step.region_bounds:
                rx_min, rx_max, ry_min, ry_max = step.region_bounds
                w = max(0.5, rx_max - rx_min)
                h = max(0.5, ry_max - ry_min)
                region_rect = patches.Rectangle(
                    (rx_min, ry_min), w, h,
                    fill=True, facecolor="#3A86FF", alpha=0.05,
                    edgecolor="#3A86FF", linestyle="--", linewidth=1.0
                )
                self.ax.add_patch(region_rect)

            # Dividing line X
            if step.dividing_line_x is not None:
                self.ax.axvline(
                    step.dividing_line_x,
                    color=RADAR_DIVIDE_LINE,
                    linestyle="-.",
                    linewidth=1.8,
                    alpha=0.9,
                    label="Split Boundary"
                )
                self.ax.text(
                    step.dividing_line_x + 0.8, -max_coord * 0.92,
                    f"SPLIT X = {step.dividing_line_x:.1f} km",
                    color=RADAR_DIVIDE_LINE,
                    fontsize=8,
                    fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=RADAR_CANVAS_BG, edgecolor=RADAR_DIVIDE_LINE, alpha=0.8)
                )

            # Boundary Candidate Strip
            if step.strip_bounds:
                s_min, s_max = step.strip_bounds
                strip_span = patches.Rectangle(
                    (s_min, -max_coord), s_max - s_min, max_coord * 2,
                    fill=True, facecolor="#00E5FF", alpha=0.10,
                    edgecolor=RADAR_STRIP_LINE, linestyle=":", linewidth=1.2
                )
                self.ax.add_patch(strip_span)
                self.ax.text(
                    (s_min + s_max) / 2.0, max_coord * 0.88,
                    "COMBINE STRIP",
                    color=ACCENT_CYAN,
                    fontsize=8,
                    fontweight="bold",
                    ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor=RADAR_CANVAS_BG, edgecolor=ACCENT_CYAN, alpha=0.7)
                )

            # Current Pair Evaluation Highlight
            if step.current_pair:
                id_a, id_b = step.current_pair
                ac_a = next((a for a in self.aircraft_list if a.id == id_a), None)
                ac_b = next((a for a in self.aircraft_list if a.id == id_b), None)
                if ac_a and ac_b:
                    eval_color = COLOR_HIGH if step.active_pair_threat == "HIGH" else (
                        COLOR_MEDIUM if step.active_pair_threat == "MEDIUM" else (
                            COLOR_LOW if step.active_pair_threat == "LOW" else "#FFD166"
                        )
                    )
                    self.ax.plot(
                        [ac_a.x, ac_b.x], [ac_a.y, ac_b.y],
                        color=eval_color, linestyle="-", linewidth=2.5, alpha=0.9
                    )

        # 5. Aircraft Conflict Lines
        # Use active step conflicts if replaying steps, else global conflicts
        displayed_conflicts = self.active_step.conflicts_found_so_far if self.active_step else self.conflicts
        for conflict in displayed_conflicts:
            ac1, ac2 = conflict.aircraft_a, conflict.aircraft_b
            color = conflict.threat_level.color
            ls = "--" if conflict.threat_level == ThreatLevel.HIGH else "-."
            lw = 2.0 if conflict.threat_level == ThreatLevel.HIGH else 1.3
            self.ax.plot([ac1.x, ac2.x], [ac1.y, ac2.y], color=color, linestyle=ls, linewidth=lw, alpha=0.75)

            # Draw threat collision point marker at closest approach
            pt_a = conflict.pos_a_at_t
            pt_b = conflict.pos_b_at_t
            mid_t_x = (pt_a[0] + pt_b[0]) / 2.0
            mid_t_y = (pt_a[1] + pt_b[1]) / 2.0
            self.ax.plot(mid_t_x, mid_t_y, marker="x", color=color, markersize=7, markeredgewidth=1.8)

        # Highlight manually selected pair
        if self.selected_pair:
            id1, id2 = self.selected_pair
            ac_a = next((a for a in self.aircraft_list if a.id == id1), None)
            ac_b = next((a for a in self.aircraft_list if a.id == id2), None)
            if ac_a and ac_b:
                self.ax.plot([ac_a.x, ac_b.x], [ac_a.y, ac_b.y],
                             color="#FFFFFF", linestyle=":", linewidth=2.8, alpha=0.95)

        # Map aircraft ID to its highest threat level
        aircraft_threats: Dict[str, ThreatLevel] = {}
        for c in displayed_conflicts:
            for ac in (c.aircraft_a, c.aircraft_b):
                curr = aircraft_threats.get(ac.id, ThreatLevel.SAFE)
                if c.threat_level.rank < curr.rank:
                    aircraft_threats[ac.id] = c.threat_level

        horizon = max(0.0, self.config.prediction_horizon)

        # 6. Draw Aircraft Symbols, Velocity Vectors, and Trajectories
        for ac in self.aircraft_list:
            threat = aircraft_threats.get(ac.id, ThreatLevel.SAFE)
            color = threat.color
            is_selected = (ac.id == self.selected_aircraft_id)

            # Projected trajectory line (dashed)
            future_x = ac.x + ac.vx * horizon
            future_y = ac.y + ac.vy * horizon
            self.ax.plot(
                [ac.x, future_x], [ac.y, future_y],
                color=color, linestyle=":", linewidth=1.2, alpha=0.6
            )
            self.ax.plot(future_x, future_y, marker=".", color=color, markersize=3, alpha=0.5)

            # Velocity vector arrow (30-second standard lookahead arrow)
            arrow_scale = 30.0
            dx = ac.vx * arrow_scale
            dy = ac.vy * arrow_scale
            if abs(dx) > 0.05 or abs(dy) > 0.05:
                self.ax.arrow(
                    ac.x, ac.y, dx, dy,
                    head_width=1.2, head_length=1.5,
                    fc=color, ec=color, length_includes_head=True, alpha=0.85
                )

            # Aircraft Blip Circle
            marker_size = 9 if not is_selected else 13
            self.ax.plot(
                ac.x, ac.y,
                marker="o", color=color, markersize=marker_size,
                markeredgecolor="#FFFFFF" if is_selected else color,
                markeredgewidth=2.0 if is_selected else 1.0,
                zorder=5
            )

            # Selection glow ring
            if is_selected:
                sel_ring = patches.Circle(
                    (ac.x, ac.y), 3.0, fill=False,
                    edgecolor="#FFFFFF", linestyle="-", linewidth=1.5, alpha=0.9
                )
                self.ax.add_patch(sel_ring)

            # Aircraft Call Sign & Altitude Tag
            label_text = f"{ac.id}\nFL{int(ac.altitude * 32.808):03d} • {ac.altitude:.1f}k"
            self.ax.text(
                ac.x + 1.2, ac.y + 1.2, label_text,
                color="#FFFFFF", fontsize=8, fontweight="bold",
                bbox=dict(boxstyle="square,pad=0.2", facecolor=RADAR_CANVAS_BG, edgecolor=color, alpha=0.75),
                zorder=6
            )

        # Set labels and radar aesthetics
        self.ax.set_xlabel("East-West Distance (km)", color=ACCENT_CYAN, fontsize=9, labelpad=5)
        self.ax.set_ylabel("North-South Distance (km)", color=ACCENT_CYAN, fontsize=9, labelpad=5)
        self.ax.tick_params(colors=RADAR_AXIS_COLOR, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(RADAR_AXIS_COLOR)
            spine.set_linewidth(1.0)

        self.canvas.draw_idle()
