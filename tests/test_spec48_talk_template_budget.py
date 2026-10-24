"""F57-TALK-01: execute the Markdown example's gates without a PPT installation.

Only the PPT container/layout and populated outline are test doubles. The real
create_presentation and require_text code runs; no file is exported or rendered.
"""
import ast
import math
import re
import unittest
from pathlib import Path
from types import SimpleNamespace

TEMPLATE = Path(__file__).resolve().parents[1] / "skills/writing-cycle/paper-talk/references/slide-templates.md"


def example_namespace(count, seconds, reason, *, page_text="Verified paper evidence"):
    blocks = re.findall(r"^```python\n(.*?)^```", TEMPLATE.read_text(encoding="utf-8"), re.M | re.S)
    if len(blocks) != 1:
        raise AssertionError("expected one complete Python generation example")
    tree = ast.parse(blocks[0], filename=str(TEMPLATE))
    constants = {
        "SLIDE_COUNTS", "SECONDS_PER_SLIDE", "CONFIRMED_TALK_TYPE",
        "CONFIRMED_COUNT_EXCEPTION", "COUNT_EXCEPTION_REASON", "VENUE_COLORS",
    }
    selected = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in {"require_text", "create_presentation"}:
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in constants for target in node.targets
        ):
            selected.append(node)

    def presentation():
        layout = SimpleNamespace(iter_cloneable_placeholders=lambda: [], shapes=[])
        return SimpleNamespace(slide_layouts=[layout], slides=[])

    def populated_outline(prs, *_args):
        prs.slides = [
            SimpleNamespace(
                shapes=[SimpleNamespace(has_text_frame=True, text=page_text)],
                notes_slide=SimpleNamespace(notes_text_frame=SimpleNamespace(text="Timing and evidence verified")),
            )
            for _ in range(count)
        ]
        return [(index, seconds / count) for index in range(1, count + 1)], []

    namespace = {"math": math, "Presentation": presentation, "Inches": lambda value: value}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(TEMPLATE), "exec"), namespace)
    namespace.update(
        CONFIRMED_TALK_TYPE="oral", COUNT_EXCEPTION_REASON=reason,
        build_confirmed_outline=populated_outline,
    )
    return namespace


class TalkTemplateBudget(unittest.TestCase):
    def create(self, count, seconds, reason, *, title="Paper talk", page_text="Verified paper evidence"):
        namespace = example_namespace(count, seconds, reason, page_text=page_text)
        return namespace["create_presentation"](title, "", "", "", "oral", 20, "GENERIC")

    def test_autonomous_23_slide_outline_with_reason_and_1150_seconds_passes(self):
        result = self.create(23, 1150, "Mandate permits autonomous outline; short transition pages fit the 20-minute budget")
        self.assertEqual(result[1], 23)
        self.assertAlmostEqual(result[3], 1150)

    def test_real_time_budget_still_rejects_even_with_count_reason(self):
        with self.assertRaisesRegex(ValueError, "超出净预算"):
            self.create(23, 1230, "Autonomous outline uses short transitions")

    def test_outside_count_range_requires_a_real_reason(self):
        for reason in ("", "   ", "UNFILLED: count rationale"):
            with self.subTest(reason=reason), self.assertRaises(ValueError):
                self.create(23, 1150, reason)

    def test_inside_suggestion_range_needs_no_exception_reason(self):
        result = self.create(22, 1100, "")
        self.assertEqual(result[1], 22)

    def test_unfilled_title_and_page_text_remain_rejected(self):
        with self.assertRaises(ValueError):
            self.create(22, 1100, "", title="UNFILLED: title")
        with self.assertRaises(ValueError):
            self.create(22, 1100, "", page_text="UNFILLED: result")
