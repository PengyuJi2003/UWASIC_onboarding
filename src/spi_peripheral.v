`define IDLE 2'b00
`define TRANSACTION 2'b01
`define VALIDATION 2'b10
`define UPDATE 2'b11

module spi_peripheral (
    input  wire cs_n,           // Active-low chip select signal
    input  wire rst_n,          // Active-low reset signal
    input  wire sclk,           // Clock signal from the controller
    input  wire copi,           // Controller out peripheral in
    output wire [7:0] reg_0,    // register with address 0x00
    output wire [7:0] reg_1,    // register with address 0x01
    output wire [7:0] reg_2,    // register with address 0x02
    output wire [7:0] reg_3,    // register with address 0x03
    output wire [7:0] reg_4     // register with address 0x04
);

//output regs & assignments
reg [7:0] out_reg_0;
reg [7:0] out_reg_1;
reg [7:0] out_reg_2;
reg [7:0] out_reg_3;
reg [7:0] out_reg_4;

assign reg_0 = out_reg_0;
assign reg_1 = out_reg_1;
assign reg_2 = out_reg_2;
assign reg_3 = out_reg_3;
assign reg_4 = out_reg_4;

//temp registers
reg [1:0] state;
reg [3:0] sclk_edge_counter;
reg [15:0] serial_data;

always @(posedge sclk or negedge rst_n) begin
    if(!rst_n) begin
        sclk_edge_counter <= 0;
        serial_data <= 0;
        state <= `IDLE;
    end else begin
        case(state)
            `IDLE: begin
                if(!cs_n)
                    state <= `TRANSACTION;
                else
                    state <= `IDLE;
            end
            `TRANSACTION: begin
                //shift 1 bit to the right and concatenate the input
                serial_data <= {copi, serial_data[14:0]};
                sclk_edge_counter <= sclk_edge_counter + 1;

                if(sclk_edge_counter == 15) begin
                    sclk_edge_counter <= 0;
                    state <= `VALIDATION;
                end
                else begin
                    state <= `TRANSACTION;
                end
            end
            `VALIDATION: begin
                if(({1'b0,serial_data[7:1]} >= 8'b0) && ({1'b0,serial_data[7:1]} <= 8'd4)) begin
                    state <= `UPDATE;
                end
                else begin
                    state <= `IDLE;
                end
            end
            `UPDATE: begin
                state <= `IDLE;
            end
        endcase
    end
end

always @(*) begin
    case(state)
        `IDLE: begin
            out_reg_0 = 8'b0;
            out_reg_1 = 8'b0;
            out_reg_2 = 8'b0;
            out_reg_3 = 8'b0;
            out_reg_4 = 8'b0;
        end
        `TRANSACTION: begin
            out_reg_0 = 8'b0;
            out_reg_1 = 8'b0;
            out_reg_2 = 8'b0;
            out_reg_3 = 8'b0;
            out_reg_4 = 8'b0;
        end
        `VALIDATION: begin
            out_reg_0 = 8'b0;
            out_reg_1 = 8'b0;
            out_reg_2 = 8'b0;
            out_reg_3 = 8'b0;
            out_reg_4 = 8'b0;
        end
        `UPDATE: begin
            if({1'b0,serial_data[7:1]} == 8'b0) begin
                out_reg_0 = serial_data[15:8];
                out_reg_1 = 8'b0;
                out_reg_2 = 8'b0;
                out_reg_3 = 8'b0;
                out_reg_4 = 8'b0;
            end
            else if({1'b0,serial_data[7:1]} == 8'd1) begin
                out_reg_0 = 8'b0;
                out_reg_1 = serial_data[15:8];
                out_reg_2 = 8'b0;
                out_reg_3 = 8'b0;
                out_reg_4 = 8'b0;
            end
            else if({1'b0,serial_data[7:1]} == 8'd2) begin
                out_reg_0 = 8'b0;
                out_reg_1 = 8'b0;
                out_reg_2 = serial_data[15:8];
                out_reg_3 = 8'b0;
                out_reg_4 = 8'b0;
            end
            else if({1'b0,serial_data[7:1]} == 8'd3) begin
                out_reg_0 = 8'b0;
                out_reg_1 = 8'b0;
                out_reg_2 = 8'b0;
                out_reg_3 = serial_data[15:8];
                out_reg_4 = 8'b0;
            end
            else if({1'b0,serial_data[7:1]} == 8'd4) begin
                out_reg_0 = 8'b0;
                out_reg_1 = 8'b0;
                out_reg_2 = 8'b0;
                out_reg_3 = 8'b0;
                out_reg_4 = serial_data[15:8];
            end
        end
    endcase
end

endmodule