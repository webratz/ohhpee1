# python imports
import os
import json

# 3rd party imports
from mutagen.aiff import IFFFile
import mutagen
from hurry.filesize import size


class OP1Aiff(object):
    """
    OP-1 creates normal aif files, altough they embed some json into the metadata
    this is currently read only
    """
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
        appl = iff.__getitem__(u'APPL')     # sorry for accessing internal functions, but TE hides the metadata well
        rawdata = appl.read()
        print rawdata
        data = rawdata.split('op-1')[1]
        f.close()
        return json.loads(data)

    def _write_op1_data(self, filename):
        """
        not yet working
        """
        f = open(filename, 'w')
        iff = IFFFile(f)
        appl = iff.__getitem__(u'APPL')     # sorry for accessing internal functions, but TE hides the metadata well
        print self.op1data
        data = "op-1%s" % json.dumps(self.op1data, sort_keys=True)
        print data
        appl.write(data)
        f.close()

    def _load_aiff_info(self, filename):
        return mutagen.aiff.AIFF(filename).info

    def _to_attrs(self, data):
        # just for convenience: set the loaded data as attributes of tje object
        for key in data:
            setattr(self, key, data[key])

    def _get_size(self):
        # filesize in bytes
        return os.path.getsize(self.filename)

    def check(self):
        if len(self.op1data['name']) > 10:
            # name may not be longer than 10 characters
            return False
        # TODO create validator for op1 json

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

# o = OP1Aiff('/Users/sie0003a/git/ohhpee1/packs/packs/synth/c-mix/angelina_bg.aif')
# o._write_op1_data(o.filename)
