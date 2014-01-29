# Copyright (c) 2014, Fortylines LLC
#   All rights reserved.

import json, logging, os, re

import vcd

from responsive_waves import settings
from responsive_waves.utils import leafs_match

LOGGER = logging.getLogger(__name__)

def _as_abspath(vcd_path):
    '''Returns a pathname to a fixture for a VCD file.'''
    vcd_abspath = os.path.join(settings.BUILDTOP, vcd_path)
    if not os.path.exists(vcd_abspath):
        if getattr(settings, 'USE_FIXTURES', False):
            return os.path.join(settings.FIXTURE_DIRS[0],
                                os.path.basename(vcd_path))
    return vcd_abspath


class VCDFileBackend:

    @staticmethod
    def load_variables(vcd_path):
        """
        Returns a scope tree (as a python dictionnary) of variables defined
        in *vcd_path*.
        """
        vcd_abspath = _as_abspath(vcd_path + '.vcd')
        with open(vcd_abspath) as vcd_file:
            defs = vcd.definitions(vcd_file)
            return json.loads(defs)['definitions']
        return None

    @staticmethod
    def load_values(vcd_path, variables, start_time, end_time, resolution):
        '''
        Returns a json-formatted version of the time records
        for the VCD file pointed by *job_id*/*vcd_path*.
        '''
        LOGGER.debug("[load_values] %s %s [%ld, %ld[ at %d",
                     vcd_path, variables, start_time, end_time, resolution)
        values = {}
        leafs = leafs_match(VCDFileBackend.load_variables(vcd_path), variables)
        id_codes = [ leaf.encode('ascii','ignore') for leaf in leafs.keys() ]
        vcd_abspath = _as_abspath(vcd_path + '.vcd')
        if os.path.exists(vcd_abspath):
            data = {}
            with open(vcd_abspath) as vcd_file:
                data = vcd.values(vcd_file, id_codes,
                                  start_time, end_time, resolution)
        # XXX It is kind of silly. We unserialize the JSON-encoded string
        #     *data* for the response to JSON-encode it again. I haven't
        #     found out how to avoid this (see: rest_framework/response.py:37)
        # XXX Right now we also use the json decoded data to transform
        #     the key from id_code to variable pk since that is what
        #     the js browser is expecting.
            loaded_values = json.loads(data)
            for id_code, names in leafs.iteritems():
                for path in names:
                    values[path] = loaded_values[id_code]
        return values

