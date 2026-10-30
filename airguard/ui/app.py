import tkinter as tk
from typing import List, Optional, Tuple
import customtkinter as ctk

from models.aircraft import Aircraft
from models.conflict import ConflictPair, ThresholdConfig
from models.scenarios import (
    PRESET_SCENARIOS, get_multiple_conflicts_scenario, generate_random_traffic
)
from algorithms.divide_and_conquer import detect_conflicts_divide_and_conquer
from algorithms.state_tracer import ExecutionTracer, AlgorithmStep

from ui.theme import BG_DARK, ACCENT_CYAN, COLOR_SAFE, COLOR_HIGH, COLOR_MEDIUM
from ui.header import HeaderFrame
from ui.sidebar_controls import SidebarControls
from ui.sidebar_threats import SidebarThreats
from ui.playback_panel import PlaybackPanel
from visualization.radar_canvas import RadarCanvas
from ui.educational_dialog import EducationalDialog
from ui.report_dialog import ReportDialog


class AirGuardApp(ctk.CTk):
    """Main AirGuard Desktop GUI Application."""
    def __init__(self):
        super().__init__()

        # Appearance mode & theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("AirGuard — Divide & Conquer Air Traffic Collision Threat Detector")
        self.geometry("1440, 900")
        self.minsize(1180, 750)
        self.configure(fg_color=BG_DARK)

        # State Variables
        self.config = ThresholdConfig()
        self.current_scenario_name = "4. MULTIPLE CONFLICTS (CROSS-BOUNDARY)"
        self.aircraft_list: List[Aircraft] = []
        self.conflicts: List[ConflictPair] = []
        self.total_comparisons: int = 0
        self.tracer: Optional[ExecutionTracer] = None

        # Playback timer state
        self.is_playing: bool = False
        self.playback_speed_sec: float = 0.4
        self.playback_timer_id: Optional[str] = None

        # Build UI Structure
        self._build_layout()

        # Load initial scenario immediately so first screen is active and demonstrable
        self.load_scenario(self.current_scenario_name)

    def _build_layout(self):
        # 1. Top Header
        self.header = HeaderFrame(
            self,
            on_open_explained=self._open_educational_dialog,
            on_generate_report=self._open_report_dialog,
            on_reset_all=self._reset_all
        )
        self.header.pack(fill="x", side="top")

        # 2. Bottom Playback Panel
        self.playback = PlaybackPanel(
            self,
            on_start_pause=self._toggle_playback,
            on_prev_step=self._step_prev,
            on_next_step=self._step_next,
            on_run_complete=self._run_to_completion,
            on_reset_steps=self._reset_steps,
            on_speed_changed=self._set_speed
        )
        self.playback.pack(fill="x", side="bottom")

        # 3. Main Center Body (Left Sidebar | Radar Canvas | Right Sidebar)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # Left Sidebar (Aircraft & Scenario Controls)
        self.sidebar_controls = SidebarControls(
            body,
            on_add_aircraft=self._add_aircraft,
            on_remove_aircraft=self._remove_aircraft,
            on_load_scenario=self.load_scenario,
            on_generate_random=self._generate_random_traffic,
            on_clear_all=self._clear_all_aircraft,
            on_horizon_changed=self._set_horizon
        )
        self.sidebar_controls.pack(side="left", fill="y")

        # Right Sidebar (Threat Telemetry & Conflict Table)
        self.sidebar_threats = SidebarThreats(
            body,
            on_pair_selected=self._on_table_pair_selected
        )
        self.sidebar_threats.pack(side="right", fill="y")

        # Center Radar Visualization Canvas
        self.radar = RadarCanvas(
            body,
            on_aircraft_selected=self._on_radar_aircraft_selected
        )
        self.radar.pack(side="left", fill="both", expand=True)

    # ------------------ Core Algorithm Execution ------------------

    def run_analysis_pipeline(self, record_steps: bool = True):
        """Executes the Divide & Conquer conflict detection pipeline."""
        self._stop_playback_timer()
        try:
            self.conflicts, self.total_comparisons, self.tracer = detect_conflicts_divide_and_conquer(
                self.aircraft_list,
                self.config,
                record_steps=record_steps
            )

            # Update Header Status
            high_count = sum(1 for c in self.conflicts if c.threat_level.value == "HIGH")
            if high_count > 0:
                self.header.set_status(f"HIGH ALERT ({high_count} THREATS)", COLOR_HIGH)
            elif len(self.conflicts) > 0:
                self.header.set_status(f"WARNING ({len(self.conflicts)} CONFLICTS)", COLOR_MEDIUM)
            else:
                self.header.set_status("AIRSPACE CLEAR", COLOR_SAFE)

            # Update Telemetry & Table
            self.sidebar_threats.update_telemetry(
                total_aircraft=len(self.aircraft_list),
                evaluated_pairs=self.total_comparisons,
                conflicts=self.conflicts
            )

            # Update Controls list
            self.sidebar_controls.update_aircraft_list(self.aircraft_list)

            # Update Playback Panel
            current_step = self.tracer.current_step if self.tracer else None
            tot_steps = self.tracer.total_steps if self.tracer else 0
            self.playback.update_step_state(current_step, self.tracer.current_step_index if self.tracer else 0, tot_steps)

            # Render Radar
            self.radar.update_data(
                aircraft_list=self.aircraft_list,
                conflicts=self.conflicts,
                config=self.config,
                active_step=current_step
            )
        except Exception as e:
            self.header.set_status(f"ERROR: {str(e)}", COLOR_HIGH)

    # ------------------ Step-by-Step Playback Controls ------------------

    def _toggle_playback(self):
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        if not self.tracer or self.tracer.total_steps == 0:
            self.run_analysis_pipeline(record_steps=True)
            return

        # If at end, restart
        if self.tracer.current_step_index >= self.tracer.total_steps - 1:
            self.tracer.to_start()

        self.is_playing = True
        self.playback.set_playing_state(True)
        self._playback_tick()

    def _pause_playback(self):
        self.is_playing = False
        self.playback.set_playing_state(False)
        self._stop_playback_timer()

    def _stop_playback_timer(self):
        if self.playback_timer_id is not None:
            self.after_cancel(self.playback_timer_id)
            self.playback_timer_id = None

    def _playback_tick(self):
        if not self.is_playing or not self.tracer:
            return

        if self.tracer.current_step_index < self.tracer.total_steps - 1:
            step = self.tracer.next()
            self._apply_tracer_step(step)
            ms = int(self.playback_speed_sec * 1000)
            self.playback_timer_id = self.after(ms, self._playback_tick)
        else:
            self._pause_playback()

    def _step_next(self):
        self._pause_playback()
        if self.tracer:
            step = self.tracer.next()
            self._apply_tracer_step(step)

    def _step_prev(self):
        self._pause_playback()
        if self.tracer:
            step = self.tracer.prev()
            self._apply_tracer_step(step)

    def _run_to_completion(self):
        self._pause_playback()
        if self.tracer:
            step = self.tracer.to_end()
            self._apply_tracer_step(step)

    def _reset_steps(self):
        self._pause_playback()
        if self.tracer:
            step = self.tracer.to_start()
            self._apply_tracer_step(step)

    def _set_speed(self, speed_sec: float):
        self.playback_speed_sec = speed_sec

    def _apply_tracer_step(self, step: Optional[AlgorithmStep]):
        if not step or not self.tracer:
            return
        self.playback.update_step_state(step, self.tracer.current_step_index, self.tracer.total_steps)
        self.radar.update_data(
            aircraft_list=self.aircraft_list,
            conflicts=step.conflicts_found_so_far,
            config=self.config,
            active_step=step
        )

    # ------------------ Scenario & Aircraft Handlers ------------------

    def load_scenario(self, scenario_name: str):
        self._pause_playback()
        self.current_scenario_name = scenario_name
        gen_fn = PRESET_SCENARIOS.get(scenario_name, get_multiple_conflicts_scenario)
        self.aircraft_list = gen_fn()
        self.radar.set_selected_aircraft(None)
        self.radar.set_selected_pair(None)
        self.run_analysis_pipeline(record_steps=True)

    def _generate_random_traffic(self, count: int, seed: int):
        self._pause_playback()
        self.current_scenario_name = f"RANDOM TRAFFIC (N={count}, Seed={seed})"
        self.aircraft_list = generate_random_traffic(count=count, seed=seed)
        self.radar.set_selected_aircraft(None)
        self.radar.set_selected_pair(None)
        self.run_analysis_pipeline(record_steps=True)

    def _add_aircraft(self, ac: Aircraft):
        # Check duplicate ID
        if any(existing.id == ac.id for existing in self.aircraft_list):
            self.header.set_status(f"Error: Aircraft ID '{ac.id}' already exists.", COLOR_HIGH)
            return
        self.aircraft_list.append(ac)
        self.run_analysis_pipeline(record_steps=True)

    def _remove_aircraft(self, ac_id: str):
        self.aircraft_list = [a for a in self.aircraft_list if a.id != ac_id]
        self.radar.set_selected_aircraft(None)
        self.run_analysis_pipeline(record_steps=True)

    def _clear_all_aircraft(self):
        self._pause_playback()
        self.aircraft_list = []
        self.radar.set_selected_aircraft(None)
        self.radar.set_selected_pair(None)
        self.run_analysis_pipeline(record_steps=True)

    def _set_horizon(self, horizon: float):
        self.config.prediction_horizon = horizon
        self.run_analysis_pipeline(record_steps=True)

    def _reset_all(self):
        self.load_scenario("4. MULTIPLE CONFLICTS (CROSS-BOUNDARY)")

    # ------------------ Interaction Handlers ------------------

    def _on_radar_aircraft_selected(self, ac: Aircraft):
        self.sidebar_threats.inspect_aircraft(ac)

    def _on_table_pair_selected(self, pair: Tuple[str, str]):
        self.radar.set_selected_pair(pair)

    # ------------------ Dialogs ------------------

    def _open_educational_dialog(self):
        EducationalDialog(self)

    def _open_report_dialog(self):
        ReportDialog(
            self,
            scenario_name=self.current_scenario_name,
            aircraft_list=self.aircraft_list,
            conflicts=self.conflicts,
            config=self.config,
            radar_figure=self.radar.fig
        )
