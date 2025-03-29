#include <memory>
#include <iostream>

#include <verilated.h>
#include "VSim.h"

int main(int argc, char** argv) {
    const std::unique_ptr<VerilatedContext> contextp{new VerilatedContext};
    contextp->debug(0);
    const std::unique_ptr<VSim> top{new VSim{contextp.get(), "Sim"}};

    top->clk = 0;
    unsigned long i = 0L;

    while (!contextp->gotFinish()) {
        top->clk = 1;
        top->eval();
        top->clk = 0;
        top->eval();
        i++;
    }

    top->final();

    std::cout << "finished after " << i << " cycles" << std::endl;

    return 0;
}
