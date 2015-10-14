import time
import decorator
import rtmidi2
from threading import Thread
from queue import Queue

#from pythonosc import osc_message_builder
#from pythonosc import udp_client

class Instrument():
    def seq(self, beat, notes):
        index = beat % len(notes)
        self.note(notes[index])

    def note(self, val):
        print("playing", val)

    def n(self, val):
        self.note(val)

    def chord(self, vals):
        for val in vals:
            self.note(val)

    def c(self, vals):
        self.chord(vals)


class Midi(Instrument, Thread):
    def __init__(self, port=0):
        super().__init__()
        self.midi = rtmidi2.MidiOut()
        self.port = port
        self.midi.open_port(self.port)
        self.note_queue = Queue()
        self.start()

    def run(self):
        on_notes = []
        try:
            while True:
                #create any new instruments
                while not self.note_queue.empty():
                    note = self.note_queue.get()
                    print("note", note[1])
                    self.midi.send_noteon(note[0], note[1], note[2])
                    on_notes.append([note, note[3]])
                time.sleep(0.005)
                for n in on_notes:
                    n[1] -= 0.005
                turn_off = [n for n in on_notes if n[1] < 0.0]
                for n_off in turn_off:
                    note = n_off[0]
                    print("off", note[1])
                    self.midi.send_noteoff(note[0], note[1])

                on_notes = [n for n in on_notes if n[1] > 0.0]
        except KeyboardInterrupt:
            return

    def note(self, val, vel=100, duration=0.5, chan=0):
        if val < 0:
            return
        self.note_queue.put((chan, val, vel, duration))

    def chord(self, vals, vel=100, duration=0.5, chan=0):
        for v in vals:
            self.note_queue.put((chan, v, vel, duration))
        #self.midi.send_noteon_many(0, vals, vels)

    def seq(self, beat, notes, vel=100, duration=0.5, chan=0):
        index = beat % len(notes)
        self.note(notes[index], vel=vel, duration=duration, chan=chan)


class Test(Instrument):
    def __init__(self):
        pass

    def note(self, val):
        print("Test Playing: ", val)


# class Dirt(Instrument):
#     def __init__(self):
#         self.conn = udp_client.UDPClient('127.0.0.1', 7771)

#     def note(self, val):
#         msg = osc_message_builder.OscMessageBuilder(address="/play")
#         msg.add_arg(1, "i")     # ?
#         msg.add_arg(1, "i")     # ?
#         msg.add_arg(1, "i")     # ?
#         msg.add_arg("808/BD/BD0000.WAV", 's')    # sound
#         msg.add_arg(0.0, "f")     # offset
#         msg.add_arg(0.0, "f")     # begin
#         msg.add_arg(1.0, "f")     # end
#         msg.add_arg(1.0, "f")     # speed
#         msg.add_arg(0.0, "f")     # velocity
#         msg.add_arg(" ", "s")      # vowel
#         msg.add_arg(0.0, "f")     # cut-off
#         msg.add_arg(0.0, "f")     # resonance
#         msg.add_arg(0.0, "f")     # accelerate
#         msg.add_arg(0.0, "f")     # shape
#         msg.add_arg(1, "i")     # kriole
#         msg.add_arg(1.0, "f")     # gain
#         msg.add_arg(0, "i")     # cut
#         msg.add_arg(0.0, "f")     # delay
#         msg.add_arg(-1.0, "f")    # delaytime
#         msg.add_arg(-1.0, "f")    # delayfeedback
#         msg.add_arg(0.0, "f")     # crush
#         msg.add_arg(1, "i")     # coarse
#         msg.add_arg(0.0, "f")     # hcutoff
#         msg.add_arg(0.0, "f")     # hresonance
#         msg.add_arg(0.0, "f")     # bandf
#         msg.add_arg(0.0, "f")     # bandq
#         msg.add_arg("rate", "s")  # unit
#         msg.add_arg(1, "i")     # loop

#         msg = msg.build()
#         self.conn.send(msg)
#         print('dirt', val)


# dirt_instrument = Dirt()
test_instrument = Test()
midi_instrument = Midi(0)

# @decorator.decorator
# def dirt(func, *args, **kw):
#     func.is_instrument = True
#     return func(dirt_instrument, *args[1:])


@decorator.decorator
def test(func, *args, **kw):
    print(kw)
    func.is_instrument = True
    return func(test_instrument, *args[1:])


@decorator.decorator
def midi(func, *args, **kw):
    func.is_instrument = True
    return func(midi_instrument, *args[1:])
