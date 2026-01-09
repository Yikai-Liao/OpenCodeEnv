# Experiment Design: More Attention with Less Working Memory

## Research Paper
**Title**: More attention with less working memory: The active inhibition of attended but outdated information
**Authors**: Yingtao Fu, Yiling Zhou, Jifan Zhou, Mowei Shen, Hui Chen
**Journal**: Psychological Science / Science Advances (Ref mentioned Sci Adv in footer)
**Year**: 2021

## Experiment Overview
The study investigates whether paying more attention to information enhances or impedes its selection into working memory. It contrasts "key features" (attended but outdated) with "irrelevant features" (ignored).

> **Quote**: "Experiments 1 to 5 provide converging evidence for an even weaker working memory trace of fully attended but outdated features, compared with baseline irrelevant features that were completely ignored. This indicates that the brain actively inhibits attended but outdated information to prevent it from entering working memory." (Paper, Page 1)

We focus on reproducing the visual stimuli for **Experiments 1, 4, 5, and 6**. These experiments represent the core variations in the study (Shape memory vs. Size memory, varying task relevance, and executive control).
- **Experiment 1**: Shape irrelevant/key, color to memorize (Change detection).
- **Experiment 4**: Color irrelevant/key, size to memorize (Change detection).
- **Experiment 5**: Shape irrelevant/key, color memory, irrelevant-change distracting paradigm.
- **Experiment 6**: Shape key, size to memorize (Change detection under executive load).

## Stimuli Construction

### Global Settings
- **Background Color**: Medium Gray (RGB: 128, 128, 128)
- **Screen Resolution**: 1024 x 768 px
- **Viewing Distance**: ~50 cm

> **Quote**: "The background of the display was medium gray (RGB: 128, 128, 128)... All experiments were... presented on a 17-inch CRT monitor (100 Hz, 1024 × 768 screen resolution). Participants sat at a viewing distance of approximately 50 cm." (Paper, Page 7)

### Visual Parameters (Visual Angles)
- **Fixation**: 1.03° x 1.03°
- **Memory Item Size (Exp 1/2/3/5)**: 2.51° x 2.51°
- **Memory Item Size (Exp 4/6)**: Large (2.89° x 2.89°) or Small (2.12° x 2.12°)
- **Search Item Size**: 2.51° x 2.51°
- **Search Array Radius**: 7.40°
- **Line Segment Size**: 0.80° x 0.12°
- **Target Tilt**: 12° (Left or Right)

> **Quote**: "After a 500-ms fixation display (1.03° × 1.03°), a memory display... was presented at the center of the screen (2.51° × 2.51°) for 1000 ms... After a blank interval of 200 ms, there was a search display in which three distractor lines (black vertical lines, 0.80° × 0.12°) and one target line (black tilted line, 12° either to the left or to the right with equal probability) were embedded in four distinct colored shapes (2.51° × 2.51°) that were evenly distributed over an invisible circle (with a radius of 7.40°)." (Paper, Page 7)

### Colors
- **Red**: (255, 0, 0)
- **Green**: (0, 128, 0)
- **Blue**: (0, 0, 255)
- **Yellow**: (255, 255, 0)
- **Pink**: (255, 192, 203)

> **Quote**: "The colors were randomly selected from red (255, 0, 0), green (0, 128, 0), blue (0, 0, 255), yellow (255, 255, 0), and pink (255, 192, 203)." (Paper, Page 7)

### Shapes
- Match numeric indices in data (1-5):
  - 1: Circle
  - 2: Square
  - 3: Star
  - 4: Triangle
  - 5: Hexagon

> **Quote**: "The shapes could be circles, squares, stars, triangles, or hexagons." (Paper, Page 7)

### Trial Structure (Experiment 1a)
1. **Fixation**: 500 ms.
2. **Memory Display**: 1000 ms. Central colored shape.
   - Task: Memorize color, ignore shape.
3. **Retention Interval**: 200 ms (Blank).
4. **Search Display**: Until response.
   - 4 colored shapes evenly distributed on an invisible circle (r=7.40°).
   - Configuration 1: 30°, 120°, 210°, 300°.
   - Configuration 2: 60°, 150°, 240°, 330°.

> **Quote**: "There were two possible configurations of the four search stimuli locations (angle relative to horizon: 30°/120°/210°/300° or 60°/150°/240°/330°) with equal probability." (Paper, Page 7)

   - **Target**: One shape contains a tilted line (12° L/R).
   - **Distractors**: Three shapes contain vertical lines.
   - **Match Conditions**:
     - **Color Match**: One distractor shares the memory item's color.
     - **Shape Match**: One distractor shares the memory item's shape.
     - **Conjunction Match**: One distractor shares both color and shape.
     - **Neutral**: No distractors share any feature with memory item.
5. **Memory Test**: Change detection (Same/Diff color).

> **Quote**: "After a 500-ms blank interval, another colored shape appeared as a memory test item (2.51° × 2.51°). The test item had the same shape as the memory item, while its color remained the same as the memory item in half the trials and different in the other half." (Paper, Page 7)

## Data Structure
The reproduction uses `data/Exp.1a&1b/Exp.1a&1b/Exp.1a_original.xlsx`.

### Experiment 1 (a & b)
- **targetshape**: Memory shape (1-5).
- **matchcondition**: 1=Color, 2=Shape, 3=Conjunction, 4=Neutral.
- **linecondition**: 1=Left, 2=Right (Target tilt).
- `centered_line` angle is in degrees with **0° as horizontal** (pointing right), so vertical lines use 90° and a 12° left/right tilt is applied as `90 ± 12`.
- **test**: 1=Same, 0=Different.

### Experiment 4 (a & b)
- **targetcolor**: Memory color (1-5).
- **targetshape**: Memory shape (1-5).
- **targetsize**: 1=Large, 2=Small.
- **matchcondition**: 1=Color, 2=Shape, 4=Neutral (Conjunction removed).
- **SOA**: 400, 600, 1000, 1800, 3000 ms.
- **test**: 1=Same, 0=Different.
- **ArrowOrientation**: (Not used for stimuli generation).

### Experiment 5 (a & b)
- **targetcolor**: Memory color (1-5).
- **targetshape**: Memory shape (1-5).
- **target_change**: Working memory test target change (1=Change, 0=No change).
- **irre_change**: Irrelevant feature (shape) change (1=Change, 0=No change).
- **testcolor**: Index of color in test? Or binary? (Inspection required).
- **testshape**: Index of shape in test? Or binary?

### Experiment 6 (a & b)
- **targetcolor**: Memory color (1-5).
- **targetshape**: Memory shape (1-5).
- **targetsize**: 1=Large, 2=Small.
- **matchcondition**: 1=Color, 2=Shape, 3=Conjunction, 4=Neutral.
- **linecondition**: 1=Left, 2=Right.

### Reproduction Logic
Since the data file provides the *condition* but not all explicit random features (e.g., specific colors of non-matching distractors in Exp 1), the script will:
1. Read the trial condition.
2. Generate all features (Memory Color/Shape, Search Colors/Shapes) deterministically based on a random seed, ensuring the constraints of the `matchcondition` are met.
   - Example: If `matchcondition == 1` (Color Match), ensure one distractor in the search array has `MemoryColor` but `SearchShape != MemoryShape`.
3. Render the **Memory Display**, **Search Display** (if applicable), and **Test Display** images.
