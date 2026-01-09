# Experiment Design: The Object as the Unit for State Switching in VWM

## 1. Experiment Overview & Rationale

**Core Question:**
Visual Working Memory (VWM) is thought to have distinct states: an **Active State** (focus of attention, guides behavior) and a **Passive State** (latent, waiting for recall).  
> "representations in VWM can exist in two functionally distinct states."  
> "The highly active representations are held in the focus of attention"  
> "latent representations are retained in a lower privileged state" (paper/paper.md, Introduction)
Key Question: Is the "unit" of this state switching an individual **Feature** (e.g., just the color) or the entire **Object**?  
> "unit for switching representational states in visual working memory (VWM)." (paper/paper.md, Abstract)

**Hypotheses:**
*   **Feature-Based Hypothesis:** Features within the same object can be in different states (e.g., Color is Active, Shape is Passive).  
    > "unit of switching being a feature (feature-based hypothesis)." (paper/paper.md, Abstract)
*   **Object-Based Hypothesis:** All features of one object must be in the same state (if Color is Active, Shape must also be Active).  
    > "unit of switching being an object (object-based hypothesis)." (paper/paper.md, Abstract)

**Experimental Logic:**
Using the **Memory-Driven Attentional Capture** paradigm:
1.  **Memory:** Participants memorize two features (e.g., Color & Shape).
2.  **Cue:** A retro-cue tells them which feature will be tested *first* (making that feature **Active**). The other becomes **Passive** (temporarily).
3.  **Search (Capture):** Participants search for a target. Crucially, a **Distractor** appears that matches either the "Active" feature (Related First) or the "Passive" feature (Related Second).
    *   If the Distractor captures attention (slows RT), that feature is **Active**.
    *   If it doesn't capture attention, that feature is **Passive**.
    > "Participants (N = 180) were instructed to hold two features from either one or two objects in their VWM."  
    > "memory-driven attentional capture effect"  
    > "actively held information in VWM can cause attention to be drawn towards matched distractors."  
    > "one of the memory features (shape or color) was cued"  
    > "indicating which feature would be probed first." (paper/paper.md, Abstract; Methods/Experiment 1 procedure; Fig. 1)

**Critical Comparison:**
*   **Separate Group:** Features belong to two *different* objects. (Baseline: Expect only "First" to be active).
*   **Integrated Group:** Features belong to the *same* object.
    *   If **Feature-based**, only "First" should capture attention.
    *   If **Object-based**, **BOTH** "First" and "Second" should capture attention (because activating one part of the object activates the whole).
    > "only the feature indicated to be probed first could elicit memory related capture"  
    > "features from an integrated object could guide attention regardless of the probe order." (paper/paper.md, Abstract)

### Experiment Flowcharts

```mermaid
graph TD
    subgraph Experiment 1: Color-Shape Binding
    A1[Start Trial] --> B1[Memory Display<br/>800ms]
    B1 --> C1{Group?}
    C1 -- Integrated --> D1[One Colored Shape<br/>(e.g., Red Triangle)]
    C1 -- Separate --> D2[Black Shape + Colored Circle<br/>(e.g., Black Triangle + Red Circle)]
    D1 --> E1[Delay 180ms]
    D2 --> E1
    E1 --> F1[Retro-Cue<br/>500ms<br/>'Color' or 'Shape']
    F1 --> G1[Delay 500ms]
    G1 --> H1[Visual Search Task<br/>Targets: Tilted Line<br/>Distractor: Color Singleton]
    H1 --> I1[Probe 1<br/>(Cued Feature)]
    I1 --> J1[Probe 2<br/>(Uncued Feature)]
    end
```
Source: paper/paper.md, Fig. 1.

