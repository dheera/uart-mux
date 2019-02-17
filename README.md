# uart-mux

UART multiplexer/demultiplexer. Combines multiple low-bandwidth RS232 devices into one RS232 line for e.g. embedded hardware.

Currently using on an Jetson TX2 which has only one usable UART, which is fed multiplexed data from a Cortex M4 that is running an embedded version of this multiplexer to combine its multiple UARTs. They then get re-enumerated on the TX2 as virtual devices, e.g. /dev/imu0, /dev/gps0, /dev/barometer0, etc.
