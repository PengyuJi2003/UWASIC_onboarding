`define IDLE 2'b00
`define TRANSACTION 2'b01
`define VALIDATION 2'b01
`define UPDATE 2'b11

module spi_peripheral (
    input wire cs_n     // Active-low chip select signal
    input wire rst_n    // Active-low reset signal
    input wire sclk     // Clock signal from the controller
    input wire copi     // Controller out peripheral in
    output wire [7:0] reg_0    // register with address 0x00
    output wire [7:0] reg_1    // register with address 0x01
    output wire [7:0] reg_2    // register with address 0x02
    output wire [7:0] reg_3    // register with address 0x03
    output wire [7:0] reg_4    // register with address 0x04
);

reg [2:0] state;
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
                if({0,serial_data[7:1]} == 0x00) begin
                    reg_0 = serial_data[15:8];
                end
                else if({0,serial_data[7:1]} == 0x01) begin
                    reg_1 = serial_data[15:8];
                end
                else if({0,serial_data[7:1]} == 0x02) begin
                    reg_2 = serial_data[15:8];
                end
                else if({0,serial_data[7:1]} == 0x03) begin
                    reg_3 = serial_data[15:8];
                end
                else if({0,serial_data[7:1]} == 0x04) begin
                    reg_4 = serial_data[15:8];
                end
                else begin
                    state <= `IDLE;
                end
            end
        endcase
    end
end

always @*() begin
    case(state)
        `IDLE: begin
            reg_0 = 0x00;
            reg_1 = 0x00;
            reg_2 = 0x00;
            reg_3 = 0x00;
            reg_4 = 0x00;
        end
        `TRANSACTION: begin
            reg_0 = 0x00;
            reg_1 = 0x00;
            reg_2 = 0x00;
            reg_3 = 0x00;
            reg_4 = 0x00;
        end
        `VALIDATION: begin
            reg_0 = 0x00;
            reg_1 = 0x00;
            reg_2 = 0x00;
            reg_3 = 0x00;
            reg_4 = 0x00;
        end
        `UPDATE: begin
            if({0,serial_data[7:1]} == 0x00) begin
                reg_0 = serial_data[15:8];
                reg_1 = 0x00;
                reg_2 = 0x00;
                reg_3 = 0x00;
                reg_4 = 0x00;
            end
            else if({0,serial_data[7:1]} == 0x01) begin
                reg_0 = 0x00;
                reg_1 = serial_data[15:8];
                reg_2 = 0x00;
                reg_3 = 0x00;
                reg_4 = 0x00;
            end
            else if({0,serial_data[7:1]} == 0x02) begin
                reg_0 = 0x00;
                reg_1 = 0x00;
                reg_2 = serial_data[15:8];
                reg_3 = 0x00;
                reg_4 = 0x00;
            end
            else if({0,serial_data[7:1]} == 0x03) begin
                reg_0 = 0x00;
                reg_1 = 0x00;
                reg_2 = 0x00;
                reg_3 = serial_data[15:8];
                reg_4 = 0x00;
            end
            else if({0,serial_data[7:1]} == 0x04) begin
                reg_0 = 0x00;
                reg_1 = 0x00;
                reg_2 = 0x00;
                reg_3 = 0x00;
                reg_4 = serial_data[15:8];
            end
        end
    endcase
end

endmodule