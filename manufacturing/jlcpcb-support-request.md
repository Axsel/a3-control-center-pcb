# JLCPCB pre-order engineering and sourcing request

Send this request to JLCPCB support before paying for Revision A. The requested
deliverable is a complete PCBA; no PCB connector may be omitted or left for
customer soldering.

## Board and assembly scope

- Board: A3 Control Center PCB, Revision A
- Requested assembled quantity: 2 boards, subject to confirmation by the JLC
  quotation portal for the selected Standard PCBA process
- Size: 100 x 70 mm
- Construction: four layers, 1.6 mm, JLC standard 7628 stack, ENIG, green mask,
  white top legend
- Assembly: top-side SMT plus required mixed-process/THT manual or wave
  soldering
- Source at least 2 usable pieces of each one-per-board constrained part, plus
  any attrition quantity required by JLC

## Questions requiring written confirmation

1. The JLC matcher marks GCT USB4105-GF-A (`J1`, LCSC `C3020560`) as difficult
   processing but selectable for an extra fee. Please confirm that paying this
   fee provides complete assembly of its SMT contacts and four plated
   through-hole shell stakes in the same Standard PCBA order.
2. Can JLC manually or wave solder JST B4B-PH-K-S(LF)(SN) (`J10`), Phoenix
   Contact 1715734 (`J20`, `J40`), and Same Sky RCJ-014 (`J60`)?
3. Will JLC accept J60's manufacturer-specified plated slots: pin 1 is
   2.20 x 1.20 mm and pin 2 is 2.00 x 1.00 mm? The 1.83:1 pin-1 slot is
   intentional and must not be silently altered.
4. Will JLC accept the TPS63070RNMR (`U5`) custom RNM0015A land pattern,
   including the documented 0.08 mm inner-heel relief on pads 4 and 5?
5. Can JLC global-source or accept customer consignment of the exact J1 and
   J60 parts listed below before component matching is locked?

## Required source actions

| Priority | Ref | Qty/board | Build qty | Exact manufacturer part | LCSC | Current evidence | Requested action |
|---|---|---:|---:|---|---|---|---|
| 1 | J1 | 1 | 2 + attrition | GCT USB4105-GF-A | C3020560 | 0 live units | Pre-order/global source/consign exact connector and confirm mixed SMT/PTH assembly |
| 2 | J60 | 1 | 2 + attrition | Same Sky RCJ-014 | C4991844 | 64-unit snapshot | Reserve exact yellow right-angle RCA and confirm four-hole manual/wave assembly |
| 3 | U41 | 1 | 2 + attrition | NXP TJA1055T/3/2Z | C5202584 | 4 live units | Reserve with order or global source exact `/3/2Z` logic-compatible variant |
| 4 | L1 | 1 | 2 + attrition | Sunlord WPN4020H2R2MT | C98361 | 33,235 stock/32,894 orderable snapshot | Reserve exact 2.2 uH part; local WPN4020H manufacturer land pattern; not documented AEC-Q200 |
| 5 | L2 | 1 | 2 + attrition | Coilcraft XGL4020-152MEC | C7417180 | 2407-unit snapshot | Reserve exact 1.5 uH XGL4020 drop-in-family part |

## Parts whose earlier shortages are already resolved

- U2 uses Silicon Labs `CP2102N-A02-GQFN28R`, LCSC `C964632`. The `R` suffix is
  only tape-and-reel packaging; live stock was 40,263.
- U40 uses Microchip `MCP2515T-I/SO`, LCSC `C153782`. The `T` prefix is only
  tape-and-reel packaging; controller silicon, temperature grade, pinout, and
  SOIC-18 footprint are unchanged.
- D60 uses HXY `HPESD5V0U1BA-Q`, LCSC `C25503782`, as the documented Revision A
  prototype substitution. It is electrically suitable and footprint-compatible
  but not AEC-Q101-qualified.
- C1 uses PSA `FV32N472J102EFG`, LCSC `C5156737`: 4.7 nF, 1 kV, C0G, +/-5%,
  1210. D078 accepts its commercial/non-AEC-Q200 status for Revision A.
- SW1/SW2/SW3 use E-Switch `TL3301NF260QG`, LCSC `C273528`. Its footprint and
  pin topology are audited and identical to the former 160 gf variant. The
  current consolidated JLC workbook allocates the required quantity 6 from
  JLCPCB for two assembled boards.

Stock is volatile. Recheck and reserve every exact MPN at quotation time even
when it is not listed above.

## Copy/paste support message

> Please review 2 assembled units of this 100 x 70 mm four-layer Standard PCBA
> as a complete assembly. Please confirm that quantity 2 is accepted for this
> mixed-process order. J1, J10, J20, J40, and J60 must all be fitted; none may
> be DNP.
> J1 combines SMT contacts with PTH shell stakes. J10/J20/J40/J60 require
> manual or wave soldering. Please confirm acceptance of J60 plated slots
> 2.20 x 1.20 mm and 2.00 x 1.00 mm without changing them, and review the U5
> RNM0015A custom pads. Please quote global sourcing or consignment handling for
> exact J1 USB4105-GF-A and J60 RCJ-014. Also source exact L1
> SRP4020FA-2R2M and L2 XGL4020-152MEC. C1 is controlled as
> FV32N472J102EFG/C5156737. Reserve exact U41
> TJA1055T/3/2Z if catalog stock is insufficient. Do not substitute parts or
> omit connectors without written customer approval.

## Evidence to retain

- JLC support response and ticket number
- DFM viewer screenshots showing both J60 slots accepted
- Selected Parts page showing all five connectors and all exact IC variants
- CPL orientation screenshots for J1/J10/J20/J40/J60 and polarized parts
- Final quotation showing manual/THT assembly and sourced/consigned parts
