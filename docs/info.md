<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project involves an SPI-controlled PWM peripheral. The design operates at 10 MHz and uses SPI communication at ~100 KHz to configure registers that control output enables, PWM enables, and duty cycles. The system comprises two main modules: an SPI Peripheral for register management and a PWM Peripheral for signal generation.

For this project, I designed the spi_peripheral module and created Python scripts to verify the pwm_peripheral module.
