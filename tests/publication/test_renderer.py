from __future__ import annotations

import re
import unittest

from research_os.publication import render_pdf


class RendererTests(unittest.TestCase):
    def test_real_deterministic_pdf_and_literal_escaping(self):
        text = 'A (claim) \\ proof\n) Tj ET /JavaScript (evil)\n' + 'line\n' * 70
        pdf = render_pdf(text)
        self.assertEqual(pdf, render_pdf(text))
        self.assertTrue(pdf.startswith(b'%PDF-1.4\n'))
        self.assertTrue(pdf.endswith(b'%%EOF\n'))
        self.assertIn(b'A \\(claim\\) \\\\ proof', pdf)
        self.assertIn(b'\\) Tj ET /JavaScript \\(evil\\)', pdf)
        startxref = int(re.search(rb'startxref\n(\d+)', pdf)[1])
        self.assertEqual(pdf[startxref:startxref + 4], b'xref')
        for offset in re.findall(rb'(\d{10}) 00000 n ', pdf):
            self.assertRegex(pdf[int(offset):], rb'^\d+ 0 obj\n')
        self.assertIn(b'/Count 2', pdf)

    def test_independent_pdf_parser_recovers_literal_text(self):
        import shutil
        import subprocess
        import tempfile
        from pathlib import Path
        tool = shutil.which('pdftotext')
        if tool is None:
            self.skipTest('independent Poppler parser unavailable')
        text = 'Theorem (fixed) \\ proof\n) Tj ET /JavaScript (not executable)'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'paper.pdf'
            path.write_bytes(render_pdf(text))
            result = subprocess.run([tool, str(path), '-'], capture_output=True, check=True)
            self.assertIn(text, result.stdout.decode())

    def test_unsupported_glyphs_fail_instead_of_silent_replacement(self):
        with self.assertRaises(ValueError):
            render_pdf('中文 theorem')
        with self.assertRaises(ValueError):
            render_pdf('hidden\x00text')


if __name__ == '__main__':
    unittest.main()
