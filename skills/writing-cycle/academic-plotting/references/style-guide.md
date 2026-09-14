# Publication Style Guide for ML Paper Figures

Adapted from Orchestra. Read for final-size layout, typography, accessibility and LaTeX snippets. Venue measurements and font tables below are historical examples, not binding current rules: inspect the user-supplied template/current official guidelines before choosing dimensions; conflicts go to the user. Do not download or install templates, fonts, packages or renderers as part of plotting.

## Universal Rules

1. **Vector format preferred** — Export PDF for LaTeX, PNG for raster content or inspection; preserve editable diagram source
2. **300 DPI minimum** for raster images
3. **Colorblind-safe palettes** — Never rely on color alone; add markers, patterns, or labels
4. **Consistent style** — All figures in a paper must share fonts, colors, and styling
5. **Self-contained** — Figure and caption together identify content, units, source, transformations and limitations
6. **Data charts stay economical** — omit decorative depth, gradients and clip art. Diagram-only visual styles may vary without changing semantics.

## Venue-Specific Figure Dimensions

### NeurIPS

| Layout | Width | Notes |
|--------|-------|-------|
| Single column | 5.5 in | NeurIPS is single-column |
| Half width | 2.65 in | Side-by-side within column |
| Max height | 9 in | Full page |

Historical example only; use the existing target template.

### ICML

| Layout | Width | Notes |
|--------|-------|-------|
| Single column | 3.25 in | ICML is two-column |
| Full width | 6.75 in | `\begin{figure*}` |
| Max height | 9.25 in | Full page |

Historical example only; use the existing target template.

### ICLR

| Layout | Width | Notes |
|--------|-------|-------|
| Single column | 5.5 in | ICLR is single-column |
| Max height | 9 in | Full page |

Historical example only; use the existing target template.

### ACL / EMNLP

| Layout | Width | Notes |
|--------|-------|-------|
| Single column | 3.3 in | ACL is two-column |
| Full width | 6.8 in | `\begin{figure*}` |

Historical example only; use the existing target template.

### AAAI

| Layout | Width | Notes |
|--------|-------|-------|
| Single column | 3.3 in | AAAI is two-column |
| Full width | 7.0 in | `\begin{figure*}` |

## Color Palettes

### Recommended Colorblind-Safe Palette

This is a styling option, not a guarantee across color vision deficiencies. Prefer Okabe-Ito from the data reference, add non-color encodings, and inspect grayscale/contrast:

```python
# "deep" variant — high contrast, good for lines and bars
PALETTE_DEEP = [
    "#4C72B0",  # blue
    "#DD8452",  # orange
    "#55A868",  # green
    "#C44E52",  # red
    "#8172B3",  # purple
    "#937860",  # brown
    "#DA8BC3",  # pink
    "#8C8C8C",  # gray
]
```

### Two-Color Schemes (ours vs. baseline)

```python
# High contrast pair
OURS = "#C44E52"     # red — stands out
BASELINE = "#8C8C8C" # gray — recedes

# Alternative pair
OURS = "#4C72B0"     # blue
BASELINE = "#DD8452"  # orange
```

### Gradient Schemes (for heatmaps / continuous data)

| Use Case | Colormap | Code |
|----------|----------|------|
| Single variable (0 to max) | Blues | `cmap="Blues"` |
| Diverging (negative to positive) | RdBu_r | `cmap="RdBu_r"` |
| Perceptually uniform | viridis | `cmap="viridis"` |
| Correlation matrix | coolwarm | `cmap="coolwarm"` |
| Attention weights | YlOrRd | `cmap="YlOrRd"` |

### Colors to Avoid

- **Pure red + pure green** — indistinguishable for ~8% of males
- **Rainbow/jet colormap** — perceptually non-uniform, misleading
- **Light yellow on white** — insufficient contrast
- **Neon/saturated colors** — look unprofessional in academic papers

## Typography

### Font Matching LaTeX Documents

| Conference | Document Font | Figure Font Setting |
|-----------|---------------|-------------------|
| NeurIPS | Times | `font.family: serif`, `font.serif: Times New Roman` |
| ICML | Times | Same as NeurIPS |
| ICLR | Times | Same as NeurIPS |
| ACL | Times | Same as NeurIPS |
| AAAI | Times | Same as NeurIPS |

### Font Size Guidelines

| Element | Size | Rationale |
|---------|------|-----------|
| Axis labels | 10-11pt | Must be readable at print size |
| Tick labels | 8-9pt | Smaller but legible |
| Legend text | 8-9pt | Compact but readable |
| Title (if any) | 11-12pt | Usually omitted (caption serves as title) |
| Annotations | 7-8pt | Smallest readable size |

**Rule**: No text in figures smaller than 7pt at final print size.

### Math Typesetting

```python
# For inline math
ax.set_xlabel(r"Number of parameters $N$")

# For display math
ax.set_ylabel(r"Loss $\mathcal{L}(\theta)$")

# Greek letters
ax.set_xlabel(r"Learning rate $\alpha$")

# Subscripts/superscripts
ax.set_ylabel(r"$R^2$ score")
```

