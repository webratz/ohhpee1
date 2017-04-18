#!/usr/bin/env python
import json
import os
from mutagen.aiff import IFFFile
import mutagen
from hurry.filesize import size
# notes https://2016.mrmcd.net/fahrplan/system/event_attachments/attachments/000/002/895/original/OP1_reverse_enginering_MRMCD2016.pdf
# https://www.operator-1.com/index.php?p=/discussion/2232/custom-firmware-on-the-op-1/p4

# Max Synth Sampler patches = 42
# Max Synth Synthesis patches = 100
# Max Drum Patches = 42


class OP1Aiff(object):
    def __init__(self, filename):
        # max filename length 10 chars
        self.filename = filename
        self.op1data = self._load_op1_data(self.filename)
        self._to_attrs(self.op1data)
        self.info = self._load_aiff_info(self.filename)
        self.filesize = self._get_size()

    def _load_op1_data(self, filename):
        f = open(filename, 'r')
        iff = IFFFile(f)
        appl =  iff.__getitem__(u'APPL')
        rawdata = appl.read()
        data = rawdata.split('op-1')[1]
        f.close()
        return json.loads(data)

    def _load_aiff_info(self, filename):
        return mutagen.aiff.AIFF(filename).info

    def _to_attrs(self, data):
        # just for convenience: set the loaded data as attributes of tje object
        for key in data:
            setattr(self, key, data[key])

    def _get_size(self):
        # filesize in bytes
        return os.path.getsize(self.filename)

    def summary(self):
        print "Name:\t%s" % self.name
        print "Type:\t%s" % self.type
        print "Len:\t%.2f sec" % self.info.length
        print "Size:\t%s" % size(self.filesize)
        print "Octave:\t%s" % self.octave
        if self.fx_active is True:
            print "FX:\t%s" % self.fx_type
        if self.lfo_active is True:
            print "LFO:\t%s" % self.lfo_type

        print ""







checkpath = "/home/andi/op1/packs/cuckoo/c-mix/op1/put-in-synth/c-mix"
for afile in os.listdir(checkpath):
    if afile.endswith(".aif"):
        patchfile = os.path.join(checkpath, afile)
        patch = OP1Aiff(patchfile)
        patch.summary()
        #print patch.data
