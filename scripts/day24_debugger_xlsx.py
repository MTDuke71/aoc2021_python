r"""Build inputs/day24_side_by_side.xlsx from inputs/day24.txt.

Three tabs:
  * Debugger (largest) / Debugger (smallest) -- edit the 14 yellow digits and
    the whole ALU trace recalculates.  Every register cell is a formula
    translated from its own instruction (add -> +, div -> TRUNC, eql -> IF),
    so nothing but the summary rows assumes the block template.
  * Side by side -- the 18-line blocks as 14 columns, varying lines shaded.

The output lands in inputs/, which is gitignored: it contains the puzzle input.

Usage (needs openpyxl in the venv):
    .venv\Scripts\python.exe -m pip install openpyxl
    .venv\Scripts\python.exe scripts\day24_debugger_xlsx.py

openpyxl writes formulas without cached values; Excel computes them on open.
Checked during development by recalculating in Excel and comparing every
register cell with day24.run_alu on 8 digit strings per tab (0 differences).
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

repo = Path(__file__).resolve().parent.parent
lines = [ln.split() for ln in (repo / "inputs" / "day24.txt").read_text().splitlines() if ln.strip()]
N = 18
blocks = [lines[i : i + N] for i in range(0, len(lines), N)]
assert len(blocks) == 14 and all(len(b) == N for b in blocks)
REGS = "wxyz"

ARIAL, ARIAL_B = Font(name="Arial"), Font(name="Arial", bold=True)
MONO, MONO_B = Font(name="Consolas"), Font(name="Consolas", bold=True)
HEAD = PatternFill("solid", fgColor="D9E1F2")
INPUT = PatternFill("solid", fgColor="FFFF00")
INSTR = PatternFill("solid", fgColor="EDEDED")
VARY = PatternFill("solid", fgColor="FFF2CC")
WRITTEN = PatternFill("solid", fgColor="E2EFDA")
GREEN = PatternFill("solid", fgColor="C6EFCE")
RED = PatternFill("solid", fgColor="FFC7CE")
CENTER = Alignment(horizontal="center")
TOP_RULE = Border(top=Side(style="thin", color="808080"))

wb = Workbook()
col = [get_column_letter(b + 2) for b in range(14)]  # B..O

# --- trace layout: per instruction, one instruction row then w x y z rows ---
TRACE0 = 15


def instr_row(i):
    return TRACE0 + i * 5


def reg_row(i, r):
    return TRACE0 + i * 5 + 1 + REGS.index(r)


def ref(b, i, r):
    """Cell holding register r after line i (0-based) of block b; i = -1 is the block's start state."""
    if i >= 0:
        return f"{col[b]}{reg_row(i, r)}"
    if b == 0:
        return None  # all registers start at 0
    return f"{col[b - 1]}{reg_row(N - 1, r)}"


def prev(b, i, r):
    return ref(b, i - 1, r) or "0"


def operand(b, i, tok):
    if tok in REGS:
        return prev(b, i, tok)
    return f"({tok})" if tok.startswith("-") else tok


