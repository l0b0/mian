#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mian - Mine analysis - Graph block types to altitude in a Minecraft save
game <http://github.com/l0b0/mian>

Default syntax:

mian [-b|--blocks=<list>] [-l|--list] <World directory>

Options:

-b, --blocks    Specify block types to include as a comma-separated list, using
                either the block types or hex values from the list.
-l, --list      List available block types and their names (from
                <http://www.minecraftwiki.net/wiki/Data_values>).
-n, --nether    Graph The Nether instead of the ordinary world.

Description:

Creates a file with a graph of how much the given materials occur at each
vertical layer of the map.

Examples:

$ mian ~/.minecraft/saves/World1
Creates graph of default materials in World1.

$ mian -b 01,dirt,09,sand ~/.minecraft/saves/World1
Ditto, showing only the specified block types.

$ mian -b 56,57,58,59,5a,5b -n ~/.minecraft/saves/World1
Graph all the materials new to The Nether.

$ mian --list
Show a list of block types which can be searched for.
"""

__author__ = 'Pepijn de Vos, Victor Engmark'
__copyright__ = 'Copyright (C) 2010-2011 Pepijn de Vos, Victor Engmark'
__credits__ = ['Pepijn de Vos', 'Victor Engmark', 'Alejandro Aguilera']
__maintainer__ = 'Victor Engmark'
__email__ = 'victor.engmark@gmail.com'
__license__ = 'GPL v3 or newer'
__url__ = 'https://github.com/l0b0/mian/wiki'
__version__ = '0.9'

from binascii import unhexlify
from getopt import getopt, GetoptError
from glob import glob
from gzip import GzipFile
import matplotlib.pyplot as plt
from operator import itemgetter
from os.path import basename, join
from signal import signal, SIGPIPE, SIG_DFL
from StringIO import StringIO
import struct
import sys
import warnings
import zlib

from blocks import BLOCK_TYPES, UNUSED_NAME

#: For binascii.unhexlify()
HEX_DIGITS = '0123456789abcdef'

#: When running without --blocks
DEFAULT_BLOCK_TYPES = [
    'clay',
    'coal ore',
    'diamond ore',
    'gold ore',
    'iron ore',
    'obsidian',
    '49']

#: Height
CHUNK_SIZE_Y = 128

#: Depth
CHUNK_SIZE_Z = 16

#: Width
CHUNK_SIZE_X = CHUNK_SIZE_Y * CHUNK_SIZE_Z

#: Plot X axis
LABEL_X = 'Layer'

#: Plot Y axis
LABEL_Y = 'Count'

#: <http://www.minecraftwiki.net/wiki/Beta_Level_Format#Structure>
KIBIBYTE = 2 ** 10
UNSIGNED_LONG_BYTES = 4
UNSIGNED_LONG_FORMAT = '>L'
UNSIGNED_CHAR_BYTES = 1
UNSIGNED_CHAR_FORMAT = '>B'
SECTOR_BYTES = 4 * KIBIBYTE
SECTOR_INTS = SECTOR_BYTES / UNSIGNED_LONG_BYTES

#: <http://www.minecraftwiki.net/wiki/Beta_Level_Format#Chunk_Location>
LOCATION_OFFSET_BYTES = 3
SECTOR_COUNT_BYTES = 1
LOCATION_BYTES = LOCATION_OFFSET_BYTES + SECTOR_COUNT_BYTES
LOCATION_FORMAT = '>LB'
LOCATION_PADDING = '\x00' * (struct.calcsize(LOCATION_FORMAT) - LOCATION_BYTES)

#: <http://www.minecraftwiki.net/wiki/Beta_Level_Format#Chunk_Timestamps>
TIMESTAMP_BYTES = UNSIGNED_LONG_BYTES

#: <http://www.minecraftwiki.net/wiki/Beta_Level_Format#Chunk_Data>
CHUNK_LENGTH_BYTES = UNSIGNED_LONG_BYTES
COMPRESSION_BYTES = 1
COMPRESSION_GZIP = 1
COMPRESSION_DEFLATE = 2

BLOCKS_NBT_TAG = "Blocks"

#: Avoid 'Broken pipe' message when canceling piped command
signal(SIGPIPE, SIG_DFL)


def lookup_block_type(block_type):

    """
    Find block types based on input string.

    Looks for a hex value iff the block type is two hex digits. In other words,
    if you specify `-b be` you'll get the block with hex value 'be', not
    bedrock.

    @param block_type: Name or hex ID of a block type.
    @return: Hex IDs of matching blocks.
    """

    if block_type is None or len(block_type) == 0:
        warnings.warn('Empty block type')
        return []

    block_type = block_type.lower()

    if [char in HEX_DIGITS for char in block_type] == [True, True]:
        # 2 hex digits
        return [unhexlify(block_type)]

    # Name substring search, could have multiple results
    result = []
    for block_hex, block_names in BLOCK_TYPES.iteritems():  # Block
        for block_name in block_names:  # Synonyms
            if block_name.lower().find(block_type) != -1:
                result.append(block_hex)
    if result == []:
        warnings.warn('Unknown block type %s' % block_type)

    return result


def print_block_types():
    """Print the block block_names and hexadecimal IDs"""
    for block_hex, block_names in sorted(
        BLOCK_TYPES.iteritems(),
        key=itemgetter(0)):
        if block_names != [UNUSED_NAME]:
            sys.stdout.write(hex(ord(block_hex))[2:].upper().zfill(2) + ' ')
            sys.stdout.write(', '.join(block_names) + '\n')


def plot(counts, block_type_hexes, title):
    """
    Actual plotting of data.

    @param counts: Integer counts per layer.
    @param block_type_hexes: Subset of BLOCK_TYPES.keys().
    """
    fig = plt.figure()
    fig.canvas.set_window_title(title)

    for index, block_counts in enumerate(counts):
        plt.plot(
            block_counts,
            label=BLOCK_TYPES[block_type_hexes[index]][0],
            linewidth=1)

    plt.legend()
    plt.xlabel(LABEL_X)
    plt.ylabel(LABEL_Y)

    plt.show()


def mian(world_dir, block_type_hexes, nether):
    """
    Runs through the MCR files and gets the layer counts for the plot.

    @param world_dir: Path to existing Minecraft world directory.
    @param block_type_hexes: Subset of BLOCK_TYPES.keys().
    @param nether: Whether or not to graph The Nether.
    """

    title = basename(world_dir.rstrip('/'))

    # All world blocks are stored in DAT files
    if nether:
        mcr_files = glob(join(world_dir, 'DIM-1/region/*.mcr'))
        title += ' Nether'
    else:
        mcr_files = glob(join(world_dir, 'region/*.mcr'))

    title += ' - mian %s' % __version__

    if mcr_files == []:
        raise Usage('Invalid savegame path.')

    print "There are %s regions in the savegame directory" % len(mcr_files)

    # Create total_counts list and write a list of 128 zeros on it for
    # every scanned block.
    total_counts = [[] for i in xrange(len(block_type_hexes))]
    for block_type_index in range(len(block_type_hexes)):
        for layer in range(128):
            total_counts[block_type_index].append(int(0))

    total_mcr_files = len(mcr_files)
    file_counter = 1

    for mcr_file in mcr_files:

        print "Reading %# 5u / %u" % (file_counter, total_mcr_files)

        region_blocks = extract_region_blocks(mcr_file)
        counts = count_blocks(region_blocks, block_type_hexes)

        # Sum up the results
        for block_type_index in range(len(block_type_hexes)):
            for layer in range(128):
                total_counts[block_type_index][layer] += \
                    counts[block_type_index][layer]

        file_counter += 1

    if total_counts == [[] for i in xrange(len(block_type_hexes))]:
        raise Usage('No blocks were recognized.')

    print "Done!"

    plot(total_counts, block_type_hexes, title)


def count_blocks(region_blocks, block_type_hexes):
    """ This function counts blocks per layer.

    Returns a list with one element per scanned block.
    Each element is a list with 128 elements the amount
    of that block in that layer.
    """

    layers = [region_blocks[i::128] for i in range(128)]
    counts = [[] for i in xrange(len(block_type_hexes))]

    for block_type_index in range(len(block_type_hexes)):
        bt_hex = block_type_hexes[block_type_index]
        for layer in layers:
            counts[block_type_index].append(layer.count(bt_hex))

    return counts


def extract_region_blocks(mcr_file):
    """ This function creates a string which contains
    all blocks within the chunks in a given region file.

    Returns a string with all the chunk blocks in NBT format
    inside a region file concatenated. """

    # Unpack block format
    # <http://www.minecraftwiki.net/wiki/Beta_Level_Format>

    locations = []

    file_pointer = open(mcr_file, 'rb')

    # Locations sector
    while file_pointer.tell() < SECTOR_BYTES:
        location_raw = file_pointer.read(LOCATION_BYTES)
        location = struct.unpack(
            LOCATION_FORMAT,
            LOCATION_PADDING + location_raw)[0]
        if location != 0:
            locations.append(location)

    locations.sort()

    region_blocks = ''

    for offset in locations:
        file_pointer.seek(offset * SECTOR_BYTES)
        chunk_length = struct.unpack(
            UNSIGNED_LONG_FORMAT,
            file_pointer.read(CHUNK_LENGTH_BYTES))[0]
        chunk_compression = struct.unpack(
            UNSIGNED_CHAR_FORMAT,
            file_pointer.read(COMPRESSION_BYTES))[0]
        chunk_raw = file_pointer.read(chunk_length)
        chunk = decompress(chunk_raw, chunk_compression)

        # Extract the blocks from the chunk
        index = chunk.find(BLOCKS_NBT_TAG)
        blocks = chunk[
            (index + len(BLOCKS_NBT_TAG)):(index + len(BLOCKS_NBT_TAG) + 32768)]
        region_blocks += blocks

    return region_blocks


def decompress(string, method):
    """
    Decompress the given string with either of the
    """

    assert(method in (COMPRESSION_GZIP, COMPRESSION_DEFLATE))
    if method == COMPRESSION_GZIP:
        with GzipFile(fileobj=StringIO(string)) as gzip_file:
            return gzip_file.read()

    if method == COMPRESSION_DEFLATE:
        return zlib.decompress(string)


class Usage(Exception):
    """Command-line usage error"""

    def __init__(self, msg):
        super(Usage, self).__init__(msg)
        self.msg = msg + '\nSee --help for more information.'


def main(argv=None):
    """Argument handling."""

    if argv is None:
        argv = sys.argv

    # Defaults
    block_type_names = DEFAULT_BLOCK_TYPES
    nether = False

    try:
        try:
            opts, args = getopt(
                argv[1:],
                'b:lnh',
                ['blocks=', 'list', 'nether', 'help'])
        except GetoptError, err:
            raise Usage(str(err))

        for option, value in opts:
            if option in ('-b', '--blocks'):
                block_type_names = value.split(',')
            elif option in ('-n', '--nether'):
                nether = True
            elif option in ('-l', '--list'):
                print_block_types()
                return 0
            elif option in ('-h', '--help'):
                print __doc__
                return 0
            else:
                raise Usage('Unhandled option %s.' % option)

        if len(args) == 0:
            raise Usage('You need to specify a save directory.')

        if len(args) != 1:
            raise Usage('You need to specify exactly one save directory.')

        world_dir = args[0]

        # Look up block_types
        block_type_hexes = []
        for block_type_name in block_type_names:
            found_hexes = lookup_block_type(block_type_name)
            for found_hex in found_hexes:
                if found_hex not in block_type_hexes:  # Avoid duplicates
                    block_type_hexes.append(found_hex)

        mian(world_dir, block_type_hexes, nether)

    except Usage, err:
        sys.stderr.write(err.msg + '\n')
        return 2


if __name__ == '__main__':
    sys.exit(main())
