#!/usr/bin/env python3
import importlib
import linecache
import inspect
import rtmidi2
import random
import time
import sys
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from queue import Queue

bpm = 125.0  # Beats per minute
bpb = 4      # Beats per bar


def __show_title__():
    python_references = ["lumberjacks", "Brian", "silly walks", "fork handles", "four candles"]
    print("===================================================")
    print("    __    ____       __              ___           ")
    print("   / /_  / __ \_____/ /_____  ____  / (_)   _____  ")
    print("  / __ \/ / / / ___/ //_/ _ \/ __ \/ / / | / / _ \ ")
    print(" / /_/ / /_/ / /  / ,< /  __/ / / / / /| |/ /  __/ ")
    print("/_.___/\____/_/  /_/|_|\___/_/ /_/_/_/ |___/\___/  ")
    print("                                                   ")
    print("livecoding from b0rkestra with <3 &", random.choice(python_references))
    print("===================================================")
    print("                                                   ")
    output_ports = rtmidi2.get_out_ports()
    print("MIDI ports")
    print("----------")
    for index, port in enumerate(output_ports):
        print("["+str(index)+"]", port)
    print("")

class FunctionThread(Thread):
    def __init__(self, target, *args):
        super(FunctionThread, self).__init__()
        self._target = target
        self._args = args

    def run(self):
        num_args = len(inspect.getargspec(self._target).args)
        if num_args == 1:
            self._target(None)
        if num_args == 2:
            self._target(None, self._args[0])
        if num_args == 3:
            self._target(None, self._args[0], self._args[1])
        if num_args == 4:
            self._target(None, self._args[0], self._args[1], self._args[2])


class InstrumentThread(Thread):
    def __init__(self):
        super(InstrumentThread, self).__init__()
        self.delete_queue = Queue()
        self.create_queue = Queue()
        self.stop_flag = False

    def run(self):
        global bpm
        global bpb

        instrument_functions = {}

        try:
            beat_count = 0
            bar_count = 0
            while not self.stop_flag:
                #create any new instruments
                while not self.create_queue.empty():
                    instrument_functions = self.create_queue.get()

                for beat in range(bpb):
                    time.sleep(60.0/bpm)
                    #trigger instruments
                    for instrument_id in instrument_functions.keys():
                        func = instrument_functions[instrument_id]
                        #if hasattr(func, '__wrapped__'):
                        #    print (dir(func.__wrapped__))
                        #    if hasattr(func.__wrapped__, 'is_instrument'):
                        #        pass
                        t = FunctionThread(func, beat_count, bar_count)
                        t.start()

                    beat_count += 1
                bar_count += 1
        except KeyboardInterrupt:
            return

    def stop(self):
        print("stopping instrument thread")
        self.stop_flag = True


class ModuleReloadHandler(FileSystemEventHandler):
    def __init__(self, filename):
        self.filename = filename
        self.module_name = os.path.splitext(filename)[0]
        self.instruments = {}
        self.instrument_thread = InstrumentThread()
        self.instrument_thread.start()
        self.setup_called = False
        self.reload()

    def on_modified(self, event):
        if os.path.split(event.src_path)[1] == self.filename:
            print ("Reloading ", self.filename)
            self.reload()

    def reload(self):
        global bpm
        global bpb

        importlib.invalidate_caches()
        if not hasattr(self, "music"):
            try:
                self.music = importlib.import_module(self.module_name)
            except SyntaxError as e:
                print("Syntax Error - ", e.filename, "line number", e.lineno)
                return
        else:
            try:
                importlib.reload(self.music)
            except SyntaxError as e:
                print("Syntax Error - ", e.filename, "line number", e.lineno)
                return

        module_lines = open(self.filename).read().split('\n')
        function_names = [l[4:].split('(')[0] for l in module_lines if l.startswith('def ')]

        linecache.clearcache()  # deal with bug https://bugs.python.org/issue1218234
        module_instruments = {}

        attrs = [attr for attr in dir(self.music) if not attr.startswith('__')]
        for attr in attrs:
            if attr == 'bpm':
                bpm = getattr(self.music, attr)
            if attr == 'bpb':
                bpb = getattr(self.music, attr)
            obj = getattr(self.music, attr)
            #if hasattr(obj, '__call__'):
            if callable(obj) and attr in function_names:
                if attr == 'setup':
                    if not self.setup_called:
                        print('Setting up file')
                        obj()
                        self.setup_called = True
                else:
                    module_instruments[attr] = obj

        #create functions
        self.instrument_thread.create_queue.put(module_instruments)
        #find functions to remove

        self.instruments = module_instruments


def main():
    __show_title__()
    if len(sys.argv) < 2:
        print("Please specify a file to play")
        print("")
        return

    filedirpath, filename = os.path.split(os.path.realpath(sys.argv[1]))
    module_reload_handler = ModuleReloadHandler(filename)

    observer = Observer()
    observer.schedule(module_reload_handler, filedirpath)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        module_reload_handler.instrument_thread.stop()
        observer.stop()
    observer.join()
    return


if __name__ == '__main__':
    main()