def build_debugger(ws, default, label):

    for b, block in enumerate(blocks):
        for i, (op, a, *rest) in enumerate(block):
            c = ws.cell(instr_row(i), b + 2, " ".join([op, a, *rest]))
            c.font, c.fill, c.border = MONO_B, INSTR, TOP_RULE
            for r in REGS:
                if r != a:
                    f = f"={prev(b, i, r)}"
                else:
                    x = prev(b, i, a)
                    y = operand(b, i, rest[0]) if rest else None
                    f = {
                        "inp": f"={col[b]}$2",
                        "add": f"={x}+{y}",
                        "mul": f"={x}*{y}",
                        "div": f"=TRUNC({x}/{y})",  # ALU div truncates toward zero
                        "mod": f"=MOD({x},{y})",
                        "eql": f"=IF({x}={y},1,0)",
                    }[op]
                cell = ws.cell(reg_row(i, r), b + 2, f)
                cell.font = MONO
                cell.number_format = "0"
                if r == a:
                    cell.fill, cell.font = WRITTEN, MONO_B

    for i in range(N):
        c = ws.cell(instr_row(i), 1, f"Line {i + 1}")
        c.font, c.fill, c.border = ARIAL_B, INSTR, TOP_RULE
        for r in REGS:
            ws.cell(reg_row(i, r), 1, f"   {r}").font = MONO

    # --- summary panel ------------------------------------------------------------
    ws["A1"] = label
    ws["A2"] = "Input (edit me)"
    ws["A3"] = "Block kind"
    ws["A4"] = "w that would match"
    ws["A5"] = "Result"
    ws["A6"] = "z after block"
    ws["A7"] = "Stack (bottom → top)"
    ws["A8"] = "Stack depth"
    for rr in range(1, 9):
        ws.cell(rr, 1).font = ARIAL_B
    ws["A1"].fill = HEAD

    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="9", showErrorMessage=True)
    dv.error, dv.errorTitle = "Model number digits are 1..9", "Digit out of range"
    ws.add_data_validation(dv)

    for b, block in enumerate(blocks):
        is_pop = block[4] == ["div", "z", "26"]
        z_end = ref(b, N - 1, "z")
        x_cmp = ref(b, 5, "x")  # after "add x check": top of stack + check
        x_eq0 = ref(b, 7, "x")  # after "eql x 0": 1 = mismatch
        pushed = ref(b, 16, "y")  # after "mul y x": w + offset when it pushes

        h = ws.cell(1, b + 2, f"Digit {b}")
        h.font, h.fill, h.alignment = ARIAL_B, HEAD, CENTER
        d = ws.cell(2, b + 2, int(default[b]))
        d.font, d.fill, d.alignment = Font(name="Arial", bold=True, size=12), INPUT, CENTER
        dv.add(d)
        ws.cell(3, b + 2, "pop" if is_pop else "push").font = ARIAL
        if is_pop:
            ws.cell(4, b + 2, f'=IF(AND({x_cmp}>=1,{x_cmp}<=9),{x_cmp},"none ("&{x_cmp}&")")')
            ws.cell(5, b + 2, f'=IF({x_eq0}=0,"match ✓","MISMATCH, push "&{pushed})')
        else:
            ws.cell(4, b + 2, f'="never ("&{x_cmp}&")"')
            ws.cell(5, b + 2, f'="push "&{pushed}')
        ws.cell(6, b + 2, f"={z_end}").number_format = "#,##0"
        stack = "&".join(f'IF({z_end}>=26^{k},MOD(INT({z_end}/26^{k}),26)&" ","")' for k in range(7, -1, -1))
        ws.cell(7, b + 2, f'=IF({z_end}=0,"(empty)",TRIM({stack}))')
        ws.cell(8, b + 2, "=" + "+".join(f"({z_end}>=26^{k})" for k in range(8)))
        for rr in range(3, 9):
            ws.cell(rr, b + 2).font = ARIAL
            ws.cell(rr, b + 2).alignment = CENTER

    ws.conditional_formatting.add("B5:O5", FormulaRule(formula=['LEFT(B5,5)="match"'], fill=GREEN))
    ws.conditional_formatting.add("B5:O5", FormulaRule(formula=['LEFT(B5,8)="MISMATCH"'], fill=RED))

    ws["A10"], ws["A11"] = "Model number", "Verdict (z = 0?)"
    ws["A10"].font = ws["A11"].font = ARIAL_B
    ws["B10"] = "=" + "&".join(f"{c}2" for c in col)
    ws["B11"] = f'=IF({col[13]}6=0,"VALID ✓","INVALID (z = "&TEXT({col[13]}6,"#,##0")&")")'
    ws["B10"].font = Font(name="Consolas", bold=True, size=12)
    ws["B11"].font = Font(name="Arial", bold=True, size=12)
    ws.conditional_formatting.add("B11", FormulaRule(formula=[f"{col[13]}6=0"], fill=GREEN))
    ws.conditional_formatting.add("B11", FormulaRule(formula=[f"{col[13]}6<>0"], fill=RED))

    notes = [
        "Edit the yellow digits (1-9) in row 2; everything else is a formula and recalculates.",
        "Trace below: each instruction, then w x y z right after it. Green = the register that instruction writes.",
        "Each block's start state is the previous column's line-18 registers (digit 0 starts at all zeros).",
        "z is a base-26 stack: push = z*26 + (w+offset), pop = z/26. 'w that would match' = top of stack + check (line 6).",
        (
            "Only z really carries between digits: line 1 (inp w) overwrites w, line 2 (mul x 0) and line 9 (mul y 0)"
            " zero x and y before they are read. The carried w/x/y links never change a result."
        ),
    ]
    for k, t in enumerate(notes):
        ws.cell(12 + k // 2, 4 + 7 * (k % 2), t).font = Font(name="Arial", italic=True, color="595959")

    ws.column_dimensions["A"].width = 22
    for c in col:
        ws.column_dimensions[c].width = 15
    ws.freeze_panes = "B3"


build_debugger(wb.active, "51939397989999", "LARGEST (part 1)")
wb.active.title = "Debugger (largest)"
build_debugger(wb.create_sheet("Debugger (smallest)"), "11717131211195", "SMALLEST (part 2)")

# --- static side-by-side sheet (unchanged from before) ----------------------
s2 = wb.create_sheet("Side by side")
labels = {5: "div", 6: "check", 16: "offset"}
s2.cell(1, 1, "Line").font = ARIAL_B
s2.cell(1, 1).fill = HEAD
for b in range(14):
    c = s2.cell(1, b + 2, f"Digit {b}")
    c.font, c.fill, c.alignment = ARIAL_B, HEAD, CENTER
s2.cell(1, 16, "Varies").font = ARIAL_B
s2.cell(1, 16).fill = HEAD
for r in range(N):
    s2.cell(r + 2, 1, r + 1).font = ARIAL
    vals = [" ".join(blk[r]) for blk in blocks]
    varies = len(set(vals)) > 1
    for b, v in enumerate(vals):
        c = s2.cell(r + 2, b + 2, v)
        c.font = MONO
        if varies:
            c.fill = VARY
    if varies:
        s2.cell(r + 2, 16, labels[r + 1]).font = ARIAL_B
s2.column_dimensions["A"].width = 6
for c in col:
    s2.column_dimensions[c].width = 12
s2.freeze_panes = "B2"
s2.cell(21, 1, "Highlighted rows are the only lines that differ between digits.").font = Font(
    name="Arial", italic=True
)

out = repo / "inputs" / "day24_side_by_side.xlsx"
wb.save(out)
print(out, "trace rows", TRACE0, "-", reg_row(N - 1, "z"))
