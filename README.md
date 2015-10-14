b0rkenlive
==========

b0rkenlive is a live coding music/midi framework built with python. It breaks a lot and does bad and weird things with the python module import system.


Usage
-----
Currently you have to run b0rkenlive on files in the root of the git directory.

python3 b0rkenlive.py demo.py

All function with an instrument decorator get run in parallel on separate threads. The functions are called every beat.

Into the functions is passed the instrument to play, the current beat and the current bar.

Editing and saving the file causes all functions to get reloaded on the start of the next bar.


```Python demo.py
import instruments
import random

bpm = 400  # set the BPM
bpb = 8    # set the number of beats per bar

# This is a bit of a bodge to set-up the midi port to use.
# The numbering of ports is shown when b0rkenlive starts.
instruments.midi_instrument = instruments.Midi(0)


@instruments.midi
def drums(i,b,bar):
    i.seq(b, [35,-1,38,-1], chan=1)
    i.note(42, vel=random.random()*80+20, chan=1)


@instruments.midi
def synth(i,b,bar):
    i.seq(b, [32,35,37], vel=random.random()*80+20, chan=2)
```

Install
-------

Dependencies

* python3
* pip3

Install the following python packages from pip.
```sudo pip3 install rtmidi2 decorator watchdog```



