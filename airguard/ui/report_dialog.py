import os
import webbrowser
import customtkinter as ctk
from typing import Dict, Any, List, Optional
from matplotlib.figure import Figure

from models.aircraft import Aircraft
from models.conflict import ConflictPair, ThresholdConfig
from reports.report_generator import generate_assignment_html_report
from ui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, BG_INPUT, ACCENT_CYAN, ACCENT_BLUE,
    COLOR_SAFE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE,
    FONT_HEADING, FONT_SMALL, FONT_BODY
)


class ReportDialog(ctk.CTkToplevel):
    """Dialog collecting student details to produce the assignment submission report."""
    def __init__(
        self,
        parent,
        scenario_name: str,
        aircraft_list: List[Aircraft],
        conflicts: List[ConflictPair],
        config: ThresholdConfig,
        radar_figure: Optional[Figure] = None
    ):
        super().__init__(parent)
        self.title("AirGuard — Generate Assignment Report")
        self.geometry("560, 480")
        self.configure(fg_color=BG_DARK)
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.scenario_name = scenario_name
        self.aircraft_list = aircraft_list
        self.conflicts = conflicts
        self.config = config
        self.radar_figure = radar_figure

        # Header
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, height=55, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text="📄 GENERATE ASSIGNMENT REPORT",
            font=FONT_TITLE, text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=12)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=15)

        ctk.CTkLabel(
            body, text="Enter your academic credentials for the report header:",
            font=FONT_SMALL, text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(0, 10))

        # Fields
        self.ent_name = self._add_field(body, "Student Full Name:", "e.g. Alex Mercer")
        self.ent_roll = self._add_field(body, "Roll / Registration Number:", "e.g. 21BCE1042")
        self.ent_dept = self._add_field(body, "Department & Specialization:", "B.Tech Computer Science (Cybersecurity)")
        self.ent_course = self._add_field(body, "Course Title & Code:", "Design & Analysis of Algorithms (CSE3001)")
        self.ent_inst = self._add_field(body, "Institution / University:", "School of Computer Science & Engineering")

        self.lbl_status = ctk.CTkLabel(body, text="", font=FONT_SMALL, text_color=COLOR_SAFE)
        self.lbl_status.pack(pady=4)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color=BG_PANEL, height=60, corner_radius=0)
        btn_frame.pack(fill="x", side="bottom")

        btn_cancel = ctk.CTkButton(
            btn_frame, text="Cancel", fg_color=BG_CARD, hover_color="#334155",
            width=100, height=32, command=self.destroy
        )
        btn_cancel.pack(side="right", padx=15, pady=14)

        btn_gen = ctk.CTkButton(
            btn_frame, text="Generate & Open Report", fg_color=ACCENT_BLUE,
            hover_color="#2563EB", font=FONT_HEADING, width=190, height=32,
            command=self._generate_report
        )
        btn_gen.pack(side="right", padx=5, pady=14)

    def _add_field(self, parent, label_text: str, default_val: str) -> ctk.CTkEntry:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label_text, font=FONT_SMALL, width=190, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(row, fg_color=BG_INPUT, height=28)
        entry.insert(0, default_val)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def _generate_report(self):
        student_info = {
            "name": self.ent_name.get().strip() or "Student",
            "roll": self.ent_roll.get().strip() or "N/A",
            "department": self.ent_dept.get().strip(),
            "course": self.ent_course.get().strip(),
            "institution": self.ent_inst.get().strip()
        }

        html_content = generate_assignment_html_report(
            student_info=student_info,
            scenario_name=self.scenario_name,
            aircraft_list=self.aircraft_list,
            conflicts=self.conflicts,
            config=self.config,
            radar_figure=self.radar_figure
        )

        # Write to report file
        out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports_output"))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "AirGuard_Assignment2_Report.html")

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.lbl_status.configure(text=f"Report generated successfully: {os.path.basename(out_path)}")
        webbrowser.open(f"file://{out_path}")