```mermaid
graph TD
    subgraph Experiment 2: Same-Dimension (Color-Color)
    A2[Start Trial] --> B2[Memory Display<br/>800ms]
    B2 --> C2{Group?}
    C2 -- Integrated --> D2a[One Bicolor Circle<br/>(Top-Red / Bottom-Blue)]
    C2 -- Separate --> D2b[Two Semicircles<br/>(Left-Red / Right-Blue)]
    D2a --> E2[Delay]
    D2b --> E2
    E2 --> F2[Retro-Cue<br/>500ms<br/>'Up' or 'Down']
    F2 --> G2[Delay]
    G2 --> H2[Visual Search Task<br/>Distractor: Color Singleton]
    H2 --> I2[Probe 1]
    I2 --> J2[Probe 2]
    end
```
Source: paper/paper.md, Fig. 3.

```mermaid
graph TD
    subgraph Experiment 3: Gestalt Object
    A3[Start Trial] --> B3[Memory Display<br/>800ms]
    B3 --> C3{Group?}
    C3 -- Integrated --> D3a[Kanizsa-like Closure<br/>(Virtually One Rectangle)]
    C3 -- Separate --> D3b[Rotated Pacmen<br/>(Closure Broken)]
    D3a --> E3[Delay]
    D3b --> E3
    E3 --> F3[Retro-Cue<br/>'Up' or 'Down']
    F3 --> G3[Delay]
    G3 --> H3[Search Task]
    H3 --> I3[Probe 1]
    I3 --> J3[Probe 2]
    end
```
Source: paper/paper.md, Fig. 5.

---


## 2. Rigorous Geometric Definitions of Stimuli

**Coordinate System & Conventions**:
*   Coordinates $(x, y)$ are in **visual degrees ($^\circ$)** relative to screen center $(0,0)$.  
    > "centered on the center of the screen."  
    > "colored shape (4.2◦ × 4.2◦)." (paper/paper.md, Methods/Experiment 1 Stimuli)
*   **Rotation**: $0^\circ$ corresponds to East (Positive X-axis). Positive rotation is **Counter-Clockwise (CCW)**.  
    > "line tilted at 45◦ (either left or right)." (paper/paper.md, Methods/Experiment 1 Stimuli)  
    Note: axis orientation (0°=East, CCW positive) is an implementation convention (not explicitly specified in paper/README).
*   **Indices**: Colors $\{C_1..C_5\}$ (Red, Green, Magenta, Yellow, Blue); Shapes $\{S_1..S_5\}$ (Square, Triangle, Diamond, Hexagon, Trapezoid).  
    > "value 1 to 5 represent red, green, purple, yellow and blue"  
    > "value 1 to 5 represent square, triangle, diamond, hexagon and trapezoid" (data/README.md)

### 2.1 Constants & Parameters Definition
Key geometric parameters mapped to configuration keys.  
> "As depicted in Fig. 1" (paper/paper.md, Methods/Experiment 1 Stimuli)  
> "As depicted in Fig. 3" (paper/paper.md, Methods/Experiment 2)  
> "As shown in Fig. 5" (paper/paper.md, Methods/Experiment 3)

