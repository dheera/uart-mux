#!/usr/bin/env python3
import serial, pty, os
import time
import signal

INPUT = "/dev/ttyTHS2"
INPUT_BAUD = 57600
OUTPUTS = ["/dev/ttyEXT0", "/dev/gps0", "/dev/roboclaw0", "/dev/ttyEXT2"]

output_devices = []
input_ser = serial.Serial(INPUT, INPUT_BAUD)

for output_symlink in OUTPUTS:
    master, slave = pty.openpty()
    master_name = os.ttyname(master)
    slave_name = os.ttyname(slave)

    if os.path.lexists(output_symlink):
        os.unlink(output_symlink)
        print("unlinked %s" % output_symlink)

    os.symlink(slave_name, output_symlink)
    print("created symlink %s -> %s" % (slave_name, output_symlink))

    output_devices.append({
        "master": master,
        "slave": slave,
        "symlink": output_symlink,
    })

do_exit = False
def signal_handler(sig, frame):
    global do_exit
    print("SIGINT received")
    do_exit = True

signal.signal(signal.SIGINT, signal_handler)

def process_inbound(ser):
    if ser.read() != b'\xaa':
        return

    packet_address = ord(ser.read())
    if not packet_address:
        print("[warn] received bad address")
        return

    packet_length = ord(ser.read())
    if not packet_length:
        print("[warn] received bad length")
        return

    packet_payload = ser.read(packet_length)
    if not packet_payload or len(packet_payload) != packet_length:
        print("[warn] length doesn't match payload")
        return

    packet_checksum = ord(ser.read())
    if not packet_checksum:
        print("[warn] bad checksum")
        return

    return packet_address, packet_payload, packet_checksum

if __name__ == "__main__":
    while not do_exit:
        if input_ser.in_waiting > 0:
            result = process_inbound(input_ser)
            if result:
                address, payload, checksum = result
                if address >= len(OUTPUTS):
                    print("[warn] received data for address %d when there are only %d devices" % (address, len(OUTPUTS)))
                else:
                    os.write(output_devices[address]["master"], payload)

    input_ser.close()
    for device in output_devices:
        os.unlink(device["symlink"])
        print("unlinked %s" % device["symlink"])