## Layout Conventions

### Legend Placement

Priority order:
1. **Inside the plot** (upper-left or upper-right) if space allows
2. **Below the plot** with `bbox_to_anchor=(0.5, -0.15), loc="upper center", ncol=N`
3. **To the right** with `bbox_to_anchor=(1.05, 1), loc="upper left"` (takes extra width)

```python
# Clean legend (no frame, no extra spacing)
ax.legend(frameon=False, loc="upper left", handlelength=1.5)

# External legend below
ax.legend(frameon=False, bbox_to_anchor=(0.5, -0.15),
          loc="upper center", ncol=4)
```

### Grid Lines

```python
# Subtle grid (recommended)
ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.5)

# Major grid only (for log-scale plots)
ax.grid(True, which="major", alpha=0.3, linestyle="--")
ax.grid(True, which="minor", alpha=0.1, linestyle=":")
```

### Axis Styling

```python
# Remove top and right spines (clean look)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Reduce tick padding
ax.tick_params(axis="both", which="major", pad=3)
```

### Multi-Panel Labels

```python
# Standard (a), (b), (c) labels
for i, ax in enumerate(axes.flat):
    ax.set_title(f"({chr(97 + i)})", loc="left", fontweight="bold", fontsize=11)

# Or as text annotation
ax.text(-0.1, 1.05, "(a)", transform=ax.transAxes,
        fontsize=12, fontweight="bold", va="top")
```

## Diagram Style Standards

For AI-generated architecture/system diagrams:

### Professional Diagram Palette

```
Section accents:  Blue #4A90D9, Teal #5BA58B, Amber #D4A252, Slate #7B8794
Failure/error:    Red #D94A4A (dashed lines)
Section fill:     #F7F7F5 (very pale warm gray)
Box borders:      #DDDDDD
Box fill:         #FFFFFF
Primary text:     #333333
Secondary text:   #666666
Background:       #FFFFFF
```

### Layout Patterns for Diagrams

| Pattern | When to Use | Description |
|---------|-------------|-------------|
| Horizontal bands | Layered architectures | Sections stacked vertically, boxes horizontal |
| Left-to-right flow | Sequential pipelines | Input → Processing → Output |
| Hub-and-spoke | Central component | Central node with radiating connections |
| Grid | Matrix of components | Regular arrangement for comparison |
| Tree | Hierarchical decisions | Top-down branching structure |

### Arrow Conventions

| Arrow Type | Style | Usage |
|-----------|-------|-------|
| Data flow | Solid, colored by source | Normal information passing |
| Control flow | Solid, gray | Orchestration signals |
| Error/failure | Dashed, red | Failure paths, refutation |
| Optional | Dotted, gray | Conditional paths |
| Bidirectional | Double-headed | Mutual dependencies |

## LaTeX Integration

### Basic Figure Inclusion

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/fig_name.pdf}
  \caption{Clear description of what the figure shows. Best viewed in color.}
  \label{fig:name}
\end{figure}
```

### Full-Width Figure (two-column venues)

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/fig_overview.pdf}
  \caption{System overview showing the three main components.}
  \label{fig:overview}
\end{figure*}
```

### Side-by-Side Subfigures

Requires an already available and venue-compatible subfigure package. Output snippets only; this skill does not edit the manuscript preamble or compile the full paper.

```latex
\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\linewidth}
    \centering
    \includegraphics[width=\linewidth]{figures/fig_a.pdf}
    \caption{Training loss}
    \label{fig:a}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\linewidth}
    \centering
    \includegraphics[width=\linewidth]{figures/fig_b.pdf}
    \caption{Evaluation accuracy}
    \label{fig:b}
  \end{subfigure}
  \caption{[Describe both panels using their actual source data, n and uncertainty definition.]}
  \label{fig:training}
\end{figure}
```

### Caption Best Practices

- **First sentence**: What the figure shows (standalone understanding)
- **Key takeaway**: What the reader should notice
- **Encoding note**: explain markers/lines as well as color; a color note does not replace accessible encodings.
- **Data note**: name source, n/unit of replication, filtering, error-band definition, and non-comparable conditions.
- **Diagram note**: explicitly say “Schematic — not experimental evidence”; identify conceptual/optional connections and any AI assistance.
- **No "Figure X shows..."** — the figure number is already there

Good: "Training loss across model sizes. Larger models converge faster and to lower final loss."
Bad: "Figure 3 shows the training loss for different model sizes."

## Accessibility Checklist

- [ ] Figures readable in grayscale (print-friendly)
- [ ] No text smaller than 7pt at final print size
- [ ] Colorblind-safe palette used
- [ ] Different line styles/markers in addition to colors
- [ ] High contrast between data and background
- [ ] Axis labels present and readable
- [ ] Legend clear and non-overlapping
