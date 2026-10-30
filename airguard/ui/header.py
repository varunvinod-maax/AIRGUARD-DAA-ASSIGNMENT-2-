import customtkinter as ctk
from typing import Callable
from ui.theme import (
    BG_PANEL, BG_CARD, ACCENT_CYAN, ACCENT_BLUE, COLOR_SAFE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_SMALL, FONT_HEADING
)


class HeaderFrame(ctk.CTkFrame):
    """Header bar with branding, status badges, and top-level action buttons."""
    def __init__(
        self,
        master,
        on_open_explained: Callable[[], None],
        on_generate_report: Callable[[], None],
        on_reset_all: Callable[[], None],
        **kwargs
    ):
        super().__init__(master, fg_color=BG_PANEL, height=64, corner_radius=0, **kwargs)
        self.pack_propagate(False)

        # Left branding container
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(side="left", padx=20, pady=10)

        # Radar symbol & Title
        title_row = ctk.CTkFrame(brand_frame, fg_color="transparent")
        title_row.pack(anchor="w")

        icon_label = ctk.CTkLabel(
            title_row, text="✈ ⌖", font=("Segoe UI", 18, "bold"), text_color=ACCENT_CYAN
        )
        icon_label.pack(side="left", padx=(0, 8))

        app_title = ctk.CTkLabel(
            title_row, text="AirGuard", font=FONT_TITLE, text_color=COLOR_TEXT_PRIMARY
        )
        app_title.pack(side="left")

        subtitle = ctk.CTkLabel(
            brand_frame, text="Divide & Conquer Collision Threat Detector • DAA Assignment 2",
            font=FONT_SMALL, text_color=COLOR_TEXT_SECONDARY
        )
        subtitle.pack(anchor="w")

        # Center Status Badges
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.pack(side="left", expand=True, padx=10)

        self.status_badge = ctk.CTkLabel(
            status_frame, text="STATUS: READY", font=("Segoe UI", 11, "bold"),
            text_color=COLOR_SAFE, fg_color=BG_CARD, corner_radius=6, padx=12, pady=4
        )
        self.status_badge.pack(side="left", padx=5)

        disclaimer_badge = ctk.CTkLabel(
            status_frame, text="⚠ EDUCATIONAL SIMULATION ONLY — NOT CERTIFIED FOR ATC",
            font=("Segoe UI", 9, "bold"), text_color="#FFB703", fg_color=BG_CARD,
            corner_radius=6, padx=10, pady=4
        )
        disclaimer_badge.pack(side="left", padx=5)

        # Right Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)

        self.btn_explained = ctk.CTkButton(
            btn_frame, text="📘 Algorithm Explained", font=FONT_SMALL,
            fg_color=BG_CARD, hover_color="#24375D", text_color=ACCENT_CYAN,
            border_color=ACCENT_CYAN, border_width=1, width=155, height=32,
            command=on_open_explained
        )
        self.btn_explained.pack(side="left", padx=6)

        self.btn_report = ctk.CTkButton(
            btn_frame, text="📄 Generate Report", font=FONT_SMALL,
            fg_color="#1D4ED8", hover_color="#1E40AF", text_color=COLOR_TEXT_PRIMARY,
            width=135, height=32,
            command=on_generate_report
        )
        self.btn_report.pack(side="left", padx=6)

        self.btn_reset = ctk.CTkButton(
            btn_frame, text="↺ Reset", font=FONT_SMALL,
            fg_color=BG_CARD, hover_color="#334155", text_color=COLOR_TEXT_SECONDARY,
            width=75, height=32,
            command=on_reset_all
        )
        self.btn_reset.pack(side="left", padx=6)

    def set_status(self, text: str, color: str = COLOR_SAFE) -> None:
        self.status_badge.configure(text=f"STATUS: {text}", text_color=color)
