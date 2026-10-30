import customtkinter as ctk
from typing import List, Optional, Tuple, Callable
from models.conflict import ConflictPair, ThreatLevel
from models.aircraft import Aircraft
from ui.theme import (
    BG_PANEL, BG_CARD, BG_INPUT, BG_BORDER, BG_HOVER,
    ACCENT_CYAN, COLOR_HIGH, COLOR_MEDIUM, COLOR_LOW, COLOR_SAFE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    FONT_HEADING, FONT_SMALL, FONT_TITLE, FONT_MONO, FONT_MONO_BOLD
)


class SidebarThreats(ctk.CTkFrame):
    """Right sidebar containing threat statistics, conflict tables, and inspector cards."""
    def __init__(
        self,
        master,
        on_pair_selected: Callable[[Tuple[str, str]], None],
        **kwargs
    ):
        super().__init__(master, fg_color=BG_PANEL, width=340, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self.on_pair_selected = on_pair_selected
        self.conflicts: List[ConflictPair] = []
        self.selected_pair: Optional[Tuple[str, str]] = None

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=10)

        self._build_stats_section()
        self._build_table_section()
        self._build_inspector_section()

    def _build_stats_section(self):
        lbl = ctk.CTkLabel(self.scroll, text="📊 THREAT TELEMETRY", font=FONT_HEADING, text_color=ACCENT_CYAN)
        lbl.pack(anchor="w", padx=2, pady=(0, 6))

        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 10))

        # 4 Summary Cards
        self.card_total = self._create_stat_card(grid, "TOTAL AIRCRAFT", "0", ACCENT_CYAN, 0, 0)
        self.card_evaluated = self._create_stat_card(grid, "EVALUATED PAIRS", "0", "#A855F7", 0, 1)
        self.card_conflicts = self._create_stat_card(grid, "TOTAL CONFLICTS", "0", COLOR_MEDIUM, 1, 0)
        self.card_high = self._create_stat_card(grid, "HIGH THREATS", "0", COLOR_HIGH, 1, 1)

    def _create_stat_card(self, parent, title: str, init_val: str, color: str, row: int, col: int) -> ctk.CTkLabel:
        frame = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, height=62)
        frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        t_lbl = ctk.CTkLabel(frame, text=title, font=("Segoe UI", 9, "bold"), text_color=COLOR_TEXT_SECONDARY)
        t_lbl.pack(anchor="w", padx=8, pady=(6, 0))

        v_lbl = ctk.CTkLabel(frame, text=init_val, font=("Segoe UI", 16, "bold"), text_color=color)
        v_lbl.pack(anchor="w", padx=8, pady=(0, 6))
        return v_lbl

    def _build_table_section(self):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=(0, 10), padx=2)

        lbl = ctk.CTkLabel(card, text="⚠ CONFLICT RANKING TABLE", font=FONT_HEADING, text_color=ACCENT_CYAN)
        lbl.pack(anchor="w", padx=12, pady=(10, 4))

        # Table header row
        h_row = ctk.CTkFrame(card, fg_color=BG_INPUT, height=26, corner_radius=4)
        h_row.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(h_row, text="PAIR", font=FONT_MONO_BOLD, width=80, anchor="w").pack(side="left", padx=4)
        ctk.CTkLabel(h_row, text="THREAT", font=FONT_MONO_BOLD, width=65, anchor="center").pack(side="left")
        ctk.CTkLabel(h_row, text="t (s)", font=FONT_MONO_BOLD, width=45, anchor="center").pack(side="left")
        ctk.CTkLabel(h_row, text="HORIZ", font=FONT_MONO_BOLD, width=50, anchor="e").pack(side="left")
        ctk.CTkLabel(h_row, text="VERT", font=FONT_MONO_BOLD, width=50, anchor="e").pack(side="left")

        # Scrollable container for conflict rows
        self.table_rows_container = ctk.CTkScrollableFrame(card, fg_color="transparent", height=180)
        self.table_rows_container.pack(fill="x", padx=6, pady=(2, 10))

    def _build_inspector_section(self):
        self.inspector_card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        self.inspector_card.pack(fill="x", pady=(0, 10), padx=2)

        lbl = ctk.CTkLabel(self.inspector_card, text="🔍 INSPECTOR", font=FONT_HEADING, text_color=ACCENT_CYAN)
        lbl.pack(anchor="w", padx=12, pady=(10, 4))

        self.lbl_inspector_text = ctk.CTkLabel(
            self.inspector_card,
            text="Select an aircraft or conflict pair to inspect 3D telemetry details.",
            font=FONT_SMALL,
            text_color=COLOR_TEXT_SECONDARY,
            justify="left",
            wraplength=280
        )
        self.lbl_inspector_text.pack(anchor="w", padx=12, pady=(0, 10))

    def update_telemetry(
        self,
        total_aircraft: int,
        evaluated_pairs: int,
        conflicts: List[ConflictPair]
    ):
        self.conflicts = conflicts
        self.card_total.configure(text=str(total_aircraft))
        self.card_evaluated.configure(text=str(evaluated_pairs))
        self.card_conflicts.configure(text=str(len(conflicts)))

        high_count = sum(1 for c in conflicts if c.threat_level == ThreatLevel.HIGH)
        self.card_high.configure(text=str(high_count))

        # Refresh table rows
        for widget in self.table_rows_container.winfo_children():
            widget.destroy()

        if not conflicts:
            no_lbl = ctk.CTkLabel(
                self.table_rows_container, text="No active collision conflicts detected.",
                font=FONT_SMALL, text_color=COLOR_SAFE
            )
            no_lbl.pack(pady=15)
            return

        for conflict in conflicts:
            row = ctk.CTkButton(
                self.table_rows_container,
                text="",
                fg_color=BG_INPUT,
                hover_color=BG_HOVER,
                height=30,
                corner_radius=4,
                command=lambda c=conflict: self._select_conflict(c)
            )
            row.pack(fill="x", pady=2)

            # Pair label
            p_text = f"{conflict.aircraft_a.id} ↔ {conflict.aircraft_b.id}"
            ctk.CTkLabel(row, text=p_text, font=FONT_MONO, width=85, anchor="w",
                         text_color=COLOR_TEXT_PRIMARY).pack(side="left", padx=4)

            # Threat Badge
            t_color = conflict.threat_level.color
            ctk.CTkLabel(row, text=conflict.threat_level.value, font=FONT_MONO_BOLD, width=60,
                         text_color=t_color).pack(side="left")

            # Time to closest approach
            ctk.CTkLabel(row, text=f"{conflict.time_to_closest_approach:.1f}s", font=FONT_MONO, width=45,
                         text_color=COLOR_TEXT_SECONDARY).pack(side="left")

            # Horizontal separation
            h_text = f"{conflict.horizontal_separation*1000:.0f}m" if conflict.horizontal_separation < 1.0 else f"{conflict.horizontal_separation:.2f}km"
            ctk.CTkLabel(row, text=h_text, font=FONT_MONO, width=50, anchor="e",
                         text_color=COLOR_TEXT_PRIMARY).pack(side="left")

            # Vertical separation
            v_text = f"{conflict.vertical_separation*1000:.0f}m"
            ctk.CTkLabel(row, text=v_text, font=FONT_MONO, width=45, anchor="e",
                         text_color=COLOR_TEXT_SECONDARY).pack(side="left", padx=(0, 4))

    def _select_conflict(self, conflict: ConflictPair):
        self.selected_pair = conflict.pair_key
        self.on_pair_selected(conflict.pair_key)

        info = (
            f"PAIR: {conflict.aircraft_a.id} ↔ {conflict.aircraft_b.id}\n"
            f"THREAT LEVEL: {conflict.threat_level.value}\n"
            f"TIME TO CLOSEST APPROACH: {conflict.time_to_closest_approach:.2f}s\n"
            f"MIN HORIZONTAL SEPARATION: {conflict.horizontal_separation*1000:.1f} m ({conflict.horizontal_separation:.3f} km)\n"
            f"VERTICAL SEPARATION: {conflict.vertical_separation*1000:.1f} m ({conflict.vertical_separation:.3f} km)\n"
            f"RELATIVE CLOSURE SPEED: {conflict.relative_speed*3600:.1f} km/h ({conflict.relative_speed:.3f} km/s)\n"
            f"PROJECTED IMPACT COORD A: ({conflict.pos_a_at_t[0]:.2f}, {conflict.pos_a_at_t[1]:.2f})\n"
            f"PROJECTED IMPACT COORD B: ({conflict.pos_b_at_t[0]:.2f}, {conflict.pos_b_at_t[1]:.2f})"
        )
        self.lbl_inspector_text.configure(text=info, text_color=conflict.threat_level.color)

    def inspect_aircraft(self, ac: Aircraft):
        info = (
            f"AIRCRAFT ID: {ac.id} ({ac.callsign})\n"
            f"CURRENT POSITION: ({ac.x:.2f} km, {ac.y:.2f} km)\n"
            f"ALTITUDE: {ac.altitude:.2f} km (FL{int(ac.altitude*32.8):03d})\n"
            f"VELOCITY: Vx={ac.vx:.3f} km/s, Vy={ac.vy:.3f} km/s\n"
            f"SPEED: {ac.speed*3600:.1f} km/h ({ac.speed:.3f} km/s)\n"
            f"HEADING: {ac.heading_deg:.1f}°"
        )
        self.lbl_inspector_text.configure(text=info, text_color=ACCENT_CYAN)
