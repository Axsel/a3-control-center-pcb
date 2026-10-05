#!/usr/bin/env python3
"""Generate reviewable JLCPCB assembly candidates from the KiCad PCB.

This deliberately does not infer DNP state from KiCad's footprint flags because
Revision A's optional parts are presently controlled by the design decision log
and value text.  Keep the explicit sets below synchronized with the schematic,
BOM, and assembly notes.  Files named ``candidate`` are not order-ready until
the readiness report has no blockers and every BOM row has an approved LCSC
part number.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import pcbnew


ASSEMBLY_QUANTITY = 2
DNP = {"C63", "R4", "R24", "R25", "R61", "R63"}
# The owner requires a complete PCBA with no connector soldering. These parts
# must remain in both BOM and CPL and be selected for JLC manual/wave assembly.
MANUAL_ASSEMBLY = {"J1", "J10", "J20", "J40", "J60"}
NON_COMPONENT_PREFIXES = ("H", "JP", "TP")

# Exact MPNs already selected by engineering. Commodity passives intentionally
# remain blank until voltage, tolerance, dielectric, temperature, and stock are
# selected together in the JLC/LCSC library immediately before release.
MPN = {
    "C1": "FV32N472J102EFG",
    "D10": "LTST-C191KGKT",
    "D20": "PESD2CAN24T-Q",
    "D40": "PESD2CAN24T-Q",
    "D60": "HPESD5V0U1BA-Q",
    "J1": "USB4105-GF-A",
    "J10": "B4B-PH-K-S(LF)(SN)",
    "J20": "1715734",
    "J40": "1715734",
    "J60": "RCJ-014",
    "L1": "WPN4020H2R2MT",
    "L2": "XGL4020-152MEC",
    "Q1": "SS8050(RANGE:300-400)",
    "Q2": "SS8050(RANGE:300-400)",
    "SW1": "TL3301NF260QG",
    "SW2": "TL3301NF260QG",
    "SW3": "TL3301NF260QG",
    "U1": "USBLC6-2SC6",
    "U2": "CP2102N-A02-GQFN28R",
    "U3": "TPS2553DBVR",
    "U4": "TPS62132RGTR",
    "U5": "TPS63070RNMR",
    "U10": "ESP32-WROOM-32E-N4",
    "U20": "TCAN332DR",
    "U40": "MCP2515T-I/SO",
    "U41": "TJA1055T/3/2Z",
    "U60": "THS7314DR",
    "Y40": "ABM3BAIG-16.000MHZ-12-2-T",
}

# Catalog identities verified against exact-MPN LCSC product pages on
# 2026-10-04. Availability is deliberately not encoded here because it changes;
# see bom/jlcpcb-verified-parts.csv and recheck at order time.
LCSC = {
    "C1": "C5156737",
    "D10": "C125098",
    "D20": "C28933048",
    "D40": "C28933048",
    "D60": "C25503782",
    "J1": "C3020560",
    "J10": "C131334",
    "J20": "C480520",
    "J40": "C480520",
    "J60": "C4991844",
    "L1": "C98361",
    "L2": "C7417180",
    "Q1": "C177739",
    "Q2": "C177739",
    "SW1": "C273528",
    "SW2": "C273528",
    "SW3": "C273528",
    "U1": "C7519",
    "U2": "C964632",
    "U3": "C55266",
    "U4": "C81563",
    "U5": "C109322",
    "U10": "C701341",
    "U20": "C73651",
    "U40": "C153782",
    "U41": "C5202584",
    "U60": "C882751",
    "Y40": "C1986798",
}

# Exact commodity selections keyed by reviewed PCB value text and footprint.
# Including the footprint is essential because values such as 10 uF occur in
# both 0603 and 0805 packages on this board.
VALUE_PARTS = {
    ("5.1k 1%", "R_0603_1608Metric"): ("0603WAF5101T5E", "C23186"),
    ("1M", "R_0603_1608Metric"): ("0603WAF1004T5E", "C22935"),
    ("22.1k 1%", "R_0603_1608Metric"): ("0603WAF2212T5E", "C25961"),
    ("47.5k 1%", "R_0603_1608Metric"): ("0603WAF4752T5E", "C23061"),
    ("1k", "R_0603_1608Metric"): ("0603WAF1001T5E", "C21190"),
    ("28.7k 1%", "R_0603_1608Metric"): ("0603WAF2872T5E", "C22928"),
    ("10k", "R_0603_1608Metric"): ("0603WAF1002T5E", "C25804"),
    ("100k", "R_0603_1608Metric"): ("0603WAF1003T5E", "C25803"),
    ("680k 1%", "R_0603_1608Metric"): ("0603WAF6803T5E", "C25822"),
    ("130k 1%", "R_0603_1608Metric"): ("0603WAF1303T5E", "C22795"),
    ("0R (CMC bypass)", "R_0603_1608Metric"): ("0603WAF0000T5E", "C21189"),
    ("120R 1%", "R_0603_1608Metric"): ("0603WAF1200T5E", "C22787"),
    ("1.2k 1% CONFIG", "R_0603_1608Metric"): ("0603WAF1201T5E", "C22765"),
    ("33R", "R_0603_1608Metric"): ("0603WAF330JT5E", "C23140"),
    ("75R 1%", "R_0603_1608Metric"): ("0603WAF750JT5E", "C4275"),
    ("100nF", "C_0603_1608Metric"): ("CL10B104KB8NNNC", "C1591"),
    ("3.3nF", "C_0603_1608Metric"): ("C0603C332J5GACTU", "C2170675"),
    ("22uF 16V", "C_0805_2012Metric"): ("CL21A226MOQNNNE", "C98190"),
    ("10uF", "C_0603_1608Metric"): ("CL10A106MA8NRNC", "C96446"),
    ("10uF", "C_0805_2012Metric"): ("CL21A106KAYNNNE", "C15850"),
    ("4.7uF", "C_0805_2012Metric"): ("CL21B475KOFNNNE", "C107365"),
    ("1uF", "C_0805_2012Metric"): ("CL21B105KAFNNNE", "C116352"),
    ("22uF", "C_0805_2012Metric"): ("CL21A226MPQNNNE", "C29277"),
    ("18pF C0G", "C_0603_1608Metric"): ("CL10C180JB8NNNC", "C1647"),
    ("47uF", "C_1210_3225Metric"): ("CL32A476KPJNNNE", "C525654"),
    ("100uF low-ESR", "C_1210_3225Metric"): ("CL32A107MPVNNNE", "C23742"),
    ("100nF X7R FIT", "C_0805_2012Metric"): ("CC0805KRX7R9BB104", "C49678"),
}


def natural_key(ref: str) -> tuple[str, int, str]:
    head = "".join(c for c in ref if not c.isdigit())
    digits = "".join(c for c in ref if c.isdigit())
    return head, int(digits or 0), ref


def population_class(ref: str) -> tuple[str, str]:
    if ref in DNP:
        return "DNP", "Do not populate in Revision A default build"
    if ref in MANUAL_ASSEMBLY:
        return "JLC_MANUAL_ASSEMBLY_CANDIDATE", "Required fitted; manual/wave assembly and orientation review"
    if ref.startswith(NON_COMPONENT_PREFIXES):
        return "PCB_FEATURE", "Fabricated pad/feature; not a purchased placement"
    return "JLC_SMT_CANDIDATE", "Candidate for JLC SMT assembly"


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", nargs="?", default="hardware/dual_can_esp32.kicad_pcb")
    parser.add_argument(
        "--output-dir",
        default="manufacturing/generated/rev-a-audit/assembly",
    )
    args = parser.parse_args()

    board = pcbnew.LoadBoard(args.board)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)

    edge_box = board.GetBoardEdgesBoundingBox()
    # Edge bounding boxes include half the graphic line width.  Round to the
    # intended 0.1 mm mechanical grid, giving the reviewed (20, 20) origin.
    board_left = round(pcbnew.ToMM(edge_box.GetX()), 1)
    board_top = round(pcbnew.ToMM(edge_box.GetY()), 1)

    footprints = sorted(board.GetFootprints(), key=lambda fp: natural_key(fp.GetReference()))
    manifest_rows: list[list[object]] = []
    cpl_rows: list[list[object]] = []
    # Group the assembly BOM by the actual purchasable identity, not by the
    # schematic display value.  SW1/SW2/SW3 deliberately have different
    # functional labels but are the same physical MPN/LCSC part; emitting three
    # rows makes JLC flag an otherwise-correct duplicate match.
    bom_groups: dict[tuple[str, str, str], list[tuple[str, str]]] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)

    for fp in footprints:
        ref = str(fp.GetReference())
        value = str(fp.GetValue())
        footprint = str(fp.GetFPID().GetLibItemName())
        population, note = population_class(ref)
        counts[population] += 1

        pos = fp.GetPosition()
        x = pcbnew.ToMM(pos.x) - board_left
        y = pcbnew.ToMM(pos.y) - board_top
        side = "Top" if fp.GetLayer() == pcbnew.F_Cu else "Bottom"
        rotation = fp.GetOrientationDegrees() % 360
        value_part = VALUE_PARTS.get((value, footprint), ("", ""))
        mpn = MPN.get(ref, value_part[0])
        lcsc = LCSC.get(ref, value_part[1])

        manifest_rows.append(
            [ref, value, footprint, population, mpn, side, f"{x:.3f}", f"{y:.3f}", f"{rotation:.1f}", note]
        )

        if population in {"JLC_SMT_CANDIDATE", "JLC_MANUAL_ASSEMBLY_CANDIDATE"}:
            cpl_rows.append([ref, f"{x:.3f}mm", f"{y:.3f}mm", side, f"{rotation:.1f}"])
            bom_groups[(footprint, mpn, lcsc)].append((ref, value))

    write_csv(
        output / "assembly-population.csv",
        ["Designator", "Comment", "Footprint", "Population", "Manufacturer Part", "Layer", "X from board left", "Y from board top", "Rotation CCW", "Notes"],
        manifest_rows,
    )
    write_csv(
        output / "jlcpcb-cpl-candidate.csv",
        ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"],
        cpl_rows,
    )

    bom_rows: list[list[object]] = []
    missing_lcsc_refs: list[str] = []
    resolved_lcsc_refs: list[str] = []
    for (footprint, mpn, lcsc), items in sorted(
        bom_groups.items(), key=lambda item: natural_key(item[1][0][0])
    ):
        refs = sorted((ref for ref, _value in items), key=natural_key)
        values = sorted({value for _ref, value in items})
        comment = mpn or " / ".join(values)
        bom_rows.append([comment, ",".join(refs), footprint, lcsc])
        if not lcsc:
            missing_lcsc_refs.extend(refs)
        else:
            resolved_lcsc_refs.extend(refs)
    write_csv(
        output / "jlcpcb-bom-candidate.csv",
        ["Comment", "Designator", "Footprint", "JLCPCB Part #"],
        bom_rows,
    )

    report = output / "jlc-readiness.txt"
    report.write_text(
        "Revision A JLCPCB assembly readiness\n"
        "====================================\n\n"
        "STATUS: NOT READY FOR PCBA UPLOAD\n\n"
        f"Requested assembled prototype quantity: {ASSEMBLY_QUANTITY}\n"
        f"Board coordinate origin used: X={board_left:.1f} mm, Y={board_top:.1f} mm\n"
        f"JLC SMT candidates: {counts['JLC_SMT_CANDIDATE']}\n"
        f"DNP footprints excluded: {counts['DNP']}\n"
        f"PCB features excluded: {counts['PCB_FEATURE']}\n"
        f"Required manual/wave-assembly connectors: {counts['JLC_MANUAL_ASSEMBLY_CANDIDATE']}\n\n"
        "Release blockers:\n"
        f"- Confirm JLC accepts {ASSEMBLY_QUANTITY} assembled boards for this Standard PCBA mixed-process order.\n"
        "- J60 and L2 were changed to verified alternatives in D079; L1 was changed to high-stock WPN4020H2R2MT/C98361 in D080. Re-check live stock when ordering.\n"
        "- Recheck all exact-part stock and reserve/global-source shortages before release.\n"
        "- Obtain written responses to manufacturing/jlcpcb-support-request.md.\n"
        "- Confirm JLC manual/wave assembly for J1/J10/J20/J40/J60; all five are required in BOM and CPL.\n"
        "- Confirm J60 RCJ-014 through-hole/wave assembly and all four round plated holes.\n"
        "- Complete physical 1:1 fit checks for all through-hole/mixed-process connectors before the assembly order.\n"
        "- Re-run ERC, DRC, Gerber/drill review, and rotation/polarity review after any change.\n\n"
        "Accepted prototype risks (not release blockers):\n"
        "- Composite-video waveform and JVC compatibility validation is owner-deferred to assembled-board bring-up; no functional pass is claimed.\n\n"
        f"References with approved catalog identities: {len(resolved_lcsc_refs)}\n"
        f"References still lacking approved LCSC numbers ({len(missing_lcsc_refs)}):\n"
        + ", ".join(sorted(missing_lcsc_refs, key=natural_key))
        + "\n",
        encoding="utf-8",
    )

    print(report.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
