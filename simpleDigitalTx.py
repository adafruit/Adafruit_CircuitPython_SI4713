#!/usr/bin/python3
#
#  simpleDigitalTx.py 2021 by Stefan Heimers


# If using a Raspberry Pi, set I2S to hifiberry-dac
# mode, play a 48k stereo file with vlc and select
# the correct audio device from the menu
#
# Put the following two lines (without the #) in
# /boot/config.txt and reboot the Raspi
#
# dtoverlay=hifiberry-dac
# dtoverlay=i2s-mmap


# Raspi             Adafruit Si4713
#
# Pin 9 (Ground)    GND
# Pin 1 (3.3V)      Vin
# Pin 3 (SDA)       SDA
# Pin 5 (SCL)       SCL
# Pin 29(GPIO5)     RST (Reset)

# Digital I2S input (nach AN383.pdf)
# Raspi             Adafruit Si4713
# 
# Pin 35 (PCM_FS)   LOut/DFS (Pin 14)
# Pin 40 (PCM_DOUT) ROut/Din (Pin 13)
# Pin 12 (PCM_CLK)  Dclk (Pin 17)
#                   Rclk (Pin 9)    <- external Quartz-Oscillator 

from time import sleep
import board
import busio
import digitalio
import adafruit_si4713

# Configuration
txFrequency = 87.5 # Frequenz in MHz
stationName = b'TSTRADIOXXX' # Stationsname für RDS, max 8 Zeichen
txPower     = 88



# SI4721 digital input formats (AN332.pdf, page 32)
hifiBerry = 0b0000000000001000 # rising edge, I2S, Stereo, 16 bit
#hifiBerry = 0b0000000010001000 # falling edge, I2S, Stereo, 16 bit
riI2sStereo24 = 0b0000000000001010 # rising edge, I2S, Stereo, 24 bit
riI2sStereo8 = 0b0000000000001011 # rising edge, I2S, Stereo, 8 bit
riLjStereo8 = 0b0000000000111011 # rising edge, left justified, Stereo, 8 bit


i2c = busio.I2C(board.SCL, board.SDA)
si_address = 0x11 # I2C Adressen: 0x63 für CS=hi am Si4713/Si4721, 0x11 für CS=low
si_reset = digitalio.DigitalInOut(board.D5) # GPIO5, = pin 29 am Raspi, nicht nötig bei Kondensatorreset (Qwiic board)
#si_reset=None

tx = adafruit_si4713.SI4713(i2c, address=si_address, reset=si_reset, timeout_s=0.5, audio='digital')
if not tx:
    print ("error! couldn't start SI4713 or 21 transmitter!")

print("turn on audio now")
sleep(10)

try:
     tx.digital_input_sample_rate = 0xBB80
except:
    print ("Can't set 'digital input sample rate'")
try:
     tx.digital_input_format = hifiBerry;
except:
    print ("Can't set 'digital input format'")

tx.tx_power = txPower
tx.tx_frequency_khz = int(1000 * txFrequency)

tx.configure_rds(0xADAF, station=stationName[0:7], rds_buffer=b'Radiotext test!')
print("ready...")
sleep(100)
print("finished...")
