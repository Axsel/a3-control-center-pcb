# JLCPCB Revision A order parameters

These are the controlled defaults for quotation. Reconfirm every item in the
JLC order summary and save screenshots before payment.

| Parameter | Revision A selection |
|---|---|
| Assembled prototype quantity | 2 boards; reconfirm portal minimum and any excess bare-board quantity at quotation |
| Board outline | 100 x 70 mm rectangular single board |
| Layers | 4 |
| Finished thickness | 1.6 mm nominal |
| Material | Standard FR-4 |
| Stackup | Standard/no-impedance-requirement 4-layer 7628 construction |
| Outer copper | 1 oz |
| Inner copper | 0.5 oz |
| Layer order | L1 signals/components; L2 continuous GND; L3 power/slow signals; L4 signals |
| Solder mask | Green, both sides |
| Legend | White, top side; bottom legend intentionally empty |
| Surface finish | ENIG |
| Controlled impedance option | No |
| Via covering | Standard tenting where defined by Gerbers |
| Gold fingers / castellations | None |
| Electrical test | Yes |
| Assembly side | Top |
| Assembly scope | SMT plus required manual/wave assembly of J1/J10/J20/J40/J60 |

JLC's published standard 1.6 mm four-layer 7628 construction uses 1 oz outer
copper, 0.5 oz inner copper, and approximately 0.2104 mm prepreg between L1 and
L2. This is consistent with the board's intended close L2 reference plane.
KiCad's statistics sum copper, dielectric, and modeled solder-mask thicknesses
to 1.6062 mm while the board/job nominal remains 1.6 mm; order the nominal
1.6 mm JLC construction rather than entering 1.6062 mm as a custom thickness.

## USB disposition

The CP2102N interface is USB 2.0 full-speed (12 Mbit/s), not high-speed
480 Mbit/s. Silicon Labs' general USB guidance still recommends a nominal 90
ohm differential pair. The Revision A data traces are 0.20 mm wide, remain
short (less than approximately 16 mm of routed geometry from connector network
through ESD to bridge), and have a continuous L2 ground reference over their
primary F.Cu paths. The Type-C orientation-contact crossover uses short layer
changes and the pair is not continuously coupled at a single controlled gap.

Consequently Revision A does **not** claim controlled 90 ohm fabrication and
must not select JLC's paid controlled-impedance option. This is an accepted
full-speed USB prototype tradeoff, not a claim that 0.20/0.25 mm automatically
produces 90 ohms. Validate enumeration/programming with representative cables
during bring-up. If field testing shows marginal USB behavior, Revision B must
reroute the connector/ESD/bridge path as a field-solved pair before changing
the fabrication impedance option.

## Assembly selections

Use Standard PCBA if required for the complete mixed SMT/THT process. Apply the
controlled remarks in `manufacturing/jlcpcb-assembly-notes.md`. Do not proceed
until every required connector and every non-DNP BOM row is selected.
