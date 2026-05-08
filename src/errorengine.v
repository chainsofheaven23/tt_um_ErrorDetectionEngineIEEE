module serial_error_engine (
    input  wire       clk,
    input  wire       rst_n,
    input  wire [7:0] data_in,
    input  wire [1:0] select,     // Changed to 2-bit as you only use 3 modes
    output reg  [7:0] serial_out  // Removed trailing comma
);

    // --- Internal Combinational Logic ---
    wire [11:0] h_bus;
    wire [7:0]  c_res;
    wire [19:0] shift_reg; // Changed to wire because it's purely combinational here

    // Hamming (12,8) XOR Tree
    assign h_bus[0]  = data_in[0]^data_in[1]^data_in[3]^data_in[4]^data_in[6];
    assign h_bus[1]  = data_in[0]^data_in[2]^data_in[3]^data_in[5]^data_in[6];
    assign h_bus[2]  = data_in[0];
    assign h_bus[3]  = data_in[1]^data_in[2]^data_in[3]^data_in[7];
    assign h_bus[4]  = data_in[1];
    assign h_bus[5]  = data_in[2];
    assign h_bus[6]  = data_in[3];
    assign h_bus[7]  = data_in[4]^data_in[5]^data_in[6]^data_in[7];
    assign h_bus[8]  = data_in[4];
    assign h_bus[9]  = data_in[5];
    assign h_bus[10] = data_in[6];
    assign h_bus[11] = data_in[7];

    // CRC-8 XOR Tree
    assign c_res[0] = h_bus[11]^h_bus[10]^h_bus[8]^h_bus[4]^h_bus[3]^h_bus[0];
    assign c_res[1] = h_bus[11]^h_bus[10]^h_bus[9]^h_bus[8]^h_bus[5]^h_bus[4]^h_bus[1]^h_bus[0];
    assign c_res[2] = h_bus[11]^h_bus[10]^h_bus[9]^h_bus[6]^h_bus[5]^h_bus[2]^h_bus[1]^h_bus[0];
    assign c_res[3] = h_bus[11]^h_bus[10]^h_bus[7]^h_bus[6]^h_bus[3]^h_bus[2]^h_bus[1];
    assign c_res[4] = h_bus[11]^h_bus[8]^h_bus[7]^h_bus[4]^h_bus[3]^h_bus[2];
    assign c_res[5] = h_bus[9]^h_bus[8]^h_bus[5]^h_bus[4]^h_bus[3];
    assign c_res[6] = h_bus[10]^h_bus[9]^h_bus[6]^h_bus[5]^h_bus[4];
    assign c_res[7] = h_bus[11]^h_bus[10]^h_bus[7]^h_bus[6]^h_bus[5];
    
    // Combine to 20-bit vector
    assign shift_reg = {h_bus, c_res};

    // Combinational Output Multiplexer
    always @(*) begin
        case (select)
            2'b00:   serial_out = {4'b0000, shift_reg[19:16]}; // MSB bits
            2'b01:   serial_out = shift_reg[15:8];             // Middle bits
            2'b10:   serial_out = shift_reg[7:0];              // LSB bits (CRC)
            default: serial_out = data_in;                     // Bypass mode
        endcase
    end

endmodule
