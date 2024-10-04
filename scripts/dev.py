from multiprocessing import Process
from timeit import default_timer as timer
import time
import os

def run_server(x):
    try:
        os.system('fastapi dev api/main.py')
    except Exception as ex:
        exit()

def run_web(x):
    try:
        os.system('cd web/ && yarn dev')
    except Exception as ex:
        exit()

if __name__ == '__main__':
    proc1 = Process(target=run_server, args=[1])
    proc2 = Process(target=run_web, args=[1])

    # start processes
    proc1.start()
    proc2.start()
