import time                   # Allows use of time.sleep() for delays
import ubinascii              # Conversions between binary data and various encodings
import machine                # Interfaces with hardware components
import dht
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd
from secrets import credentials  # Importing the credentials for Adafruit IO

# BEGIN SETTINGS
publish_interval = 40
last_publish = time.time()
# led pin initialization for Raspberry Pi Pico W
onboard_led = Pin("LED", Pin.OUT)
tempSensor = dht.DHT11(machine.Pin(21))  # DHT11 Constructor

buzzer = Pin(22, Pin.OUT)

LED_Pin_Red = Pin(26, Pin.OUT)
LED_Pin_Green = Pin(27, Pin.OUT)
LED_Pin_Blue = Pin(28, Pin.OUT)


# LCD setup
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
celsiusSymbol = bytearray([0x0C, 0x12, 0x12, 0x0C, 0x00, 0x00, 0x00, 0x00])
lcd.custom_char(0, celsiusSymbol)


# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = credentials["AIO_USERNAME"]
AIO_KEY = credentials["AIO_KEY"]
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_humidity_FEED = "nikolaosmoskoglou/feeds/humidity"
AIO_temperature_FEED = "nikolaosmoskoglou/feeds/temperature"


# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)
client.connect()

while True:
    try:
        if ((time.time() - last_publish) < publish_interval):
            lcd.clear()
            onboard_led.value(1)
            tempSensor.measure()
            temperature_value, humidity_value = tempSensor.temperature(), tempSensor.humidity()
            if temperature_value > 23:
                LED_Pin_Red.value(0)
                LED_Pin_Green.value(1)
                LED_Pin_Blue.value(0)
                time.sleep(2)
                LED_Pin_Red.value(0)
                LED_Pin_Green.value(0)
                LED_Pin_Blue.value(0)
                buzzer.value(1)
                time.sleep(1)
                buzzer.value(0)
                lcd.putstr("Temperature")
                lcd.move_to(0, 1)
                lcd.putstr("exceeded 23" + chr(0) + "C")
                time.sleep(5)
                lcd.clear()
            lcd.putstr(f"Temperature:{temperature_value}{chr(0)}C")
            lcd.putstr(f"Humidity:   {humidity_value}%")
            print(
                f"Publishing: {temperature_value} to {AIO_temperature_FEED}... ", end='')
            client.publish(topic=AIO_temperature_FEED,
                           msg=str(temperature_value))
            print("Done")
            print(
                f"Publishing: {humidity_value} to {AIO_humidity_FEED}... ", end='')
            client.publish(topic=AIO_humidity_FEED,
                           msg=str(humidity_value))
            print("Done")
    except Exception as e:
        print("Error occured: " + str(e))
    finally:
        onboard_led.value(0)
        last_publish = time.time()
        time.sleep(15)
