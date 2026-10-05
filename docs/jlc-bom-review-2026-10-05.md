# JLCPCB BOM matching review — 2026-10-05

Source workbook:
`manufacturing/generated/rev-a-audit/reports/jlcpcb-bom-candidate-JLCPCB Assembly Order.xls`

The file is an XLSX workbook despite its `.xls` extension. It was downloaded
from JLC on 2026-10-05 at 15:02:47 and reviewed row by row.

## Quantity interpretation

The workbook header reports `PCB Assembled Qty: 5`, while one-per-assembly
devices such as U2, U4, U5, U10, U20, U40, U41, U60, Y40, J60, L1, and L2 each
show an order quantity of 2. SW1-SW3 show quantity 6. This is consistent with
JLC fabricating its five-board PCB minimum while populating two boards, which
matches the controlled order intent. Reconfirm both quantities in the final
quotation.

## Accepted matches and changes

- J1 `USB4105-GF-A` / C3020560 is the correct connector. JLC labels its
  processing difficult but permits selection for an extra fee. Accept the fee
  only after written confirmation that SMT contacts and all PTH shell stakes
  are assembled.
- SW1-SW3 are now correctly consolidated as one BOM row using
  `TL3301NF260QG` / C273528, quantity 6 from JLCPCB. The earlier duplicate-line
  warning and stock ambiguity are closed for this quotation.
- U40 is matched to `MCP2515T-I/SO` / C153782. Microchip defines the `T` prefix
  as tape-and-reel; device, industrial temperature range, SOIC-18 package,
  pinout, electrical behavior, and firmware are unchanged. This match is
  accepted and made the controlled ordering code.
- D60 is changed to HXY `HPESD5V0U1BA-Q` / C25503782 under D075. It is an
  electrically suitable low-capacitance prototype substitute in the existing
  SOD-323 footprint, but it is not AEC-Q101-qualified.

## C1 mismatch resolved

- Reject the workbook's C1 suggestion `C1210X201F1HACAUTO` / C2309638. It is
  200 pF, 100 V, X8R and is wrong in capacitance, voltage, and dielectric.
- The owner located PSA `FV32N472J102EFG` / C5156737 in JLC global inventory.
  Manufacturer data verifies 4.7 nF, 1 kV, C0G, +/-5%, and a compatible 1210
  body. D078 adopts it for Revision A prototypes and records the loss of the
  former TDK part's AEC-Q200 qualification.

## Correct identities with zero JLCPCB stock

| Ref | Required part | LCSC | Disposition |
|---|---|---|---|
| J1 | GCT USB4105-GF-A | C3020560 | Difficult-processing fee plus source/pre-order; confirm complete mixed SMT/PTH assembly |
| J60 | Same Sky RCJ-014 | C4991844 | D079 in-stock replacement; reserve and confirm THT assembly |
| L1 | Sunlord WPN4020H2R2MT | C98361 | D080 high-stock replacement; 33,235 stock/32,894 orderable snapshot; MOQ 1 |
| L2 | Coilcraft XGL4020-152MEC | C7417180 | D079 documented drop-in-family replacement; reserve |

Do not select an inductor using inductance alone. Saturation current, RMS
current, DCR, shield construction, height, pad geometry, temperature behavior,
and regulator stability/layout requirements must all be checked before any
replacement.

## Release effect

The workbook is suitable for continued quotation and sourcing work, not final
payment. C1 is resolved. Final release remains blocked on J1/J60/L1/L2 sourcing, J1/J60
assembly-process confirmation, J60 slot acceptance, component rotation review,
and final DFM evidence.
