# Adapted from https://projectf.io/posts/verilog-sim-verilator-sdl/

VFLAGS = -O3 -DENABLE_INITIAL_MEM_ --x-assign fast --x-initial fast --noassert

all: VSim

VSim.mk: Sim.sv
	verilator ${VFLAGS} -I./ Sim.sv --top-module Sim -cc --exe -j 0 wrapper.cpp -o sim

VSim: VSim.mk
	make -C ./obj_dir -f VSim.mk

Sim.fir:
	cd .. && yodl Sim.yodl "write_firrtl sim/Sim.fir"

Sim.sv: Sim.fir
	firtool -O=release --format=fir --verilog -disable-all-randomization -strip-debug-info Sim.fir -o Sim.sv

clean:
	rm -rf obj_dir sim Sim.sv Sim.fir VSim.mk
