#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mian - Mine analysis - Graph block types to altitude in a Minecraft save
game <http://github.com/l0b0/mian>

Default syntax:

mian [-b|--blocks=<list>] [-l|--list] <World directory>

Options:

-b, --blocks    Specify block types to include as a comma-separated list, using
                either the block types or hex values from the list.
-l, --list      List available block types and their names (from
                <http://www.minecraftwiki.net/wiki/Data_values>).
-n, --nether    Graph The Nether instead of the ordinary world.
--log           Render logarithmic output.
-s, --save      Save the result to file instead of showing an interactive GUI.

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
__version__ = '0.9.3'

from binascii import unhexlify
from getopt import getopt, GetoptError
from glob import glob
from gzip import GzipFile
import matplotlib as mpl
from operator import itemgetter
from os.path import basename, join
from signal import signal, SIGPIPE, SIG_DFL
from StringIO import StringIO
import struct
import sys
import warnings
import zlib
from optparse import OptionParser
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np

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


def plot(counts, block_type_hexes, title, options):
    """
    Actual plotting of data.

    @param counts: Integer counts per layer.
    @param block_type_hexes: Subset of BLOCK_TYPES.keys().
    """
    o = options
    if o.save_path:
        mpl.use('Agg')

    import matplotlib.pyplot as plt

    if o.plot_mode == 'normal':
        fig = plt.figure()
        fig.canvas.set_window_title(title)

        if o.log:
            for index, block_counts in enumerate(counts):
                plt.semilogy(
                    block_counts,
                    label=BLOCK_TYPES[block_type_hexes[index]][0],
                    linewidth=1,
                    nonposy='clip',
                    picker=3)
        else:
            for index, block_counts in enumerate(counts):
                plt.plot(
                    block_counts,
                    label=BLOCK_TYPES[block_type_hexes[index]][0],
                    linewidth=1,
                    picker=3)

        def on_pick(pickevent):
            thisline = pickevent.artist
            print "Toggeling", thisline.get_label()
            if thisline.get_alpha() == None or thisline.get_alpha() == 1:
                thisline.set_alpha(0.3)
            else:
                thisline.set_alpha(1)

            fig.canvas.draw()

        fig.canvas.mpl_connect('pick_event', on_pick)

        plt.legend()
        plt.xlabel(LABEL_X)
        plt.ylabel(LABEL_Y)

    elif o.plot_mode == 'colormap' or o.plot_mode == 'wireframe':
        X, Z, min_chunk_x, min_chunk_z, max_chunk_x, max_chunk_z, Data = counts

        if o.plot_mode == 'colormap':
            Data = np.rot90(Data, 3) # north on the top of the image
            im = plt.imshow(Data,
                cmap=cm.jet,
                extent=(max_chunk_z, min_chunk_z, max_chunk_x, min_chunk_x))
            # Don't use interpolation, chunk as pixels
            im.set_interpolation('nearest')
            plt.colorbar()
            plt.ylabel('X axis, negative to North (blocks)')
            plt.xlabel('Z axis, negative to East (blocks)')
            plt.title(title + '(north on top of image)')

        elif o.plot_mode == 'wireframe':
            fig = plt.figure()
            ax = Axes3D(fig)
            ax.plot_wireframe(Z, X, Data, rstride=1, cstride=1)
            plt.xlabel('X axis, negative to North (chunks)')
            plt.ylabel('Z axis, negative to East (chunks)')
            plt.title(title + '(north on top of image)')

    if o.save_path == None:
        plt.show()
    else:
        print 'Saving image to: %s' % save_path
        plt.savefig(save_path, dpi = o.dpi)


def mian(world_dir, block_type_hexes, options):
    """
    Runs through the MCR files and gets the layer counts for the plot.

    @param world_dir: Path to existing Minecraft world directory.
    @param block_type_hexes: Subset of BLOCK_TYPES.keys().
    @param nether: Whether or not to graph The Nether.
    """
    o = options
    title = basename(world_dir.rstrip('/'))

    # All world blocks are stored in .mcr files
    if o.nether:
        mcr_files = glob(join(world_dir, 'DIM-1/region/*.mcr'))
        title += ' Nether'
    else:
        mcr_files = glob(join(world_dir, 'region/*.mcr'))

    if o.plot_mode == 'colormap' or o.plot_mode == 'wirframe':
        title += ' - map for block {0}'.format(
            BLOCK_TYPES[block_type_hexes[0]][0])

    title += ' - mian %s' % __version__

    if not mcr_files:
        raise Usage('Invalid savegame path.')

    total_counts = generate_graph_data(world_dir,
                    mcr_files, block_type_hexes, o.plot_mode)

    plot(total_counts, block_type_hexes, title, options)


def generate_graph_data(world_dir, mcr_files, block_type_hexes, plot_mode):
    if plot_mode == 'normal':
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

        return total_counts

    elif plot_mode == 'colormap' or plot_mode == 'wireframe':

        # Find the maximun and minimun region coordinates
        min_x = 0
        min_z = 0
        max_x = 0
        max_z = 0

        for mcr_file in mcr_files:
            region_x, region_z = get_region_coords(mcr_file)
            min_x = min(min_x, region_x)
            min_z = min(min_z, region_z)
            max_x = max(max_x, region_x)
            max_z = max(max_z, region_z)

        # Find the chunk coordinates of these region coordinates
        min_chunk_x = min_x * 32
        min_chunk_z = min_z * 32
        max_chunk_x = max_x * 32 + 31
        max_chunk_z = max_z * 32 + 31

        # Find the block coordinates of these chunk coordinates
        min_block_x = min_chunk_x * 16
        min_block_z = min_chunk_z * 16
        max_block_x = max_chunk_x * 16 + 15
        max_block_z = max_chunk_z * 16 + 15

        # Generate a grid for the graph using numpy
        X = np.arange(min_chunk_x, max_chunk_x + 1)
        Z = np.arange(min_chunk_z, max_chunk_z + 1)
        X, Z = np.meshgrid(X, Z)

        # Generate data
        Data = np.zeros((X.shape[0]-1, X.shape[1]-1))

        total_chunks = X.shape[0] * X.shape[1]
        progress = 1
        print "Scanning chunks... "

        for index_x in xrange(abs(min_chunk_x) + abs(max_chunk_x)):
            for index_z in xrange(abs(min_chunk_z) + abs(max_chunk_z)):

                # be careful with the index in the np.array!
                counts = count_chunk_blocks(world_dir,
                    (X[index_z][index_x], Z[index_z][index_x]),
                     block_type_hexes[0])
                if counts < 0:
                    # To properly show zones without chunks
                    Data[index_z][index_x] = -10

                else:
                    Data[index_z][index_x] = counts

                progress += 1
                if progress % 1000 == 0:
                    print int(float(progress) / total_chunks * 100), "%"

        print "100%... Done!"

        return (X, Z, min_block_x, min_block_z, max_block_x, max_block_z, Data)


def extract_region_chunk_blocks(mcr_file, coordsXZ):
    """ Takes a region file and a local chunk coordinates
    and returns the blocks as a string.

    Returns None if the chunk is not in the region file,
    or if the region file doesn't exist.
    """

    def location(coordsXZ):
        return 4 * ((coordsXZ[0] % 32) + (coordsXZ[1] % 32) * 32)

    try:
        file_pointer = open(mcr_file, 'rb')
    except IOError:
        return None

    file_pointer.seek(location(coordsXZ))

    # Locate sector
    location_raw = file_pointer.read(LOCATION_BYTES)
    location = struct.unpack(
        LOCATION_FORMAT,
        LOCATION_PADDING + location_raw)[0]
    if location == 0:
        return None

    # Get chunk and decompress
    file_pointer.seek(location * SECTOR_BYTES)
    chunk_length = struct.unpack(
        UNSIGNED_LONG_FORMAT,
        file_pointer.read(CHUNK_LENGTH_BYTES))[0]
    chunk_compression = struct.unpack(
        UNSIGNED_CHAR_FORMAT,
        file_pointer.read(COMPRESSION_BYTES))[0]
    chunk_raw = file_pointer.read(chunk_length)
    chunk = decompress(chunk_raw, chunk_compression)

    # Extract the blocks of the chunk
    index = chunk.find(BLOCKS_NBT_TAG)
    blocks = chunk[
        (index + len(BLOCKS_NBT_TAG)):(index + len(BLOCKS_NBT_TAG) + 32768)]

    return blocks


def get_region_coords(mcr_file):
    """ Takes the name of a file with or without the full path and
    returns 2 integers with the coordinates of a region file """

    regionXZ = basename(mcr_file).lstrip('r.').split('.', 2)[:2]
    return int(regionXZ[0]), int(regionXZ[1])


def count_chunk_blocks(world_dir, chunkXZ, block_type):
    """ Takes the global chunk coordinates, the world_dir
    and the block type for count.

    Returns the count of block or -1 if the chunk, or the
    region file doesn't exist.
    """

    # Determine the propper region file.
    rXZ = (chunkXZ[0] / 32, chunkXZ[1] / 32)
    mcr_file = world_dir.rstrip('/') + "/region/r." + str(rXZ[0]) + \
        "." + str(rXZ[1]) + ".mcr"

    # Determine chunk coords in region file.
    local_chunkXZ = (divmod(chunkXZ[0], 32)[1], + divmod(chunkXZ[1], 32)[1])

    blocks = extract_region_chunk_blocks(mcr_file, local_chunkXZ)

    if blocks == None:
        return -1

    count = blocks.count(block_type)

    return count


def count_blocks(region_blocks, block_type_hexes):
    """
    This function counts blocks per layer.

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
    """
    This function creates a string which contains
    all blocks within the chunks in a given region file.

    Returns a string with all the chunk blocks in NBT format
    inside a region file concatenated.
    """

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
            (index + len(BLOCKS_NBT_TAG) + 4):(index +
            len(BLOCKS_NBT_TAG) + 4 + 32768)]
            # after the NBT tag there is always
            # four bytes with \x00 \x00 \x80 \x00, ignore them!
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

    # things for --help and --version options
    prog = 'mian'
    description = 'mian: Mine analysis - Graph block types to altitude \
        in a Minecraft save game <http://github.com/l0b0/mian>'
    usage = 'usage: %prog [-b|--blocks=<list>] [-l|--list] <World directory>'
    version = __version__

    # populating the parser
    parser = OptionParser(usage = usage, version = version,
        description = description, prog = prog)

    parser.add_option("-b", "--blocks", dest="block_type_names", default = None,
        help="Specify block types to include as a comma-separated list, using either the block types or hex values from the list.")
    parser.add_option("-l", "--list", action = "store_true", dest = "print_blocks",
        help = "List available block types and their names (from <http://www.minecraftwiki.net/wiki/Data_values>)")
    parser.add_option("-n", "--nether", action = "store_true", default = False, dest = "nether",
        help = "Graph The Nether instead of the ordinary world.")
    parser.add_option("--log", action = "store_true", default = False, dest = "log",
        help = "Render logarithmic output.")
    parser.add_option("-o", "--output", default = None, dest = "save_path",
        help = "Save the result to file instead of showing an interactive GUI.")
    parser.add_option("--dpi", type = 'int', default = 100, dest = "dpi",
        help = "The resolution in dots per inch for the --output option. Default = 100 (800x600).")
    parser.add_option("--plot-mode", "-p", type = 'string', default = 'normal', dest = 'plot_mode',
        help = "The plot modes are: normal, colormap and wireframe (3D). Warning! Wireframe can be really resource hungry with big maps")

    (options, args) = parser.parse_args()

    # print block types if asked for
    if options.print_blocks:
        print_block_types()
        return 0

    # check things
    if len(args) == 0:
        parser.error('need to specify a save directory')

    if len(args) != 1:
        parser.error('need to specify exactly one save directory')

    if not options.dpi > 0:
        parser.error('dpi should be an interger greater than 0, given \'%s\'' % options.dpi)

    plot_modes = ["normal", "colormap", "wireframe"]
    if options.plot_mode not in plot_modes:
        parser.error('The plot mode \'{0}\' is not recognized'.format(options.plot_mode))

    world_dir = args[0]

    # Look up block_types
    if options.block_type_names == None:
        block_type_names = DEFAULT_BLOCK_TYPES
    else:
        block_type_names = options.block_type_names.split(',')

    block_type_hexes = []
    for block_type_name in block_type_names:
        found_hexes = lookup_block_type(block_type_name)
        for found_hex in found_hexes:
            if found_hex not in block_type_hexes:  # Avoid duplicates
                block_type_hexes.append(found_hex)

    if block_type_hexes == []:
        parser.error('No proper blocks given!')

    mian(world_dir, block_type_hexes, options)


if __name__ == '__main__':
    sys.exit(main())
