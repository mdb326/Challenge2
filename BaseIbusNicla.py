

from pyb import UART, LED

import sensor
import time

sensor.reset()  # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565)  # Set pixel format to RGB565 (or GRAYSCALE)
sensor.ioctl(sensor.IOCTL_SET_FOV_WIDE, True)
sensor.set_framesize(sensor.HQVGA)  # Set frame size to QVGA (320x240)
sensor.skip_frames(time=2000)  # Wait for settings take effect.

r_LED = LED(1)  # The red LED
g_LED = LED(2)  # The green LED
b_LED = LED(3)  # The blue LED
g_LED.on()
r_LED.off()
b_LED.off()
clock = time.clock()  # Create a clock object to track the FPS.
uart = UART("LP1", 115200, timeout_char=2000) # (TX, RX) = (P1, P0) = (PB14, PB15)

def checksum(arr, initial= 0):
    """ The last pair of byte is the checksum on iBus
    """
    sum = initial
    for a in arr:
        sum += a
    checksum = 0xFFFF - sum
    chA = checksum >> 8
    chB = checksum & 0xFF
    return chA, chB

def IBus_message(message_arr_to_send):
    msg = bytearray(32)
    msg[0] = 0x20
    msg[1] = 0x40
    for i in range(len(message_arr_to_send)):
        msg_byte_tuple = bytearray(message_arr_to_send[i].to_bytes(2, 'little'))
        msg[int(2*i + 2)] = msg_byte_tuple[0]
        msg[int(2*i + 3)] = msg_byte_tuple[1]

    # Perform the checksume
    chA, chB = checksum(msg[:-2], 0)
    msg[-1] = chA
    msg[-2] = chB

    uart.write(msg)

def refreshIbusConnection():
    while uart.any():
        uart_input = uart.read()
        print(uart_input)


thresholdsBanana = (5, 54, 15, 54, -20, 22)

while True:
    ############### Color detection here ###############

    #put color detection and such here
    xcenter = 0
    ycenter = 0
    width = 0
    height = 0

    clock.tick()  # Update the FPS clock.
    img = sensor.snapshot()  # Take a picture and return the image.
#    print(clock.fps())  # Note: OpenMV Cam runs about half as fast when connected
    # to the IDE. The FPS should increase once disconnected.

    blobs = img.find_blobs([thresholdsBanana], area_threshold=2500, merge=True)
    color_is_detected = False
    # Draw blobs
    for blob in blobs:
        # Draw a rectangle where the blob was found
        img.draw_rectangle(blob.rect(), color=(0,255,0))
        # Draw a cross in the middle of the blob
        img.draw_cross(blob.cx(), blob.cy(), color=(0,255,0))
        xcenter = blob.cx()
        ycenter = blob.cy()
        width = blob.rect()[2]
        height = blob.rect()[3]
        print(blob.cx()," ", blob.cy())
        print(blob.rect())
        #print(blob.rect()[2] * blob.rect()[3])
        color_is_detected = True





    flag = 0
    if (color_is_detected):
        g_LED.off()
        r_LED.off()
        b_LED.on()
        flag = 1 # when a color is detected make this flag 1
    else:
        g_LED.on()
        r_LED.off()
        b_LED.off()
    pixels_x = xcenter # put your x center in pixels
    pixels_y = ycenter # put your y center in pixels
    pixels_w = width # put your width in pixels (these have almost no affect on control (for now))
    pixels_h = height # put your height center in pixels (these have almost no affect on control (for now))
    ###############################




    messageToSend = [flag, pixels_x, pixels_y, pixels_w, pixels_h,0,0,0,0,0]

    refreshIbusConnection()
    IBus_message(messageToSend)
