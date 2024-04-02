from tqdm import tqdm
from time import sleep
import psutil, os

pid = os.getpid()
python_process = psutil.Process(pid)

#https://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python#:~:text=One%20can%20get%20real%20time%20CPU%20and%20RAM%20monitoring%20by%20combining%20tqdm%20and%20psutil.%20It%20may%20be%20handy%20when%20running%20heavy%20computations%20/%20processing.
with tqdm(total=100, desc='pros%', position=2) as prosbar, tqdm(total=100, desc='cpu%', position=1) as cpubar, tqdm(total=100, desc='ram%', position=0) as rambar:
    while True:
        rambar.n=psutil.virtual_memory().percent
        cpubar.n=psutil.cpu_percent()
        prosbar.n=python_process.cpu_percent()
        rambar.refresh()
        cpubar.refresh()
        prosbar.refresh()
        sleep(0.5)