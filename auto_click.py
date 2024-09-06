import pyautogui as pag
import time

start_time = time.time()
# print(pag.position())

while True:
    current_time = time.time()
    if current_time - start_time > 10:
        current_position = pag.position()
        pag.moveTo(1886, 601)
        pag.click()
        pag.moveTo(current_position)
        pag.click()
        start_time = current_time
