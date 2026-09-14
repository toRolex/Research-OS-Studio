# Comparison Tables and Figure Review

Adapted from ARIS `paper-figure` table, include-snippet and review steps. Read when making comparison tables or reviewing completed figures. These local methods do not invoke a writing workflow.

## Comparison table

Read the plan's table rows and their original evidence, including prior-work conditions. For theoretical comparisons, preserve assumptions, rate notation and variable definitions; a rate is not a measured benchmark. Verify the source establishes the stated expression under the compared conditions. Unresolved source identity or context stays “unverified”; do not invent bibliography keys.

For empirical comparisons, load cells from the result files with units, n and uncertainty definitions; keep missing results visibly missing. Bold a best value only under a declared direction, comparable protocol and tie rule; formatting is not a significance test.

Produce a standalone Markdown table or `.tex` file, plus the generation source and cell-to-source explanation. The following is a structure template, not a completed result table. Replace brackets only with verified content. `booktabs` and any citation package must already exist before compiling; plain `tabular` is a no-extra-package option. Do not install or edit the manuscript preamble.

```latex
\begin{table}[t]
\centering
\caption{[Compared quantity, units, conditions, n and uncertainty; define all symbols.]}
\label{tab:comparison}
\begin{tabular}{lcc}
\hline
Method & [Metric or theoretical rate] & [Conditions] \\
\hline
[Verified method] & [Source-backed value] & [Assumptions/budget] \\
\hline
\end{tabular}
\end{table}
```

## Include snippet

Preserve existing manual figures and use their actual paths. Resolve paths relative to the intended manuscript location, not the skill installation. Output the fragment beside the figures only when requested; insertion into the manuscript is a separate authorization. A missing image gets a gap note, not a dangling `includegraphics` advertised as complete.

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{[actual relative figure path]}
  \caption{[Self-contained, source-constrained caption.]}
  \label{fig:[unique figure id]}
\end{figure}
```

## Review prompt

Apply to each figure/table after reopening the actual render. Use as self-check or give an authorized independent reviewer direct access to the source files, transformations, image and caption. Report which mode actually occurred.

> Review these figures/tables for the specified audience and final size.
>
> 1. Is each caption informative and self-contained? Does every quantitative or comparative statement survive checking all plotted rows, including unfavorable cases?
> 2. Does the figure type suit the data, or does a different display reveal the comparison more clearly?
> 3. Are comparisons fair and legible, with units, conditions, n and uncertainty defined? Does highlighting obscure any baseline?
> 4. Are relevant supplied baselines or ablations omitted? Name evidence-backed gaps; propose additional experiments only as future user decisions.
> 5. For diagrams, is every component and edge supported by the method description, with conceptual/proposed content labeled?
> 6. Do actual exported labels, glyphs, legends and panel markers remain readable at the intended size and in grayscale?
> 7. Can a reader locate editable source, source data and exact reproduction steps? Separate static checks, executed commands, visual inspection and scientific interpretation.
>
> Return specific findings with figure/panel and source location, a scoped correction or question, and checks you could not perform. A score or no-findings result is not user acceptance.