| Symbol | Config Key | Value | Description / Source |
| :--- | :--- | :--- | :--- |
| **Canvas** | | | Specified in `[canvas]` section. |
| $S_{diag}$ | `screen_size` | 17.0 in | Screen diagonal size. > "17-in. CRT monitor (100 Hz, 1024 × 768 screen resolution)." (paper/paper.md, Methods/Experiment 1 Apparatus) |
| $R_{screen}$ | `screen_resolution` | (1024, 768) | Screen resolution (width, height) in px. > "1024 × 768 screen resolution." (paper/paper.md, Methods/Experiment 1 Apparatus) |
| $D_{view}$ | `screen_distance` | 50.0 cm | Viewing distance from screen. > "viewing distance of approximately 50 cm." (paper/paper.md, Methods/Experiment 1 Apparatus) |
| $W_{canvas}$ | *(computed)* | $\approx 13.6$ in | Screen width. Derived from $S_{diag}$ and $R_{screen}$. > "17-in. CRT monitor (100 Hz, 1024 × 768 screen resolution)." (paper/paper.md, Methods/Experiment 1 Apparatus) |
| $H_{canvas}$ | *(computed)* | $\approx 10.2$ in | Screen height. Derived from $S_{diag}$ and $R_{screen}$. > "17-in. CRT monitor (100 Hz, 1024 × 768 screen resolution)." (paper/paper.md, Methods/Experiment 1 Apparatus) |
| $C_{bg}$ | `bg_color` | "white" | Background color. > "background of the display was white (RGB: 255, 255, 255)." (paper/paper.md, Methods/Experiment 1 Apparatus) |
| $F_{out}$ | `output_format` | "svg" | Output image format. > "output_format = \"svg\"" (script/stimuli_config.toml) |
| **Search Task** | | | |
| $R_{search}$ | `radius` | $7.59^\circ$ | Radius of item centers. > "imaginary circle (radius = 7.59◦)." (paper/paper.md, Methods/Experiment 1 Stimuli) |
| $D_{item}$ | `item_size` | $2.94^\circ$ | Diameter of items. > "eight disks (2.94◦)" (paper/paper.md, Methods/Experiment 1 Stimuli) |
| $\theta_{tilt}$ | `tilt_pos/neg` | $\pm 45^\circ$ | Target line tilt relative to vertical. > "line tilted at 45◦ (either left or right)." (paper/paper.md, Methods/Experiment 1 Stimuli) |
| $C_{base}$ | `base_color` | "0.75" | Gray distractor color. > "remaining disks were gray (RGB = 192, 192, 192)." (paper/paper.md, Methods/Experiment 1 Stimuli) |
| **Exp 1** | | | |
| $D_{mem}$ | `integrated_item_size` | $4.2^\circ$ | Diameter/Size of memory items. > "colored shape (4.2◦ × 4.2◦)." (paper/paper.md, Methods/Experiment 1 Stimuli; Fig. 1) |
| $D_{offset}$ | `separate_offset` | $4.2^\circ$ | Separation offset. Derived from half of "virtual rectangle (8.4◦ × 8.4◦)". (paper/paper.md, Methods/Experiment 1 Stimuli; Fig. 1) |
| **Exp 2** | | | |
| $R_{semi}$ | `integrated_item_size`/2 | $2.1^\circ$ | Radius of semicircles ($D_{mem}/2$). > "two differently colored semicircles (radius =  2.1◦)." (paper/paper.md, Methods/Experiment 2; Fig. 3) |
| $O_{exp2}$ | `separate_left_x/y` | $2.1^\circ$ | Eccentricity offset (symmetric). Derived from radius and Fig. 3 layout. > "memory items were two separated colored semicircles." (paper/paper.md, Methods/Experiment 2) |
| $\theta_{L}^{sep}$ | `separate_left_orientation` | "bottom" | Left semicircle curved side orientation ($180^\circ$-$360^\circ$). Inferred from Fig. 3 diagram. > "memory items were two separated colored semicircles." (paper/paper.md, Methods/Experiment 2; Fig. 3) |
| $\theta_{R}^{sep}$ | `separate_right_orientation` | "top" | Right semicircle curved side orientation ($0^\circ$-$180^\circ$). Inferred from Fig. 3 diagram. > "memory items were two separated colored semicircles." (paper/paper.md, Methods/Experiment 2; Fig. 3) |
| **Exp 3** | | | |
| $R_{notch}$ | `radius` | $2.1^\circ$ | Radius of notched circles. Inferred from Fig. 5 scale; not explicitly stated in text. > "As shown in Fig. 5" (paper/paper.md, Methods/Experiment 3) |
| $L_{notch}$ | `notch_side` | $2.0$ | Side length of square notch (unitless scalar in config). Inferred from Fig. 5; not explicit in text. > "As shown in Fig. 5" (paper/paper.md, Methods/Experiment 3) |
| $O_{vert}$ | `vertical_offset` | $2.1^\circ$ | Vertical center offset. Inferred from Fig. 5; not explicit in text. > "As shown in Fig. 5" (paper/paper.md, Methods/Experiment 3) |
| $\theta_{top}^{int}$ | `integrated_top_angle` | $270^\circ$ | Top circle notch angle (Integrated). Inferred from Fig. 5 diagram; not explicit in text. > "As shown in Fig. 5" (paper/paper.md, Methods/Experiment 3) |
| $\theta_{bot}^{int}$ | `integrated_bottom_angle` | $90^\circ$ | Bottom circle notch angle (Integrated). Inferred from Fig. 5 diagram; not explicit in text. > "As shown in Fig. 5" (paper/paper.md, Methods/Experiment 3) |
| $\Delta\theta_{sep}$ | *(fixed)* | $\pm 90^\circ$ | Separate group: randomly rotate **one** component by ±90° from integrated angles. > "randomly rotate one of the components 90◦ to the left or right" (paper/paper.md, Methods/Experiment 3) |

