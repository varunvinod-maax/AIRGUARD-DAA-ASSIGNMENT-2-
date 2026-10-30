import customtkinter as ctk
from typing import List, Callable, Optional
from models.aircraft import Aircraft, AircraftValidationError
from models.scenarios import PRESET_SCENARIOS
from ui.theme import (
    BG_PANEL, BG_CARD, BG_INPUT, BG_BORDER, BG_HOVER,
    ACCENT_CYAN, ACCENT_BLUE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_HIGH, COLOR_SAFE, FONT_HEADING, FONT_SMALL, FONT_BODY
)


class SidebarControls(ctk.CTkFrame):
    """Left sidebar containing aircraft management, scenarios, and traffic generators."""
    def __init__(
        self,
        master,
        on_add_aircraft: Callable[[Aircraft], None],
        on_remove_aircraft: Callable[[str], None],
        on_load_scenario: Callable[[str], None],
        on_generate_random: Callable[[int, int], None],
        on_clear_all: Callable[[], None],
        on_horizon_changed: Callable[[float], None],
        **kwargs
    ):
        super().__init__(master, fg_color=BG_PANEL, width=320, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        self.on_add_aircraft = on_add_aircraft
        self.on_remove_aircraft = on_remove_aircraft
        self.on_load_scenario = on_load_scenario
        self.on_generate_random = on_generate_random
        self.on_clear_all = on_clear_all
        self.on_horizon_changed = on_horizon_changed

        self.aircraft_list: List[Aircraft] = []

        # Scrollable container for controls
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=12, pady=10)

        self._build_add_aircraft_section()
        self._build_aircraft_list_section()
        self._build_scenarios_section()
        self._build_random_generator_section()
        self._build_horizon_section()

    def _build_add_aircraft_section(self):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=(0, 10), padx=2)

        lbl = ctk.CTkLabel(card, text="✈ ADD AIRCRAFT", font=FONT_HEADING, text_color=ACCENT_CYAN)
        lbl.pack(anchor="w", padx=12, pady=(10, 6))

        # ID & Category
        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(r1, text="Callsign / ID:", font=FONT_SMALL, width=80, anchor="w").pack(side="left")
        self.ent_id = ctk.CTkEntry(r1, placeholder_text="e.g. AI-202", width=95, height=26, fg_color=BG_INPUT)
        self.ent_id.pack(side="left", padx=4)
        self.combo_cat = ctk.CTkComboBox(
            r1, values=["COMMERCIAL", "CARGO", "MILITARY", "PRIVATE"],
            width=95, height=26, fg_color=BG_INPUT
        )
        self.combo_cat.set("COMMERCIAL")
        self.combo_cat.pack(side="left")

        # X & Y positions
        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(r2, text="Pos X (km):", font=FONT_SMALL, width=80, anchor="w").pack(side="left")
        self.ent_x = ctk.CTkEntry(r2, placeholder_text="-20.0", width=95, height=26, fg_color=BG_INPUT)
        self.ent_x.pack(side="left", padx=4)
        ctk.CTkLabel(r2, text="Y (km):", font=FONT_SMALL, width=45, anchor="w").pack(side="left")
        self.ent_y = ctk.CTkEntry(r2, placeholder_text="15.0", width=50, height=26, fg_color=BG_INPUT)
        self.ent_y.pack(side="left")

        # Altitude & Velocities
        r3 = ctk.CTkFrame(card, fg_color="transparent")
        r3.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(r3, text="Altitude (km):", font=FONT_SMALL, width=80, anchor="w").pack(side="left")
        self.ent_alt = ctk.CTkEntry(r3, placeholder_text="10.0", width=95, height=26, fg_color=BG_INPUT)
        self.ent_alt.pack(side="left", padx=4)

        r4 = ctk.CTkFrame(card, fg_color="transparent")
        r4.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(r4, text="Vx (km/s):", font=FONT_SMALL, width=80, anchor="w").pack(side="left")
        self.ent_vx = ctk.CTkEntry(r4, placeholder_text="0.20", width=95, height=26, fg_color=BG_INPUT)
        self.ent_vx.pack(side="left", padx=4)
        ctk.CTkLabel(r4, text="Vy:", font=FONT_SMALL, width=45, anchor="w").pack(side="left")
        self.ent_vy = ctk.CTkEntry(r4, placeholder_text="0.00", width=50, height=26, fg_color=BG_INPUT)
        self.ent_vy.pack(side="left")

        # Error message label
        self.lbl_error = ctk.CTkLabel(card, text="", font=FONT_SMALL, text_color=COLOR_HIGH, wraplength=270)
        self.lbl_error.pack(padx=12, pady=(2, 2))

        # Add Button
        self.btn_add = ctk.CTkButton(
            card, text="+ Add Aircraft", font=FONT_SMALL, fg_color=ACCENT_BLUE,
            hover_color="#2563EB", height=28, command=self._handle_add_aircraft
        )
        self.btn_add.pack(fill="x", padx=12, pady=(4, 10))

    def _build_aircraft_list_section(self):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=(0, 10), padx=2)

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 4))
        self.lbl_count = ctk.CTkLabel(header_row, text="AIRCRAFT IN SECTOR (0)", font=FONT_HEADING, text_color=ACCENT_CYAN)
        self.lbl_count.pack(side="left")

        # Scrollable list of aircraft badges
        self.list_frame = ctk.CTkScrollableFrame(card, fg_color=BG_INPUT, height=110)
        self.list_frame.pack(fill="x", padx=12, pady=4)

        # Action row
        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.pack(fill="x", padx=12, pady=(6, 10))

        self.btn_remove = ctk.CTkButton(
            action_row, text="Remove Selected", font=FONT_SMALL,
            fg_color="#DC2626", hover_color="#991B1B", height=26, width=120,
            command=self._handle_remove_selected
        )
        self.btn_remove.pack(side="left")

        self.btn_clear = ctk.CTkButton(
            action_row, text="Clear All", font=FONT_SMALL,
            fg_color="#475569", hover_color="#334155", height=26, width=90,
            command=self.on_clear_all
        )
        self.btn_clear.pack(side="right")

    def _build_scenarios_section(self):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=(0, 10), padx=2)

        lbl = ctk.CTkLabel(card, text="📁 DEMONSTRATION SCENARIOS", font=FONT_HEADING, text_color=ACCENT_CYAN)
        lbl.pack(anchor="w", padx=12, pady=(10, 6))

        scenario_names = list(PRESET_SCENARIOS.keys())
        self.combo_scenarios = ctk.CTkComboBox(
            card, values=scenario_names, height=28, fg_color=BG_INPUT,
            font=FONT_SMALL, dropdown_font=FONT_SMALL
        )
        self.combo_scenarios.set(scenario_names[3])  # Default to Multiple Conflicts
        self.combo_scenarios.pack(fill="x", padx=12, pady=4)

        btn_load = ctk.CTkButton(
            card, text="Load Scenario", font=FONT_SMALL,
            fg_color="#0D9488", hover_color="#0F766E", height=28,
            command=self._handle_load_scenario
        )
        btn_load.pack(fill="x", padx=12, pady=(4, 10))

    def _build_random_generator_section(self):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=(0, 10), padx=2)

        lbl = ctk.CTkLabel(card, text="🎲 RANDOM TRAFFIC GENERATOR", font=FONT_HEADING, text_color=ACCENT_CYAN)
        lbl.pack(anchor="w", padx=12, pady=(10, 6))

        r1 = ctk.CTkFrame(card, fg_color="transparent")
        r1.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(r1, text="Aircraft Count:", font=FONT_SMALL, width=100, anchor="w").pack(side="left")
        self.ent_rnd_count = ctk.CTkEntry(r1, width=60, height=24, fg_color=BG_INPUT)
        self.ent_rnd_count.insert(0, "10")
        self.ent_rnd_count.pack(side="left")

        r2 = ctk.CTkFrame(card, fg_color="transparent")
        r2.pack(fill="x", padx=12, pady=2)
        ctk.CTkLabel(r2, text="Random Seed:", font=FONT_SMALL, width=100, anchor="w").pack(side="left")
        self.ent_rnd_seed = ctk.CTkEntry(r2, width=60, height=24, fg_color=BG_INPUT)
        self.ent_rnd_seed.insert(0, "42")
        self.ent_rnd_seed.pack(side="left")

        btn_gen = ctk.CTkButton(
            card, text="Generate Traffic", font=FONT_SMALL,
            fg_color="#7C3AED", hover_color="#6D28D9", height=28,
            command=self._handle_generate_random
        )
        btn_gen.pack(fill="x", padx=12, pady=(6, 10))

    def _build_horizon_section(self):
        card = ctk.CTkFrame(self.scroll, fg_color=BG_CARD, corner_radius=8)
        card.pack(fill="x", pady=(0, 10), padx=2)

        self.lbl_horizon = ctk.CTkLabel(
            card, text="⏱ PREDICTION HORIZON: 60s", font=FONT_HEADING, text_color=ACCENT_CYAN
        )
        self.lbl_horizon.pack(anchor="w", padx=12, pady=(10, 4))

        self.slider_horizon = ctk.CTkSlider(
            card, from_=10.0, to=120.0, number_of_steps=22,
            command=self._handle_horizon_slider
        )
        self.slider_horizon.set(60.0)
        self.slider_horizon.pack(fill="x", padx=12, pady=(4, 10))

    def _handle_horizon_slider(self, value: float):
        sec = int(round(value))
        self.lbl_horizon.configure(text=f"⏱ PREDICTION HORIZON: {sec}s")
        self.on_horizon_changed(float(sec))

    def _handle_add_aircraft(self):
        self.lbl_error.configure(text="")
        try:
            ac_id = self.ent_id.get().strip().upper()
            x = float(self.ent_x.get().strip())
            y = float(self.ent_y.get().strip())
            alt = float(self.ent_alt.get().strip())
            vx = float(self.ent_vx.get().strip())
            vy = float(self.ent_vy.get().strip())
            cat = self.combo_cat.get()

            ac = Aircraft(id=ac_id, x=x, y=y, altitude=alt, vx=vx, vy=vy, callsign=cat)
            self.on_add_aircraft(ac)

            # Clear inputs
            self.ent_id.delete(0, "end")
            self.ent_x.delete(0, "end")
            self.ent_y.delete(0, "end")
            self.ent_alt.delete(0, "end")
            self.ent_vx.delete(0, "end")
            self.ent_vy.delete(0, "end")
        except AircraftValidationError as e:
            self.lbl_error.configure(text=str(e))
        except ValueError:
            self.lbl_error.configure(text="Coordinates, altitude, and velocities must be numeric values.")

    def _handle_remove_selected(self):
        if hasattr(self, "selected_id_var") and self.selected_id_var.get():
            self.on_remove_aircraft(self.selected_id_var.get())

    def _handle_load_scenario(self):
        scenario_name = self.combo_scenarios.get()
        self.on_load_scenario(scenario_name)

    def _handle_generate_random(self):
        try:
            count = int(self.ent_rnd_count.get().strip())
            seed = int(self.ent_rnd_seed.get().strip())
            count = max(2, min(count, 40))
            self.on_generate_random(count, seed)
        except ValueError:
            self.lbl_error.configure(text="Count and Seed must be valid integers.")

    def update_aircraft_list(self, aircraft_list: List[Aircraft]):
        self.aircraft_list = aircraft_list
        self.lbl_count.configure(text=f"AIRCRAFT IN SECTOR ({len(aircraft_list)})")

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        self.selected_id_var = ctk.StringVar(value="")

        for ac in aircraft_list:
            item = ctk.CTkRadioButton(
                self.list_frame,
                text=f"{ac.id} (FL{int(ac.altitude*32.8):03d}, {ac.speed*3600:.0f}km/h)",
                value=ac.id,
                variable=self.selected_id_var,
                font=FONT_SMALL,
                text_color=COLOR_TEXT_PRIMARY
            )
            item.pack(anchor="w", padx=4, pady=2)
