#!/usr/bin/env python

# python imports
import os
import json
import shutil
import datetime

# 3rd party imports
from mutagen.aiff import IFFFile
import mutagen
from hurry.filesize import size

class OP1Device(object):
    """
    represents the beloved OP-1
    """
    def __init__(self):
        self.mountpath = '/Volumes/NO NAME'     # no trailing slash
        self.packs = []
        self._get_installed_packs()

    def _get_installed_packs(self):
        if os.path.isdir(self.mountpath):
            for i in ['synth', 'tape']:
                for pack in os.walk(os.path.join('%s/%s' % (self.mountpath, i), '.')).next()[1]:
                    self.packs.append(OP1Pack(pack, self, i))
        else:
            print "OP1 not mounted"

    def _get_usb_info(self):
        import usb
        busses = usb.busses()
        for bus in busses:
            devices = bus.devices
            for dev in devices:
                #print dir(dev)
                # print dev.idVendor #, dev.iManufacturer, dev.iProduct, dev.filename, dev.dev

                if dev.dev.product == 'OP-1':
                    print dev.dev.idVendor
                    print dir(dev.dev)
                #print usb.util.get_string(dev, 256, dev.iSerialNumber)
                #print usb.util.get_string(dev, 256, dev.iManufacturer)


class OP1Pack(object):
    """
    packtype is either 'synth' or 'drum'
    See Guide: https://www.teenageengineering.com/guides/op-1/synthesizer-mode#5.8
    There are several file operations, heres the naming we use for now
    PC -> OP1   : PUSH
    OP1 -> PC   : PULL
    """
    def __init__(self, name, op1device, packtype):
        self.name = name    # either user for a UserPack or something else
        self.op1device = op1device      # device object
        self.packtype = packtype        # synth or drum
        self.userpack = None            # is this a User pack? (1-8)
        self.packpath = None            # on OP-1 device
        self.pcpath = None              # on PC
        self._determine_paths()

    def __repr__(self):
        return 'OP-1 Pack: %s %s' % (self.name, self.packtype)

    def _determine_paths(self):
        """
        we build up an opinonated file structure
        """
        # do we have a user pack here (1-8), or some other pack (eg from cuckoo)
        if 'user' in self.name:
            self.userpack = True
        else:
            self.userpack = False

        # where do we find the pack on the OP-1 device?
        self.packpath = "%s/%s/%s/" % (self.op1device.mountpath, self.packtype, self.name)

        # if we have a userpack we add a timestamp, as we most likely do not want to overwrite
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        if self.userpack:
            destname = "user-%s" % (timestamp)
        else:
            destname = self.name

        # Where will we store the pack on the PC?
        self.pcpath = os.path.expanduser('~/ohhpee1/packs/%s/%s' % (self.packtype, destname))

    def pull(self):
        """
        get the given pack from the OP-1 device and store it on the local computer
        """
        shutil.copytree(self.packpath, self.pcpath)
        print "copied pack %s to %s" % (self.name, self.pcpath)

    def push(self):
        """
        get a pack folder from the local PC and push it to the OP-1 device
        """
        print "copied pack %s to %s" % (self.name, self.packpath)
        #shutil.copytree(self.pcpath, self.packpath)

    def check(self):
        """
        check some general things
        """
        checkpath = self.pcpath
        if not os.path.isdir(checkpath):
            self.pull()
        for afile in os.listdir(checkpath):
            if afile.endswith(".aif"):
                patchfile = os.path.join(checkpath, afile)
                patch = OP1Aiff(patchfile)
                patch.summary()


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


d = OP1Device()
print d.packs
print d._get_usb_info()
#pack = OP1Pack('c-mix', d, 'synth')
#pack.check()
