# AirGuard — Divide & Conquer Air Traffic Collision Threat Detector

> **Design and Analysis of Algorithms (DAA) — Assignment 2**  
> *Academic Simulation & Interactive Algorithmic Radar Dashboard*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-00E5FF.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Visualization](https://img.shields.io/badge/Engine-Matplotlib-orange.svg)](https://matplotlib.org/)
[![Status](https://img.shields.io/badge/Tests-28%2F28%20Passing-brightgreen.svg)]()

---

> ⚠️ **EDUCATIONAL SIMULATION NOTICE**  
> **AirGuard** is an educational simulation developed solely for the academic study of **Divide and Conquer spatial partitioning algorithms**. It is **not** certified for real-world aviation safety by the FAA, ICAO, DGCA, or any civil aviation authority. It does not interface with actual aircraft transponders (ADS-B) or air traffic control systems.

---

## 1. Project Overview

AirGuard simulates an en-route Air Traffic Control (ATC) sector where aircraft move continuously in 3D airspace. Rather than utilizing an exhaustive $O(n^2)$ all-pairs distance check, AirGuard implements a **Spatial Divide and Conquer algorithm** that partitions the airspace, solves subregions recursively, and rigorously inspects a dynamic **cross-boundary trajectory reach strip** to detect impending loss of separation within a configurable prediction horizon $T$.

### Key Capabilities:
- ✈ **True Divide & Conquer Spatial Partitioning:** Recursively divides aircraft along the median $X$-coordinate with base cases ($n \le 3$).
- 🛡 **Cross-Boundary Trajectory Reach Envelopes:** Mathematically prevents false negatives across partition boundaries by computing spatial reach intervals $[x_i + \min(0, v_{xi}T), x_i + \max(0, v_{xi}T)]$ with 3D safety buffers.
- 📐 **Kinematic Relative Motion Equations:** Computes analytical minimum separation time $t_{\text{closest}}$ via quadratic derivative minimization, with safe zero-relative-velocity handling.
- 🎛 **Interactive Step-by-Step Execution Replay:** Real backwards and forwards state replay (`Next Step`, `Prev Step`, `Pause`, `Run to End`, `Reset`) with active partition lines, candidate strips, and evaluating pair visual highlights.
- 🌌 **High-Aesthetics Dark Radar Dashboard:** Deep cockpit navy palette, range rings (10–50 km), heading rose, velocity vector arrows, dotted trajectory extrapolations, and threat-coded connecting lines.
- 📑 **Assignment Report Generator:** Generates an assignment HTML report containing student credentials, scenario telemetry, complexity analysis, embedded live radar visual, and automated unit test pass/fail metrics.
- 🎓 **In-App Viva Voce Guide & Theory Modal:** Accessible cheat sheet for explaining algorithms, recurrences, and Master Theorem to examiners.

---

## 2. Project File Structure

```text
airguard/
├── main.py                     # Primary GUI application entry point
├── requirements.txt            # Python dependencies (customtkinter, matplotlib, numpy, pillow)
├── run.bat                     # Simple Windows one-click launcher
├── README.md                   # Complete architectural, theoretical, and user documentation
│
├── models/
│   ├── __init__.py
│   ├── aircraft.py             # Aircraft model, validation, and kinematic extrapolation
│   ├── conflict.py             # ConflictPair, ThreatLevel enums, and ThresholdConfig
│   └── scenarios.py            # 4 demonstration presets + reproducible random generator
│
├── algorithms/
│   ├── __init__.py
│   ├── closest_approach.py     # Analytical relative motion and closest approach equations
│   ├── brute_force.py          # O(n^2) exhaustive reference algorithm for ground-truth validation
│   ├── divide_and_conquer.py   # Spatial Divide & Conquer algorithm with strip reach search
│   └── state_tracer.py         # Step snapshot manager for interactive visual replay
│
├── visualization/
│   ├── __init__.py
│   └── radar_canvas.py         # Matplotlib-Tkinter interactive circular radar display
│
├── ui/
│   ├── __init__.py
│   ├── app.py                  # Main window coordinator and event orchestrator
│   ├── header.py               # Top branding, status badges, and action buttons
│   ├── sidebar_controls.py     # Aircraft form, scenario selector, random generator, horizon slider
│   ├── sidebar_threats.py      # Telemetry cards, ranked conflict table, and details inspector
│   ├── playback_panel.py       # Replay controls, speed slider, progress bar, and phase badges
│   ├── educational_dialog.py   # Theory modal, Master Theorem proofs, and Viva Q&A guide
│   ├── report_dialog.py        # Student details form and HTML report exporter
│   └── theme.py                # Visual styling tokens, dark palette, and typography
│
├── reports/
│   ├── __init__.py
│   └── report_generator.py     # HTML report compiler with base64 embedded radar screenshots
│
└── tests/
    ├── __init__.py
    ├── test_algorithm.py       # Cross-boundary tests, scenarios, and brute-force equivalence
    ├── test_closest_approach.py# Analytical math, zero-velocity, and altitude edge cases
    ├── test_validation.py      # Dataset validation, duplicate IDs, and coordinate bounds
    └── test_gui_smoke.py       # Lifecycle smoke test, step replay, and report generation
```

---

## 3. Installation & Execution

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed on Windows.
- Standard libraries: `math`, `typing`, `dataclasses`, `unittest`.

### Installation Steps

1. **Clone or Navigate to the Directory:**
   ```powershell
   cd C:\Users\ASUS\.gemini\airguard
   ```

2. **Install Dependencies:**
   ```powershell
   py -3.13 -m pip install -r requirements.txt
   ```
   *(or `pip install -r requirements.txt`)*

3. **Launch AirGuard:**
   ```powershell
   py -3.13 main.py
   ```
   *Alternatively, double-click `run.bat` on Windows.*

4. **Run the Automated Test Suite:**
   ```powershell
   py -3.13 -m unittest discover -s tests -p "test_*.py"
   ```

---

## 4. Algorithmic Foundation: Spatial Divide and Conquer

### 4.1 Kinematic Relative Motion & Separation Math

Given two aircraft $A$ and $B$:
- Initial Positions: $\vec{P}_A = (x_A, y_A)$, $\vec{P}_B = (x_B, y_B)$
- Velocities: $\vec{V}_A = (v_{xA}, v_{yA})$, $\vec{V}_B = (v_{xB}, v_{yB})$
- Relative Position Vector: $\vec{r} = \vec{P}_B - \vec{P}_A = (x_B - x_A, y_B - y_A)$
- Relative Velocity Vector: $\vec{v} = \vec{V}_B - \vec{V}_A = (v_{xB} - v_{xA}, v_{yB} - v_{yA})$

The squared horizontal separation as a function of time $t$ is:
$$D(t)^2 = \|\vec{r} + \vec{v}t\|^2 = \vec{r}\cdot\vec{r} + 2(\vec{r}\cdot\vec{v})t + (\vec{v}\cdot\vec{v})t^2$$

To find the time of closest approach, we differentiate with respect to $t$ and set the derivative to zero:
$$\frac{d}{dt}[D(t)^2] = 2(\vec{r}\cdot\vec{v}) + 2(\vec{v}\cdot\vec{v})t = 0 \implies t_{\text{raw}} = -\frac{\vec{r}\cdot\vec{v}}{\vec{v}\cdot\vec{v}}$$

#### Edge Case Handling:
1. **Zero Relative Velocity ($\vec{v}\cdot\vec{v} < 10^{-12}$):**  
   If both aircraft fly with identical headings and speeds, their relative distance remains constant. Division by zero is prevented by setting $t_{\text{closest}} = 0.0$.
2. **Prediction Horizon Clamping:**  
   If the instant of closest approach lies in the past ($t < 0$) or beyond the horizon ($t > T$), it is clamped:
   $$t_{\text{closest}} = \max(0, \min(t_{\text{raw}}, T))$$
3. **Minimum Predicted Separation:**
   $$d_{\text{horiz}} = \|\vec{r} + \vec{v} \cdot t_{\text{closest}}\|, \quad d_{\text{vert}} = |h_B - h_A|$$

---

### 4.2 Threat Level Classification (Educational Thresholds)

- **HIGH THREAT (Red):** $d_{\text{horiz}} \le 0.50\text{ km}$ ($500\text{ m}$) AND $d_{\text{vert}} \le 0.15\text{ km}$ ($150\text{ m}$)
- **MEDIUM THREAT (Amber):** $d_{\text{horiz}} \le 1.50\text{ km}$ ($1500\text{ m}$) AND $d_{\text{vert}} \le 0.30\text{ km}$ ($300\text{ m}$)
- **LOW THREAT (Cyan):** $d_{\text{horiz}} \le 3.00\text{ km}$ ($3000\text{ m}$) AND $d_{\text{vert}} \le 0.50\text{ km}$ ($500\text{ m}$)
- **SAFE (Green):** Separation remains above warning thresholds throughout horizon $T$.

---

### 4.3 Spatial Divide & Conquer Pipeline

1. **Input Validation:** Enforces non-empty unique callsigns, valid finite coordinates, non-negative altitudes, and non-empty datasets.
2. **Sorting:** Sorts $N$ aircraft by their $X$ coordinate in $O(N \log N)$ time.
3. **Base Case:** When $|P_{\text{sub}}| \le 3$, evaluates all pairs directly without further recursion.
4. **Divide Step:** Computes median index $m = |P_{\text{sub}}| // 2$. The spatial dividing line is:
   $$x_{\text{mid}} = \frac{P_{\text{sub}}[m-1].x + P_{\text{sub}}[m].x}{2}$$
   Partitions into $P_{\text{left}}$ and $P_{\text{right}}$.
5. **Conquer:** Recursively solves $P_{\text{left}}$ and $P_{\text{right}}$.
6. **Combine Step (Cross-Boundary Correctness):**
   - Computes the spatial reach envelope along $X$ for both partitions over time $[0, T]$:
     $$\text{LeftReach}_X = \left[ \min_{A \in \text{Left}} \min_{t} x_A(t), \max_{A \in \text{Left}} \max_{t} x_A(t) \right]$$
     $$\text{RightReach}_X = \left[ \min_{B \in \text{Right}} \min_{t} x_B(t), \max_{B \in \text{Right}} \max_{t} x_B(t) \right]$$
   - Candidate Left aircraft $\text{Strip}_L$: Left aircraft that can reach within $D_{\max}$ of $\text{RightReach}_X$.
   - Candidate Right aircraft $\text{Strip}_R$: Right aircraft that can reach within $D_{\max}$ of $\text{LeftReach}_X$.
   - **Pruning Filters:**
     1. Vertical altitude difference: $|h_A - h_B| \le H_{\max}$
     2. $Y$-trajectory reach overlap test: Overlap of $Y$-intervals over $[0, T]$ with safety buffer $D_{\max}$.
   - Surviving candidate pairs are evaluated for exact 3D closest approach.
7. **Ranking:** Deduplicates and sorts conflict pairs by severity (`HIGH` > `MEDIUM` > `LOW`), earliest $t_{\text{closest}}$, and minimum horizontal separation.

---

## 5. Verified Complexity Analysis

| Metric | Complexity | Mathematical Justification |
| :--- | :---: | :--- |
| **Best-Case Time** | $\Omega(N \log N)$ | Sparse airspace; boundary strip contains $O(1)$ aircraft. $T(N) = 2T(N/2) + O(1) \implies \Omega(N \log N)$. |
| **Average-Case Time**| $O(N \log N)$ | Realistic operational air traffic; spatial pruning bounds cross-boundary checks to $O(N)$. $T(N) = 2T(N/2) + O(N) \implies O(N \log N)$ via Master Theorem Case 2. |
| **Worst-Case Time** | $O(N^2)$ | Pathological traffic: all $N$ aircraft converge into the central dividing strip, yielding $(N/2) \times (N/2)$ pair checks. |
| **Auxiliary Space** | $O(N)$ | $O(N)$ for sorted arrays and candidate buffers; $O(\log N)$ maximum recursive call stack depth. |

---

## 6. Demonstration Scenarios

1. **1. SAFE AIRSPACE:** 5 aircraft on parallel, non-conflicting corridors. Demonstrates zero false positives.
2. **2. HEAD-ON APPROACH:** Two aircraft on reciprocal headings at FL328 (10.0 km). Produces a textbook `HIGH` threat collision alert at $t = 50.0\text{s}$ with $0\text{ m}$ separation.
3. **3. CROSSING TRAFFIC:** Orthogonal flight paths intersecting at origin $(0, 0)$ at $t = 50.0\text{s}$.
4. **4. MULTIPLE CONFLICTS (CROSS-BOUNDARY):** 8 aircraft containing internal subproblem conflicts and a **cross-boundary pair** (`QR-555` on Left, `CX-666` on Right) that cross the median bisection line $X = 0\text{ km}$ to collide at $t = 26.7\text{s}$.
5. **RANDOM TRAFFIC GENERATOR:** Generates $N$ aircraft (configurable from 2 to 40) using a fixed random seed (default 42) for 100% reproducible testing.

---

## 7. Automated Test Suite

AirGuard includes **28 automated unit and smoke tests** covering all rubric criteria:

| Test File | Test Cases Covered |
| :--- | :--- |
| `test_closest_approach.py` | Head-on collision, diverging flights, crossing paths, zero relative velocity (parallel far/close), altitude separation, prediction horizon $= 0$. |
| `test_validation.py` | Valid aircraft creation, negative coordinates, empty/whitespace IDs, negative altitudes, non-numeric input, NaN handling, duplicate IDs. |
| `test_algorithm.py` | Empty aircraft list, single aircraft, cross-boundary divide collision, 4 preset scenarios, fixed-seed repeatability, and **exhaustive brute-force cross-validation across multiple seeds** (verifying 100% recall). |
| `test_gui_smoke.py` | GUI lifecycle, scenario switching, step-by-step backwards/forwards replay, and HTML report generation. |

Execute all tests:
```powershell
py -3.13 -m unittest discover -s tests -p "test_*.py"
```

---

## 8. Viva Voce Preparation Guide (For B.Tech CSE / Cybersecurity)

### Q1: Why is Divide and Conquer chosen over Brute Force?
> **Answer:** Brute force checks all $\binom{N}{2} = \frac{N(N-1)}{2}$ pairs, which is strictly $\Theta(N^2)$ regardless of aircraft distribution. Divide and Conquer exploits spatial locality: aircraft separated by large distances cannot collide within lookahead horizon $T$. Spatial bisection reduces average comparisons to $O(N \log N)$.

### Q2: What is the most common pitfall when applying Divide and Conquer to moving objects?
> **Answer:** In static 2D closest pair, points do not move, so the strip width is simply $\delta = \min(\delta_L, \delta_R)$. For aircraft with velocity $\vec{V}$, an aircraft in the left partition can fly across the dividing line and collide with an aircraft in the right partition. AirGuard resolves this by computing dynamic **trajectory reach intervals** $[x_i + \min(0, v_{xi}T), x_i + \max(0, v_{xi}T)]$ with threat buffer $D_{\max}$ to ensure zero missed collisions (100% recall).

### Q3: How is division by zero avoided in relative velocity calculations?
> **Answer:** When two aircraft fly with identical velocity vectors ($\vec{v} = 0$), $\vec{v}\cdot\vec{v} = 0$. The implementation checks `v_dot_v < 1e-12` and sets $t_{\text{closest}} = 0.0$, evaluating their constant existing separation.

### Q4: What is the Master Theorem recurrence for this algorithm?
> **Answer:** The recurrence is $T(N) = 2T(N/2) + f(N)$, where $a=2$, $b=2$, and $\log_b a = \log_2 2 = 1$. In average-case traffic where cross-boundary candidates are bounded by linear density, $f(N) = O(N) = O(N^1)$. By Master Theorem Case 2, $T(N) = \Theta(N \log N)$.

### Q5: How is this relevant to Cybersecurity?
> **Answer:** Modern NextGen ATC relies on ADS-B and digital datalinks which are vulnerable to spoofing, ghost aircraft injection, and denial-of-service attacks. Algorithmic efficiency is critical: an $O(N^2)$ detector can be subjected to algorithmic complexity attacks (traffic flooding) causing ATC display freezes. An $O(N \log N)$ algorithm with strict input validation provides resilience against algorithmic denial of service.

---

## 9. Assignment Report Generation

1. In the application header, click **"📄 Generate Report"**.
2. Enter your academic details (Student Name, Roll Number, Department, Course, Institution).
3. Click **"Generate & Open Report"**.
4. The system produces a complete, professional report (`reports_output/AirGuard_Assignment2_Report.html`) containing:
   - Full student metadata and problem definition
   - Exact mathematical equations and pseudocode
   - Complexity proofs and Master Theorem justification
   - Embedded high-resolution base64 PNG screenshot of the active radar canvas
   - Current scenario aircraft telemetry and ranked collision table
   - Automated test suite pass/fail audit
   - One-click **"🖨 Print to PDF"** button formatted with clean print CSS
