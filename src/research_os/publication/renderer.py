"""Deterministic, dependency-free PDF projection; never interprets markup."""

import textwrap


def render_pdf(text: str) -> bytes:
    """Render printable ASCII with Helvetica; reject unsupported glyphs explicitly.

    No clock, random IDs, shell, HTML, links or executable PDF actions are used.
    Unicode remains supported in Manuscript source, but requires another explicitly
    selected renderer rather than silently losing glyphs in this minimal profile.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("PDF source must be nonempty text")
    if any(ord(c) > 126 or (ord(c) < 32 and c not in '\n\t') for c in text):
        raise ValueError("minimal PDF renderer supports printable ASCII, newline and tab only")
    lines = []
    for line in text.expandtabs(4).split('\n'):
        lines.extend(textwrap.wrap(line, 88, replace_whitespace=False) or [''])
    pages = [lines[i:i + 54] for i in range(0, len(lines), 54)]
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    for page in pages:
        page_id = len(objects) + 1
        kids.append(f'{page_id} 0 R')
        objects.append((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
                        f'/Resources << /Font << /F1 3 0 R >> >> '
                        f'/Contents {page_id + 1} 0 R >>').encode('ascii'))
        commands = [b'BT /F1 10 Tf 12 TL 42 750 Td']
        for line in page:
            literal = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
            commands.append(f'({literal}) Tj T*'.encode('ascii'))
        commands.append(b'ET')
        stream = b'\n'.join(commands) + b'\n'
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode() + stream + b'endstream')
    objects[1] = f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(kids)} >>'.encode()
    output = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offsets = []
    for index, obj in enumerate(objects, 1):
        offsets.append(len(output))
        output.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(output)
    output.extend(f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'.encode())
    for offset in offsets:
        output.extend(f'{offset:010d} 00000 n \n'.encode())
    output.extend((f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n'
                   f'startxref\n{xref}\n%%EOF\n').encode())
    return bytes(output)
