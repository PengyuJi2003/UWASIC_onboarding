`define IDLE 2'b00
`define TRANSACTION 2'b01
`define VALIDATION 2'b01
`define UPDATE 2'b11

module spi_peripheral (
    input wire cs_n     // Active-low chip select signal
    input wire sclk     // Clock signal from the controller
    input wire [7:0] copi     // Serial data output from controller
    output wire [7:0] cipo    // Serial data output from peripheral
);

reg [2:0] state;

endmodule