### 2.2 Experiment 1: Color-Shape Binding
**Input Data**: `col1`$\in[1,5]$ (Color), `col2`$\in[1,5]$ (Shape).  
> "First and second column: the color (value 1 to 5 represent red, green, purple, yellow and blue)"  
> "and the shape (value 1 to 5 represent square, triangle, diamond, hexagon and trapezoid) of the memory display, respectively." (data/README.md)

#### Memory Display
*   **Integrated Group**:
    *   Single object at $(0,0)$.
    *   **Geometry**: Shape $S_{col2}$ fitting box $D_{mem} \times D_{mem}$.
    *   **Fill**: $C_{col1}$.
*   **Separate Group**:
    *   **Object 1 (Shape)** at $(-D_{offset}, D_{offset})$: Shape $S_{col2}$, Size $D_{mem}$, Color Black.
    *   **Object 2 (Color)** at $(D_{offset}, -D_{offset})$: Circle, Diameter $D_{mem}$, Color $C_{col1}$.
    > "memory display contained a colored shape (4.2◦ × 4.2◦)."  
    > "black shape (4.2◦ × 4.2◦) and a colored circle (4.2◦ × 4.2◦)."  
    > "upper left and lower right corners of a virtual rectangle (8.4◦ × 8.4◦)." (paper/paper.md, Methods/Experiment 1 Stimuli; Fig. 1)

### 2.3 Experiment 2: Same-Dimension (Color-Color)
**Input Data**: `col1`$\in[1,5]$ (Top Color), `col2`$\in[1,5]$ (Bottom Color).  
> "the first and second column represent the two colors in the memory display." (data/README.md)

#### Memory Display
*   **Integrated Group**:
    *   Composite Circle at $(0,0)$, Radius $R_{semi}$.
    *   **Top Half**: Wedge $\theta \in [0^\circ, 180^\circ)$, Fill $C_{col1}$.
    *   **Bottom Half**: Wedge $\theta \in [180^\circ, 360^\circ)$, Fill $C_{col2}$.
*   **Separate Group**:
    *   **Left Item** at $(-O_{exp2}, O_{exp2})$: Semicircle ($R_{semi}$), Fill $C_{col1}$. Orientation $\theta_{L}^{sep}$ ("bottom") implies Flat Side Up, Arc Down ($\theta \in [180^\circ, 360^\circ]$ relative to item center).
    *   **Right Item** at $(O_{exp2}, -O_{exp2})$: Semicircle ($R_{semi}$), Fill $C_{col2}$. Orientation $\theta_{R}^{sep}$ ("top") implies Flat Side Down, Arc Up ($\theta \in [0^\circ, 180^\circ]$ relative to item center).
    > "memory display was a circle composed of two differently colored semicircles (radius =  2.1◦)."  
    > "memory items were two separated colored semicircles." (paper/paper.md, Methods/Experiment 2; Fig. 3)

### 2.4 Experiment 3: Gestalt (Notched Circles)
**Input Data**: `col1` (Top), `col2` (Bottom).  
> "the first and second column represent the two colors in the memory display." (data/README.md)

#### Memory Display
*   Two circles, Radius $R_{notch}$, Square Notch $L_{notch}$. Notch rotation defined by angle $\phi$ (CCW from East).
*   **Top Object** at $(0, O_{vert})$:
    *   Fill $C_{col1}$.
    *   **Integrated**: Notch $\phi = \theta_{top}^{int}$ ($270^\circ$/South $\rightarrow$ Facing Center).
