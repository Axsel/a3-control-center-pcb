#!/usr/bin/env bash
set -euo pipefail

# Independent raster review of the KiCad-generated fabrication package.
# gerbv 2.9.x reports KiCad's X2 TF/TA/TO attributes as unknown metadata but
# still parses and renders the underlying RS-274X geometry.

root="manufacturing/generated/rev-a-audit"
gerbers="$root/gerbers"
drill="$root/drill"
out="$root/review"
mkdir -p "$out"

render() {
    local output="$1"
    shift
    gerbv -a -B 2 -w 1600x1200 -b '#FFFFFF' \
        -x png -o "$out/$output" "$@" 2>"$out/${output%.png}.log"
}

render front-copper-drill.png \
    -f '#B00000' -f '#202020' -f '#000000' -f '#000000' \
    "$gerbers/dual_can_esp32-F_Cu.gtl" \
    "$gerbers/dual_can_esp32-Edge_Cuts.gm1" \
    "$drill/dual_can_esp32-PTH.drl" "$drill/dual_can_esp32-NPTH.drl"
render front-mask.png -f '#0050A0' -f '#202020' \
    "$gerbers/dual_can_esp32-F_Mask.gts" "$gerbers/dual_can_esp32-Edge_Cuts.gm1"
render front-paste.png -f '#A000A0' -f '#202020' \
    "$gerbers/dual_can_esp32-F_Paste.gtp" "$gerbers/dual_can_esp32-Edge_Cuts.gm1"
render front-silkscreen.png -b '#202020' -f '#FFFFFF' -f '#E0B000' \
    "$gerbers/dual_can_esp32-F_Silkscreen.gto" "$gerbers/dual_can_esp32-Edge_Cuts.gm1"
render back-copper-drill.png \
    -f '#0040B0' -f '#202020' -f '#000000' -f '#000000' \
    "$gerbers/dual_can_esp32-B_Cu.gbl" \
    "$gerbers/dual_can_esp32-Edge_Cuts.gm1" \
    "$drill/dual_can_esp32-PTH.drl" "$drill/dual_can_esp32-NPTH.drl"
render back-mask.png -f '#0050A0' -f '#202020' \
    "$gerbers/dual_can_esp32-B_Mask.gbs" "$gerbers/dual_can_esp32-Edge_Cuts.gm1"
render back-paste.png -f '#A000A0' -f '#202020' \
    "$gerbers/dual_can_esp32-B_Paste.gbp" "$gerbers/dual_can_esp32-Edge_Cuts.gm1"
render back-silkscreen.png -b '#202020' -f '#FFFFFF' -f '#E0B000' \
    "$gerbers/dual_can_esp32-B_Silkscreen.gbo" "$gerbers/dual_can_esp32-Edge_Cuts.gm1"
render inner-gnd.png -f '#B06000' -f '#202020' -f '#000000' \
    "$gerbers/dual_can_esp32-GND plane.g1" \
    "$gerbers/dual_can_esp32-Edge_Cuts.gm1" "$drill/dual_can_esp32-PTH.drl"
render inner-power-signals.png -f '#008050' -f '#202020' -f '#000000' \
    "$gerbers/dual_can_esp32-Power and slow signals.g2" \
    "$gerbers/dual_can_esp32-Edge_Cuts.gm1" "$drill/dual_can_esp32-PTH.drl"

echo "Independent Gerber renders written to $out"
