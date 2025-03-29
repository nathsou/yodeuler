#!/usr/bin/env python3
import os
import sys
import termios
import tty
import select

def configure_serial(fd, baud=9600):
    """
    Configure the serial port:
      - Baud rate (default 9600)
      - 8 data bits, no parity, 1 stop bit (8N1)
      - Raw (non-canonical) mode
    """
    attrs = termios.tcgetattr(fd)
    
    # Set baud rate for input and output.
    baud_const = getattr(termios, 'B{}'.format(baud))
    attrs[4] = baud_const  # ispeed
    attrs[5] = baud_const  # ospeed

    # Control mode flags:
    # - Clear parity enable (no parity)
    # - Clear CSTOPB (1 stop bit)
    # - Clear current character size mask, then set 8 data bits (CS8)
    attrs[2] &= ~termios.PARENB
    attrs[2] &= ~termios.CSTOPB
    attrs[2] &= ~termios.CSIZE
    attrs[2] |= termios.CS8

    # Local modes: disable canonical mode, echo, signal generation, etc.
    attrs[3] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    
    # Apply the configuration immediately.
    termios.tcsetattr(fd, termios.TCSANOW, attrs)

def main():
    if len(sys.argv) < 2:
        print("Usage: {} <serial device> [baud]".format(sys.argv[0]))
        sys.exit(1)
    
    serial_device = sys.argv[1]
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 9600

    # Open the serial device for read/write, non-blocking, and no controlling terminal.
    try:
        fd = os.open(serial_device, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except Exception as e:
        print("Error opening serial device '{}': {}".format(serial_device, e))
        sys.exit(1)
    
    # Configure the serial port.
    configure_serial(fd, baud)

    # Save current terminal settings for stdin and set raw mode.
    stdin_fd = sys.stdin.fileno()
    old_stdin_attrs = termios.tcgetattr(stdin_fd)
    tty.setraw(stdin_fd)

    print("Serial monitor started on {} @ {} baud.".format(serial_device, baud))
    print("Press ESC or 'q' to exit.")

    try:
        while True:
            # Use select to wait until either stdin or the serial device has data.
            rlist, _, _ = select.select([stdin_fd, fd], [], [])
            
            if stdin_fd in rlist:
                # Read input from keyboard
                try:
                    input_data = os.read(stdin_fd, 1024)
                except OSError:
                    input_data = b""
                if input_data:
                    # Check for exit keys: ESC (ASCII 27) or 'q'
                    if b'\x1b' in input_data or b'q' in input_data:
                        break
                    os.write(fd, input_data)
            
            if fd in rlist:
                # Read data from the serial device
                try:
                    serial_data = os.read(fd, 1024)
                except OSError:
                    serial_data = b""
                if serial_data:
                    # Decode the bytes (with replacement for any errors) and write to stdout.
                    sys.stdout.write(serial_data.decode('utf-8', errors='replace'))
                    sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Exiting serial monitor.")
    finally:
        # Restore the original terminal settings for stdin.
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_stdin_attrs)
        os.close(fd)

if __name__ == '__main__':
    main()
