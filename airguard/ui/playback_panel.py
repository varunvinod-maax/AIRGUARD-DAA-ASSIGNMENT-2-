import customtkinter as ctk
from typing import Optional, Callable
from algorithms.state_tracer import AlgorithmStep, ExecutionTracer
from ui.theme import (
    BG_PANEL, BG_CARD, BG_INPUT, BG_BORDER, BG_HOVER,
    ACCENT_CYAN, ACCENT_BLUE, ACCENT_PURPLE, COLOR_HIGH, COLOR_MEDIUM,
    COLOR_SAFE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    FONT_HEADING, FONT_SMALL, FONT_BODY, FONT_MONO, FONT_MONO_BOLD
)


class PlaybackPanel(ctk.CTkFrame):
    """Bottom panel managing Divide & Conquer execution and granular step replay."""
    def __init__(
        self,
        master,
        on_start_pause: Callable[[], None],
        on_prev_step: Callable[[], None],
        on_next_step: Callable[[], None],
        on_run_complete: Callable[[], None],
        on_reset_steps: Callable[[], None],
        on_speed_changed: Callable[[float], None],
        **kwargs
    ):
        super().__init__(master, fg_color=BG_PANEL, height=130, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self.on_start_pause = on_start_pause
        self.on_prev_step = on_prev_step
        self.on_next_step = on_next_step
        self.on_run_complete = on_run_complete
        self.on_reset_steps = on_reset_steps
        self.on_speed_changed = on_speed_changed

        self.is_running = False

        self._build_controls_row()
        self._build_status_row()

    def _build_controls_row(self):
        ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=16, pady=(10, 4))

        # Action Buttons
        self.btn_play = ctk.CTkButton(
            ctrl_frame, text="▶ Start Analysis", font=FONT_HEADING,
            fg_color="#10B981", hover_color="#059669", width=140, height=32,
            command=self.on_start_pause
        )
        self.btn_play.pack(side="left", padx=(0, 6))

        self.btn_prev = ctk.CTkButton(
            ctrl_frame, text="⏮ Prev Step", font=FONT_SMALL,
            fg_color=BG_CARD, hover_color=BG_HOVER, width=100, height=32,
            command=self.on_prev_step
        )
        self.btn_prev.pack(side="left", padx=4)

        self.btn_next = ctk.CTkButton(
            ctrl_frame, text="⏭ Next Step", font=FONT_SMALL,
            fg_color=BG_CARD, hover_color=BG_HOVER, width=100, height=32,
            command=self.on_next_step
        )
        self.btn_next.pack(side="left", padx=4)

        self.btn_complete = ctk.CTkButton(
            ctrl_frame, text="⏩ Run to End", font=FONT_SMALL,
            fg_color="#3B82F6", hover_color="#2563EB", width=100, height=32,
            command=self.on_run_complete
        )
        self.btn_complete.pack(side="left", padx=4)

        self.btn_reset = ctk.CTkButton(
            ctrl_frame, text="↺ Reset", font=FONT_SMALL,
            fg_color=BG_CARD, hover_color=BG_HOVER, width=75, height=32,
            command=self.on_reset_steps
        )
        self.btn_reset.pack(side="left", padx=4)

        # Right side: Speed selector and progress indicator
        right_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        right_frame.pack(side="right")

        ctk.CTkLabel(right_frame, text="Speed:", font=FONT_SMALL, text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=4)
        self.speed_slider = ctk.CTkSlider(
            right_frame, from_=0.05, to=1.5, number_of_steps=10, width=110,
            command=self._handle_speed_slider
        )
        self.speed_slider.set(0.4)
        self.speed_slider.pack(side="left", padx=4)

        self.lbl_step_counter = ctk.CTkLabel(
            right_frame, text="Step 0 / 0", font=FONT_MONO_BOLD, text_color=ACCENT_CYAN,
            fg_color=BG_CARD, corner_radius=6, padx=10, pady=4
        )
        self.lbl_step_counter.pack(side="left", padx=(10, 0))

    def _build_status_row(self):
        status_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=6, height=52)
        status_frame.pack(fill="x", padx=16, pady=(4, 8))
        status_frame.pack_propagate(False)

        # Progress bar at top of card
        self.progress_bar = ctk.CTkProgressBar(status_frame, height=4, corner_radius=0, fg_color="#1E293B", progress_color=ACCENT_CYAN)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x")

        inner_row = ctk.CTkFrame(status_frame, fg_color="transparent")
        inner_row.pack(fill="both", expand=True, padx=12, pady=4)

        # Phase Badge
        self.lbl_phase = ctk.CTkLabel(
            inner_row, text="IDLE", font=FONT_MONO_BOLD, text_color="#FFFFFF",
            fg_color="#334155", corner_radius=4, padx=8, pady=2
        )
        self.lbl_phase.pack(side="left", padx=(0, 10))

        # Main Description Text
        self.lbl_desc = ctk.CTkLabel(
            inner_row,
            text="Ready to execute Divide and Conquer collision detection. Click 'Start Analysis' or 'Next Step'.",
            font=FONT_SMALL, text_color=COLOR_TEXT_PRIMARY, anchor="w"
        )
        self.lbl_desc.pack(side="left", fill="x", expand=True)

        # Telemetry Badges
        self.lbl_depth = self._create_badge(inner_row, "Depth: 0", ACCENT_PURPLE)
        self.lbl_comparisons = self._create_badge(inner_row, "Comps: 0", ACCENT_CYAN)
        self.lbl_conflicts = self._create_badge(inner_row, "Threats: 0", COLOR_HIGH)

    def _create_badge(self, parent, text: str, color: str) -> ctk.CTkLabel:
        badge = ctk.CTkLabel(
            parent, text=text, font=FONT_MONO, text_color=color,
            fg_color=BG_INPUT, corner_radius=4, padx=8, pady=2
        )
        badge.pack(side="right", padx=3)
        return badge

    def _handle_speed_slider(self, val: float):
        self.on_speed_changed(float(val))

    def set_playing_state(self, playing: bool):
        self.is_running = playing
        if playing:
            self.btn_play.configure(text="⏸ Pause", fg_color="#F59E0B", hover_color="#D97706")
        else:
            self.btn_play.configure(text="▶ Resume" if self.progress_bar.get() > 0 else "▶ Start Analysis",
                                    fg_color="#10B981", hover_color="#059669")

    def update_step_state(self, step: Optional[AlgorithmStep], current_idx: int, total_steps: int):
        if not step or total_steps == 0:
            self.progress_bar.set(0.0)
            self.lbl_step_counter.configure(text="Step 0 / 0")
            self.lbl_phase.configure(text="IDLE", fg_color="#334155")
            self.lbl_desc.configure(text="Ready to execute Divide and Conquer. Click 'Start Analysis'.")
            self.lbl_depth.configure(text="Depth: 0")
            self.lbl_comparisons.configure(text="Comps: 0")
            self.lbl_conflicts.configure(text="Threats: 0")
            return

        prog = (current_idx + 1) / max(1, total_steps)
        self.progress_bar.set(prog)
        self.lbl_step_counter.configure(text=f"Step {current_idx + 1} / {total_steps}")

        # Update Phase Badge
        phase = step.phase
        phase_colors = {
            "SORT": "#3B82F6",
            "DIVIDE": "#EC4899",
            "RECURSE_LEFT": "#8B5CF6",
            "RECURSE_RIGHT": "#8B5CF6",
            "STRIP_CHECK": "#06B6D4",
            "BASE_CASE": "#F59E0B",
            "EVALUATE_PAIR": "#EF4444" if step.active_pair_threat in ["HIGH", "MEDIUM"] else "#10B981",
            "COMPLETE": "#10B981"
        }
        self.lbl_phase.configure(text=phase, fg_color=phase_colors.get(phase, "#334155"))

        # Update Description
        self.lbl_desc.configure(text=step.description)

        # Update Badges
        self.lbl_depth.configure(text=f"Depth: {step.depth}")
        self.lbl_comparisons.configure(text=f"Comps: {step.comparisons_count}")
        self.lbl_conflicts.configure(text=f"Threats: {len(step.conflicts_found_so_far)}")
