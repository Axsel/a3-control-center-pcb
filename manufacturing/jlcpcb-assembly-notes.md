# JLCPCB Revision A assembly notes

Use these notes in the JLCPCB PCBA remarks and confirm them with engineering
support before payment. This board is ordered as a **complete assembly**. The
customer is not expected to solder any PCB connector.

Requested prototype quantity is **2 fully assembled boards**. Confirm the JLC
quotation accepts quantity 2 for the selected Standard PCBA mixed SMT/THT
process; do not silently increase the assembled quantity.

## Required connector population

Do not mark any of these references DNP and do not proceed with an unpopulated
substitute position:

| Ref | Exact part | LCSC | Process / orientation |
|---|---|---|---|
| J1 | GCT USB4105-GF-A | C3020560 | Mixed SMT contacts plus plated shell stakes; USB mouth faces the left PCB edge |
| J10 | JST B4B-PH-K-S(LF)(SN) | C131334 | THT manual/wave assembly; vertical keyed header; pin 1 is +3V3 |
| J20 | Phoenix Contact 1715734 | C480520 | THT manual/wave assembly; CAN_HS wire entry faces the right PCB edge |
| J40 | Phoenix Contact 1715734 | C480520 | THT manual/wave assembly; CAN_FT wire entry faces the right PCB edge |
| J60 | Same Sky RCJ-014 | C4991844 | THT manual/wave assembly; yellow RCA; pin 1 shell / pin 2 center |

No connector substitution is authorized without written approval. In
particular, do not replace J20/J40 with a Phoenix `-B-` internally commoned
variant: that would short CANH, CANL, and GND.

J60 uses intentional plated slots of 2.20 x 1.20 mm and 2.00 x 1.00 mm from
Kycon's drawing. Obtain JLC DFM acceptance without changing those slots.

## Sourcing

At the 2026-10-04 audit, J1 and J60 were out of stock. Use JLC pre-order/global
sourcing or customer consignment for the exact parts. Wait until all five
connector references are matched, selected, received into inventory, and
visible in the final Selected Parts list before releasing assembly.

The 2026-10-05 order workbook marks J1 as difficult processing with an extra
fee. The fee is acceptable only if JLC confirms that both the SMT contacts and
PTH shell stakes will be assembled. The same workbook reports zero JLCPCB stock
for J60 RCJ-014, L1 SRP4020FA-2R2M, and L2 XGL4020-152MEC; retain their exact identities
and use pre-order/global sourcing or consignment.

C1 is controlled as PSA FV32N472J102EFG / C5156737: 4.7 nF, 1 kV, C0G,
1210, +/-5%. JLC's earlier automatic suggestion C1210X201F1HACAUTO/C2309638
remains prohibited because it is only 200 pF, 100 V, X8R.

Use `jlcpcb-support-request.md` for the consolidated engineering questions and
source-action table. It also records the resolved CP2102N tape-and-reel and
button substitutions so they are not mistakenly reopened during matching.

## Order-screen checks

1. Upload `jlcpcb-bom-candidate.csv` and `jlcpcb-cpl-candidate.csv` only after
   the readiness report is cleared.
2. Confirm J1, J10, J20, J40, and J60 are selected, not unmatched, shortfall,
   or DNP.
3. Confirm their placement side is Top and compare orientation against the
   assembly drawing and 3D render.
4. Select/approve manual or wave soldering for all THT joints and the J1 shell
   stakes.
5. Save screenshots of component matching, orientation, DFM results, and the
   final quotation with the versioned release evidence.

## Ready-to-paste PCBA remark

> Quote 2 fully assembled PCBAs. Complete PCBA required. Assemble all connectors
> J1, J10, J20, J40, and J60;
> none may be omitted. J1 has SMT contacts and plated through-hole shell stakes.
> J10/J20/J40/J60 require THT manual/wave soldering. Use only the exact MPNs in
> the BOM. USB J1 mouth faces left; CAN J20/J40 wire entries and RCA J60 barrel
> face right. Confirm J60 plated-slot DFM before production. Contact customer if
> any exact connector cannot be sourced or assembled; do not depopulate or
> substitute it automatically.
