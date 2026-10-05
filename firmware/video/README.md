# Video firmware and validation

The first reproducible bench target is in [`bench/`](bench/). It uses a pinned
GPL-3.0-or-later reference implementation to generate static PAL or NTSC on
GPIO25 through I2S0 DMA. It is intentionally isolated from the future product
application until licensing, coexistence, and measured hardware behavior have
been reviewed.

1. Build the PAL black pattern and validate line/frame timing on an oscilloscope.
2. Measure white and eight-step bars at the terminated RCA output.
3. Repeat with NTSC and establish what the JVC accepts.
4. Add text using a 320x200 1-bpp product-oriented framebuffer.
5. Measure DMA underruns and timing jitter under CAN and radio load.
6. Select or implement the production renderer only after the bench results.

Candidate feasibility references and analog acceptance criteria are in
`docs/video.md`. No external video library is vendored or approved as the
production dependency.
