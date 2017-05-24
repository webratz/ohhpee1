from __future__ import print_function
import os
import sys
import time
import shutil

import usb.core
import usb.util
import psutil


def get_visible_children(d):
    return list(filter(lambda x: x[0] != '.', os.listdir(d)))


def get_visible_folders(d):
    return list(filter(lambda x: os.path.isdir(os.path.join(d, x)), get_visible_children(d)))


class OP1Mount(object):
    """
    everything related to the mounting of the OP1
    """
    def __init__(self):
        self.OP1_BASE_DIRS = set(['tape', 'album', 'synth', 'drum'])

    def find_mount(self):
        """
        tries to find the OP1 mount path
        returns the mountpoint
        """
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if partition.fstype == 'msdos':
                dirs = get_visible_folders(partition.mountpoint)

                if set(dirs) == self.OP1_BASE_DIRS:
                    return partition.mountpoint

        # did not find anything
        return None

    def wait_mount(self, timeout=15):
        """
        wait for the mount to come availlable
        returns the mountpoint
        """
        i = 0
        try:
            while i < timeout:
                time.sleep(1)
                mount = self.find_mount()
                if mount is not None:
                    return mount
                i += 1
            raise ValueError("timed out waiting for mount of OP-1 device. Make sure its connected and start again")
        except KeyboardInterrupt:
            sys.exit(0)


class OP1Device(object):
    """
    this represents the actual OP-1 Hardware device
    """
    def __init__(self):
        # USB IDs
        self.VENDOR_TE = 0x2367
        self.PRODUCT_OP1 = 0x0002

        self.op1mount = OP1Mount()
        self.mountpath = None

        self.packs = []

    def is_ready(self):
        """
        is the device in a state where we can interact with its storage
        """
        if self.op1mount.find_mount() and self._is_connected():
            return True
        return False

    def _is_connected(self):
        """
        check if the device is connected via USB
        """
        return usb.core.find(idVendor=self.VENDOR_TE, idProduct=self.PRODUCT_OP1) is not None

    def ensure_connection(self):
        if not self._is_connected():
            print("Please connect your OP-1 via USB and put it in DISK mode (Shift+COM -> 3) ...")
            self._wait_for_connection()

    def _wait_for_connection(self, timeout=30):
        """
        waits for USB connection of the OP1
        timeout is specified in seconds
        """
        counter = 0
        try:
            while timeout > counter:
                time.sleep(1)
                counter += 1
                if self._is_connected():
                    break
        except KeyboardInterrupt:
            sys.exit(0)

    def mount(self):
        self.mountpath = self.op1mount.wait_mount()
        return self.mountpath

    def _get_installed_packs(self):
        if os.path.isdir(self.mountpath):
            for i in ['synth', 'tape']:
                for pack in os.walk(os.path.join('%s/%s' % (self.mountpath, i), '.')).next()[1]:
                    self.packs.append(OP1Pack(pack, self, i))




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
        print("copied pack %s to %s" % (self.name, self.pcpath))

    def push(self):
        """
        get a pack folder from the local PC and push it to the OP-1 device
        """
        print("copied pack %s to %s" % (self.name, self.packpath))
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
