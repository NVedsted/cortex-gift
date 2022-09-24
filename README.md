# Cortex-GIFT

This project allows for executing masked and unmasked GIFT-128 encryption on an STMF303xx-family chip. Intended for
testing leakage through differential power analysis. Furthermore, tooling written in Python is provided for data capture
through the ChipWhisperer suite and for data processing which conducts a Welch's t-test in a fixed-vs-random setting.

The masked and unmasked version are split into separate binaries.