*   **Bottom Object** at $(0, -O_{vert})$:
    *   Fill $C_{col2}$.
    *   **Integrated**: Notch $\phi = \theta_{bot}^{int}$ ($90^\circ$/North $\rightarrow$ Facing Center $\rightarrow$ **Closure**).
*   **Separate Group Rotation Rule**:
    *   Randomly choose **one** component (top or bottom) and rotate its notch by $\pm 90^\circ$ (CCW or CW) relative to the integrated angle to break closure.
    > "two colors were integrated by Gestalt principles (integrated group)"  
    > "randomly rotate one of the components 90◦ to the left or right as separate group." (paper/paper.md, Methods/Experiment 3; Fig. 5)

### 2.5 Search Display (Common to All)
**Input Data**: `dist_cond`, `target_orient`, `cue_val` (for Exp2/3).

*   **Layout**: 8 Items centers $P_k = (R_{search} \cos(k \frac{\pi}{4}), R_{search} \sin(k \frac{\pi}{4}))$, $k=0..7$.
    > "eight disks (2.94◦) equally distributed on an imaginary circle (radius = 7.59◦)." (paper/paper.md, Methods/Experiment 1 Stimuli; Fig. 1)

*   **Singleton Determination**:
    > "In 3/4 of the trials, the search display featured a color singleton distractor." (paper/paper.md, Methods/Experiment 1 Procedure)
    
    **Experiment 1 (Color-Shape):**
    *   `dist_cond == 1` OR `dist_cond == 2` $\implies$ Color Singleton matching $C_{col1}$ (Both values are **equivalent** per `data/README.md`: "value 1 and 2 represent the color of the distractor match the color in the memory display").
    *   `dist_cond == 3` (Unrelated) $\implies$ $C_{new} \notin \{C_{col1}\}$.
    *   `dist_cond == 4` (No Singleton) $\implies$ All items gray.
    > "Third column: the condition of distractor in the search task." (data/README.md)
    
    **Experiment 2 \& 3 (Color-Color):**
    *   `dist_cond` encodes **probe order** ("first" vs "second"), **NOT** direct color mapping.
    *   To determine the matched color, **combine** `dist_cond` with `cue_val`:
        *   `cue_val == 1` (Upper/col1 tested first):
            *   `dist_cond == 1` (Related First) $\implies$ Match $C_{col1}$
            *   `dist_cond == 2` (Related Second) $\implies$ Match $C_{col2}$
        *   `cue_val == 2` (Lower/col2 tested first):
            *   `dist_cond == 1` (Related First) $\implies$ Match $C_{col2}$
            *   `dist_cond == 2` (Related Second) $\implies$ Match $C_{col1}$
        *   `dist_cond == 3` (Unrelated) $\implies$ $C_{new} \notin \{C_{col1}, C_{col2}\}$.
        *   `dist_cond == 4` (No Singleton) $\implies$ All items gray.
    > "value 1 to 4 represent related first probe condition, related second probe condition color, unrelated condition, and no-singleton condition, respectively." (data/README.md)

*   **Rendering**:
    *   **Target** ($k_{target}$): Gray Circle ($D_{item}$) + Black Line ($\theta_{tilt}$ relative to vertical).
    *   **Singleton** ($k_{singleton}$): Circle ($D_{item}$), Fill $C_{match}$ (determined above).
    *   **Distractors**: Gray Circle ($D_{item}$) + Black Cross.
    > "single line tilted at 45◦ (either left or right)."  
    > "remaining disks were gray (RGB = 192, 192, 192)." (paper/paper.md, Methods/Experiment 1 Stimuli; Fig. 1)




---

## 4. Data Structure (`.mat` Files)

The raw data follows a consistent column structure across experiments, but the semantic meaning of columns 1, 2, and 3 changes by experiment.

**Common Columns (Indices 1-based in Paper, 0-based in Python):**  
> "The structure of the behavior raw data file on each experiment:" (data/README.md)

