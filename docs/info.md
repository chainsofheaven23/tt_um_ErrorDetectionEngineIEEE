<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project is a high-reliability Serial Error Correction Engine that combines two layers of data protection: Hamming(12,8) encoding and a CRC-8 checksum.

Encoding Layer 1 (Hamming): When an 8-bit data byte is loaded via ui_in, the engine immediately generates 4 parity bits using a Hamming(12,8) XOR tree, creating a 12-bit protected word.

Encoding Layer 2 (CRC): The 12-bit Hamming word is then fed into a secondary XOR tree to calculate an 8-bit CRC checksum.

Serialization: These two components are combined into a 20-bit hybrid codeword.

Output: Upon a load trigger, the engine sets a busy flag high and shifts the 20-bit codeword out serially through uo_out[0] at the rate of one bit per clock cycle.

## How to test

To test the engine, follow these steps using the input pins provided:

Reset: Apply a low pulse to rst_n to clear the internal shift register and bit counter.

Input Data: Set your 8-bit test pattern on the ui_in[7:0] pins.

Trigger: Pulse the load signal (uio_in[0]) high for exactly one clock cycle while the engine is not busy.

Monitor:

Observe the busy signal (uo_out[1]) going high.

Capture the serial bitstream on uo_out[0] for the next 20 clock cycles.

The engine is ready for a new load once busy returns to low.

## External hardware

This project does not strictly require specific external PMODs, but for physical verification, the following are recommended:

Logic Analyzer: To capture and verify the 20-bit serial output sequence against the expected Hamming-CRC values.

Microcontroller (Optional): An Arduino or ESP32 can be used to automate the load pulse and read the serial stream for high-speed testing.
