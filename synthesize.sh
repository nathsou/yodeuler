#!/bin/bash

set -e

module="Top"

mkdir -p output
rm -f output/$module.json output/$module.asc output/$module.bin output/$module.fir output/$module.sv

yodl Top.yodl "write_firrtl output/$module.fir"

firtool --format=fir -O=release --verilog \
    -disable-all-randomization -strip-debug-info \
    --lowering-options=disallowPackedArrays,disallowLocalVariables,emitBindComments \
    output/$module.fir -o output/$module.sv

yosys -p "verilog_defines -DENABLE_INITIAL_MEM_=1; read_verilog -sv output/$module.sv; check -assert; synth_ice40 -top Top -json output/$module.json"
nextpnr-ice40 --hx8k --json output/$module.json --pcf constraints/cu.pcf --package cb132 --asc output/$module.asc
icepack output/$module.asc output/$module.bin
openFPGALoader -b ice40_generic output/$module.bin
