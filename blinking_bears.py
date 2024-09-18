from gpiozero import LED
from time import sleep
import os
import sys
import subprocess
from time import sleep
from subprocess import Popen
from openai import OpenAI
import RPi.GPIO as GPIO
import time
import asyncio

OPENAI_API_KEY = "sk-proj-"
client = OpenAI(api_key = OPENAI_API_KEY)


GPIO.setmode(GPIO.BOARD)

GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)#Button to GPIO22
GPIO.setup(16, GPIO.OUT)  #LED to GPIO23
GPIO.setup(18, GPIO.OUT)  #LED to GPIO24
led_state = False  # Initially, the LED is off
last_statement = ""

async def get_transcript():
    global led_state, last_statement
    print("getting transcript")
    audio_file = open("test.wav", "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    print(transcription.text.lower(), flush=True)
    last_statement = transcription.text.lower()
    print("led state ", led_state)
    if (led_state):
        print("true")
        if ("dumplings" in last_statement):
            for i in range(3):
                GPIO.output(16, False)
                await asyncio.sleep(0.3)
                GPIO.output(16, True)
                await asyncio.sleep(0.3)
            last_statement = ""
        if ("honey" in last_statement):
            print("hi honey")
            for i in range(3):
                GPIO.output(18, False)
                await asyncio.sleep(0.3)
                GPIO.output(18, True)
                await asyncio.sleep(0.3)
            last_statement = ""
    

async def listen():
    print("in listen")
    while True:
        print("recording")
        proc = subprocess.Popen(['arecord -D plughw:2,0 --duration=3 -f S16_LE test.wav'], shell=True)
        await asyncio.sleep(3)
        proc.terminate()
        asyncio.create_task(get_transcript())
        
async def toggle_light():
    global led_state
    print("checking light")
    try:
        asyncio.create_task(listen())
        while True:
            button_state = GPIO.input(15)
            if button_state == False:                
                led_state = not led_state
                GPIO.output(16, led_state)  # Set LED to new state
                GPIO.output(18, led_state)  # Set LED to new state
                print(f"LED {'ON' if led_state else 'OFF'}")
                await asyncio.sleep(0.5)  # Debounce delay to avoid multiple toggles on one press
                print("TL ", led_state)
            await asyncio.sleep(0.1)
            
                
    except Exception as error:
        # handle the exception
        print("An exception occurred:", error)
        GPIO.cleanup()

asyncio.run(toggle_light())
