import instruments
import random

bpm = 400  # set the BPM
bpb = 8    # set the number of beats per bar

# This is a bit of a bodge to set-up the midi port to use.
# The numbering of ports is shown when b0rkenlive starts.
instruments.midi_instrument = instruments.Midi(1)


@instruments.midi
def drums(i,b,bar):
    i.seq(b, [35,-1,38,-1], chan=1)
    i.note(42, vel=random.random()*80+20, chan=1)


@instruments.midi
def synth(i,b,bar):
    i.seq(b, [32,35,37], vel=random.random()*80+20, chan=2)