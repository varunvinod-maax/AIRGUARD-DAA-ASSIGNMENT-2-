import customtkinter as ctk
from ui.theme import (
    BG_DARK, BG_PANEL, BG_CARD, BG_INPUT, ACCENT_CYAN, ACCENT_BLUE,
    COLOR_SAFE, COLOR_HIGH, COLOR_MEDIUM, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_SMALL, FONT_BODY, FONT_MONO
)


class EducationalDialog(ctk.CTkToplevel):
    """Educational window explaining Divide & Conquer algorithm mechanics,
    complexity analysis, and Viva preparation cheat sheet.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("AirGuard — Algorithm Explained & Viva Guide")
        self.geometry("900, 680")
        self.configure(fg_color=BG_DARK)

        # Make modal-like
        self.transient(parent)
        self.grab_set()

        # Header banner
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, height=60, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text="📘 ALGORITHM THEORY & COMPLEXITY ANALYSIS",
            font=FONT_TITLE, text_color=ACCENT_CYAN
        ).pack(side="left", padx=20, pady=12)

        btn_close = ctk.CTkButton(
            header, text="✕ Close", width=80, height=28, fg_color=BG_CARD,
            hover_color="#334155", command=self.destroy
        )
        btn_close.pack(side="right", padx=20)

        # Tabbed interface
        tabview = ctk.CTkTabview(self, fg_color=BG_PANEL)
        tabview.pack(fill="both", expand=True, padx=20, pady=15)

        tab1 = tabview.add("1. Divide & Conquer")
        tab2 = tabview.add("2. Closest Approach Math")
        tab3 = tabview.add("3. Complexity Analysis")
        tab4 = tabview.add("4. Viva Q&A Guide")

        self._build_tab1_dac(tab1)
        self._build_tab2_math(tab2)
        self._build_tab3_complexity(tab3)
        self._build_tab4_viva(tab4)

    def _build_tab1_dac(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        content = """
### What is Divide and Conquer?
Divide and Conquer (D&C) is a fundamental algorithmic paradigm that breaks down a complex problem into smaller independent subproblems of the same type, solves them recursively, and finally combines their solutions to form the global solution.

### Step-by-Step AirGuard D&C Spatial Pipeline:

1. **Step 1: Input Validation & Presorting**
   - The airspace contains N aircraft with coordinates (X, Y, Altitude) and velocities (Vx, Vy).
   - Aircraft are sorted along the primary spatial X-axis in O(N log N) time.

2. **Step 2: Base Case (N <= 3)**
   - When a partitioned region contains 3 or fewer aircraft, recursion stops.
   - All pairs within this subproblem are evaluated directly using pairwise kinematic equations.

3. **Step 3: Divide (Spatial Bisection)**
   - The median aircraft index `mid = N // 2` is identified.
   - The spatial dividing line is `X_mid = (X[mid-1] + X[mid]) / 2`.
   - The region is partitioned into Left (P_left) and Right (P_right) halves.

4. **Step 4: Conquer (Recursive Exploration)**
   - `recursive_dac(P_left)` evaluates all conflicts strictly within the Left half.
   - `recursive_dac(P_right)` evaluates all conflicts strictly within the Right half.

5. **Step 5: Combine Step (Cross-Boundary Candidate Strip)**
   - **Crucial Algorithmic Requirement:** An aircraft in the Left half can travel across X_mid and conflict with an aircraft in the Right half during the prediction horizon T!
   - To avoid missing conflicts, AirGuard defines a **Reach Envelope**:
     - For aircraft i: `[min(X_i, X_i + Vx_i * T) - D_max, max(X_i, X_i + Vx_i * T) + D_max]`.
   - Strip_L: Left aircraft whose maximum reach overlaps the Right partition's reach envelope.
   - Strip_R: Right aircraft whose minimum reach overlaps the Left partition's reach envelope.
   - Pruning filters:
     - Vertical altitude filter: Prunes pairs where `|Alt_A - Alt_B| > Vert_Threshold`.
     - Y-trajectory reach filter: Prunes pairs whose Y-intervals over time [0, T] do not overlap.
   - Surviving candidate pairs are evaluated for exact 3D closest approach!
"""
        self._add_markdown_label(scroll, content)

    def _build_tab2_math(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        content = """
### Kinematic Relative-Motion Equations

For two aircraft A and B with initial positions P_A, P_B and velocities V_A, V_B:

1. **Relative Position Vector:**
   r = P_B - P_A = (X_B - X_A, Y_B - Y_A)

2. **Relative Velocity Vector:**
   v = V_B - V_A = (Vx_B - Vx_A, Vy_B - Vy_A)

3. **Time of Minimum Separation (Closest Approach):**
   The squared distance between A and B at time t is:
   D(t)^2 = ||r + v * t||^2 = (r + v * t) · (r + v * t) = r·r + 2(r·v)t + (v·v)t^2

   To minimize D(t)^2, we set the derivative with respect to t to zero:
   d/dt [D(t)^2] = 2(r · v) + 2(v · v)t = 0
   ==> t_raw = - (r · v) / (v · v)