| Col Index | Name | Meaning | Values |
| :--- | :--- | :--- | :--- |
| **3** | `dist_cond` | **Distractor Condition** | **See experiment-specific tables below**. > "Third column: the condition of distractor in the search task." (data/README.md) |
| **4** | `target_orient`| **Target Line Tilt** | **1** = Left (-45°)<br>**2** = Right (+45°). > "Fourth column: the orientation of the target line, value 1 to 2 represent left and right." (data/README.md) |
| **5** | `cue_val` | **Retro-Cue** | **Exp 1:** 1=Color First, 2=Shape First<br>**Exp 2/3:** 1=Up/Upper First, 2=Down/Lower First. > "Fifth column: the retro cue, value 1 to 2 represent color and shape." (data/README.md) |
| **6** | `probe_cond` | **Probe Match Type** | **1** = Only 1st Probe Matches Memory<br>**2** = Only 2nd Probe Matches Memory<br>**3** = Neither Match<br>**4** = Both Match. > "value 1 to 4 represent only first probe same, only second probe same, both different and both same." (data/README.md) |

**Experiment-Specific Columns (1, 2, 3):**  
> "The structure of data is identical to Experiment 1, except that the first and second column represent the two colors in the memory display" (data/README.md)

### Experiment 1 (Color-Shape Binding)
| Col Index | Name | Meaning | Values |
| :--- | :--- | :--- | :--- |
| **1** | `col1` | **Memory Color** | 1=Red, 2=Green, 3=Magenta, 4=Yellow, 5=Blue. > "First and second column: the color (value 1 to 5 represent red, green, purple, yellow and blue)" (data/README.md) |
| **2** | `col2` | **Memory Shape** | 1=Square, 2=Triangle, 3=Diamond, 4=Hexagon, 5=Trapezoid. > "and the shape (value 1 to 5 represent square, triangle, diamond, hexagon and trapezoid) of the memory display, respectively." (data/README.md) |
| **3** | `dist_cond` | **Distractor Condition** | **1** = Color Match (Singleton matches memory color)<br>**2** = Color Match (EQUIVALENT to 1, per `data/README.md`)<br>**3** = Unrelated Color Singleton<br>**4** = No Singleton. > "value 1 and 2 represent the color of the distractor match the color in the memory display." (data/README.md) |

### Experiment 2 & 3 (Color-Color Binding)
| Col Index | Name | Meaning | Values |
| :--- | :--- | :--- | :--- |
| **1** | `col1` | **Top/Upper Color** | 1=Red, 2=Green, 3=Magenta, 4=Yellow, 5=Blue. > "the first and second column represent the two colors in the memory display." (data/README.md) |
| **2** | `col2` | **Bottom/Lower Color** | 1=Red, 2=Green, 3=Magenta, 4=Yellow, 5=Blue. > "the first and second column represent the two colors in the memory display." (data/README.md) |
| **3** | `dist_cond` | **Distractor Condition** | **1** = Related to **First** Probe (combine with `cue_val` to determine color)<br>**2** = Related to **Second** Probe (combine with `cue_val` to determine color)<br>**3** = Unrelated Color Singleton<br>**4** = No Singleton. > "value 1 to 4 represent related first probe condition, related second probe condition color, unrelated condition, and no-singleton condition, respectively." (data/README.md) |

> **Critical Note on `dist_cond` Semantics:**
> 
> - **Experiment 1**: `dist_cond=1` and `dist_cond=2` are **EQUIVALENT** — both indicate the color singleton matches the memory color (`col1`). The original `data/README.md` states: *"value 1 and 2 represent the color of the distractor match the color in the memory display."* The distinction between "related first" vs "related second" is an **analysis-level** concept determined by combining `dist_cond` with `cue_val`, NOT encoded in `dist_cond` itself.
> 
> - **Experiment 2 & 3**: `dist_cond` encodes **probe order** ("first probe" vs "second probe"), NOT direct color mapping. The actual matched color must be determined by combining `dist_cond` with `cue_val`:
>   - `dist_cond=1` (first probe) + `cue_val=1` (col1 first) → match `col1`
>   - `dist_cond=1` (first probe) + `cue_val=2` (col2 first) → match `col2`  
>   - `dist_cond=2` (second probe) + `cue_val=1` (col1 first) → match `col2`
>   - `dist_cond=2` (second probe) + `cue_val=2` (col2 first) → match `col1`

