const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageNumber, PageBreak, LevelFormat
} = require('docx');
const fs = require('fs');

// Read short test
const md = fs.readFileSync('docs/测试说明书-完整版.md', 'utf8').split('\n').slice(0, 200).join('\n');
console.log('MD lines:', md.split('\n').length);

// Minimal parse
function parseMarkdown(md) {
  const lines = md.split('\n');
  const blocks = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trimEnd();
    const h2 = line.match(/^## (.+)/);
    const h3 = line.match(/^### (.+)/);
    if (h2) { blocks.push({ type: 'h2', text: h2[1].trim() }); i++; continue; }
    if (h3) { blocks.push({ type: 'h3', text: h3[1].trim() }); i++; continue; }
    if (line.match(/^\|.*\|$/)) {
      const tableLines = [];
      while (i < lines.length && lines[i].trimEnd().match(/^\|.*\|$/)) {
        tableLines.push(lines[i].trimEnd());
        i++;
      }
      const headers = tableLines[0].split('|').filter((_, k, a) => k > 0 && k < a.length - 1).map(c => c.trim());
      const rows = [];
      for (let j = 2; j < tableLines.length; j++) {
        if (tableLines[j].match(/^\|[-: |]+\|$/)) continue;
        const cells = tableLines[j].split('|').filter((_, k, a) => k > 0 && k < a.length - 1).map(c => c.trim());
        if (cells.length > 0) rows.push(cells);
      }
      blocks.push({ type: 'table', headers, rows });
      continue;
    }
    if (line.match(/^(\*|-) /)) {
      const items = [];
      while (i < lines.length && lines[i].trimEnd().match(/^(\*|-) /)) {
        const m = lines[i].trimEnd().match(/^(\*|-) (.+)/);
        if (m) items.push({ type: 'bullet', text: m[2].trim() });
        i++;
      }
      blocks.push({ type: 'list', items });
      continue;
    }
    if (line.trim()) blocks.push({ type: 'para', text: line });
    i++;
  }
  return blocks;
}

const blocks = parseMarkdown(md);
console.log('Blocks:', blocks.length);
const tableCount = blocks.filter(b => b.type === 'table').length;
console.log('Tables found:', tableCount);
console.log('First table headers:', blocks.find(b => b.type === 'table')?.headers);
console.log('First table rows[0]:', blocks.find(b => b.type === 'table')?.rows[0]);

// Now try to build and pack just the first table
const C = { LIGHT_BG: 'D5E8F0', GRAY: 'D9D9D9', DARK: '002060', DARK_TEXT: '1F2937', MID_TEXT: '4B5563', WHITE: 'FFFFFF', PRIMARY: '0070C0' };
const PW = 11906, PH = 16838, M = 1134, CW = PW - M * 2;
const thinBorder = { style: BorderStyle.SINGLE, size: 1, color: C.GRAY };
const allBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };

function makeTable(headers, rows, widths) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => new TableCell({
      borders: allBorders,
      width: { size: widths[i], type: WidthType.DXA },
      shading: { fill: C.LIGHT_BG, type: ShadingType.CLEAR },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true, font: 'Arial', size: 22 })] })]
    }))
  });
  const dataRows = rows.map(row => new TableRow({
    children: row.map((cell, i) => new TableCell({
      borders: allBorders,
      width: { size: widths[i], type: WidthType.DXA },
      children: [new Paragraph({ children: [new TextRun({ text: String(cell), font: 'Arial', size: 21 })] })]
    }))
  }));
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: widths, rows: [headerRow, ...dataRows] });
}

function computeWidths(headers, rows) {
  const count = headers.length;
  if (count === 0) return [];
  const colWidths = headers.map((h, colIdx) => {
    let maxLen = h.replace(/^\s+|\s+$/g, '').length;
    for (const row of rows) {
      if (row[colIdx] !== undefined) {
        const cellLen = String(row[colIdx]).replace(/^\s+|\s+$/g, '').length;
        if (cellLen > maxLen) maxLen = cellLen;
      }
    }
    return Math.max(maxLen, 2);
  });
  const total = colWidths.reduce((a, b) => a + b, 0);
  const usableWidth = Math.floor(CW * 0.75);
  const dxWidths = colWidths.map(w => Math.max(400, Math.floor((w / total) * usableWidth)));
  const sumWidths = dxWidths.reduce((a, b) => a + b, 0);
  dxWidths[dxWidths.length - 1] += (CW - sumWidths);
  return dxWidths;
}

const t = blocks.find(b => b.type === 'table');
const widths = computeWidths(t.headers, t.rows);
console.log('Widths:', widths);
const doc = new Document({
  sections: [{
    properties: { page: { size: { width: PW, height: PH }, margin: { top: M, right: M, bottom: M, left: M } } },
    children: [makeTable(t.headers, t.rows, widths)]
  }]
});

console.log('Packing...');
const start = Date.now();
Packer.toBuffer(doc).then(buf => {
  console.log('Packed in', Date.now() - start, 'ms, size:', buf.length);
  fs.writeFileSync('test-table.docx', buf);
  console.log('Written!');
}).catch(e => console.error('Error:', e));