4. **Zero-Relative-Velocity & Horizon Clamping:**
   - If (v · v) < 1e-12 (parallel flight or identical velocities):
     The distance remains constant over time. Therefore, t_closest = 0.
   - Otherwise, clamp t_raw to the prediction horizon [0, T]:
     t_closest = max(0, min(t_raw, T))

5. **Predicted Horizontal Separation:**
   d_horiz = ||r + v * t_closest|| = sqrt((r_x + v_x * t_closest)^2 + (r_y + v_y * t_closest)^2)

6. **Predicted Vertical Separation:**
   d_vert = |Altitude_B - Altitude_A|

7. **Educational Threat Classification:**
   - **HIGH THREAT:** d_horiz <= 0.5 km (500m) AND d_vert <= 0.15 km (150m)
   - **MEDIUM THREAT:** d_horiz <= 1.5 km (1500m) AND d_vert <= 0.30 km (300m)
   - **LOW THREAT:** d_horiz <= 3.0 km (3000m) AND d_vert <= 0.50 km (500m)
   - **SAFE:** Otherwise.
"""
        self._add_markdown_label(scroll, content)

    def _build_tab3_complexity(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        content = """
### Rigorous Asymptotic Complexity Analysis

#### 1. Spatial Recurrence Relation
The algorithm divides N aircraft into two equal halves of size N/2 and combines them:
`T(N) = 2 * T(N/2) + f(N)`
where `f(N)` is the cost of the combine step (strip candidate comparison).

#### 2. Best-Case Time Complexity: Ω(N log N)
- **Scenario:** Aircraft are spatially sparse and well-separated across sectors.
- **Analysis:** Very few aircraft reach across the median split line (`|Strip| = O(1)`).
- `f(N) = O(1)` or `O(N)`.
- By Master Theorem (Case 2): `T(N) = 2T(N/2) + O(N) ==> Θ(N log N)`.

#### 3. Average-Case Time Complexity: O(N log N)
- **Scenario:** Realistic operational air traffic with standard corridor distributions.
- **Analysis:** Due to 2D trajectory reach filtering and altitude separation, the number of candidate pairs across the boundary strip is bounded by `c * N`.
- Combining takes linear time `O(N)`.
- Initial sorting takes `O(N log N)`.
- Total Average Time = `O(N log N)`.

#### 4. Worst-Case Time Complexity: O(N^2)
- **Scenario:** All N aircraft are clustered near the center line moving towards each other.
- **Analysis:** In this adversarial scenario, both Strip_L and Strip_R contain N/2 aircraft with overlapping trajectories.
- The combine step checks `(N/2) * (N/2) = O(N^2)` candidate pairs.
- Total Worst-Case Time = `O(N^2)`.
- *Note:* This matches the theoretical worst-case of 2D closest-pair when all points fall within the boundary strip.

#### 5. Auxiliary Space Complexity: O(N)
- Array of N sorted aircraft: `O(N)`.
- Strip candidate lists: `O(N)`.
- Tracer execution history: `O(N log N)` when recording step-by-step history.
- Recursion Call Stack: Depth is `log2(N)`. Stack frame usage = `O(log N)`.
"""
        self._add_markdown_label(scroll, content)

    def _build_tab4_viva(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        content = """
### Viva Voce Q&A Cheat Sheet (B.Tech CSE / Cybersecurity)

**Q1: Why use Divide and Conquer instead of checking all pairs?**
*Answer:* A naive brute-force algorithm checks all C(N, 2) = N(N-1)/2 pairs, which is strictly O(N^2) for all inputs. Divide and Conquer reduces the average comparisons to O(N log N) by pruning spatially separated aircraft that cannot possibly collide.

**Q2: What is the most critical step in this algorithm?**
*Answer:* The Combine Step. If we only checked aircraft within their recursive halves, any two aircraft heading towards each other across the dividing line would be completely missed (false negative). AirGuard constructs a dynamic trajectory reach strip to ensure 100% recall of cross-boundary threats.

**Q3: How do you prevent division by zero in relative motion calculations?**
*Answer:* When two aircraft fly with identical velocities (Vx_A = Vx_B and Vy_A = Vy_B), their relative velocity squared `v · v = 0`. AirGuard explicitly checks `v · v < 1e-12` and sets `t_closest = 0.0`, measuring their constant current separation.

**Q4: How does 3D collision detection differ from 2D closest pair?**
*Answer:* In standard 2D closest pair, points are static. In air traffic, aircraft move over time horizon T. AirGuard computes temporal reach intervals [X(0), X(T)] and performs kinematic quadratic minimization to find the exact instant t in [0, T] of minimum horizontal separation, coupled with vertical flight level separation.

**Q5: Is this system certified for real ATC operations?**
*Answer:* No. AirGuard is an educational simulation built for Design and Analysis of Algorithms (DAA). Certified ATC systems (like TCAS II / ACAS X) incorporate sensor uncertainty, turn dynamics, wind vectors, pilot reaction time, and Resolution Advisories (RA).
"""
        self._add_markdown_label(scroll, content)

    def _add_markdown_label(self, parent, text: str):
        lbl = ctk.CTkLabel(
            parent, text=text.strip(), font=FONT_BODY,
            text_color=COLOR_TEXT_PRIMARY, justify="left", wraplength=820
        )
        lbl.pack(anchor="w", padx=10, pady=5)
