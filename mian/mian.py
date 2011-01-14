#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mian - Mine analysis - Graph block types to height in a Minecraft save game
<http://github.com/l0b0/mian>

Default syntax:

mian [-b|--blocks=<list>] [-l|--list] <World directory>

Options:

-b, --blocks    Specify block types to include as a comma-separated list, using
                either the block types or hex values from the list.
-l, --list      List available block types (from
                <http://www.minecraftwiki.net/wiki/Data_values>).
-n, --nether    Graph The Nether instead of the ordinary world.

Description:

Creates a file with a graph of how much the given materials occur at each
layer of the map.

Examples:

$ mian ~/.minecraft/saves/World1
Creates World1.png in the current directory with the graph.

$ mian -b 01,dirt,09,sand ~/.minecraft/saves/World1
Ditto, showing only the specified block types.

$ mian -b 56,57,58,59,5a,5b -n ~/.minecraft/saves/World1
Graph all the materials new to The Nether.

$ mian --list
Show a list of block types which can be searched for.
"""

__author__ = 'Pepijn de Vos, Victor Engmark'
__copyright__ = 'Copyright (C) 2010 Pepijn de Vos, Victor Engmark'
__credits__ = ['Pepijn de Vos', 'Victor Engmark']
__maintainer__ = 'Victor Engmark'
__email__ = 'victor.engmark@gmail.com'
__license__ = 'GPL v3 or newer'

from binascii import unhexlify
from getopt import getopt, GetoptError
from glob import glob
import matplotlib.pyplot as plt
from nbt.nbt import NBTFile
from operator import itemgetter
from os.path import join, split
from signal import signal, SIGPIPE, SIG_DFL
import sys
import warnings

HEXDIGITS = '0123456789abcdef'

UNUSED_NAME = '<unused>'

# The first name is the canocical one (for the moment).
# Subsequent names are synonyms.
BLOCK_TYPES = {
    '\x00': ['Air'],
    '\x01': ['Stone'],
    '\x02': ['Grass'],
    '\x03': ['Dirt'],
    '\x04': ['Cobblestone'],
    '\x05': [
        'Wood',
        'Log'],
    '\x06': ['Sapling'],
    '\x07': [
        'Bedrock',
        'Adminium'],
    '\x08': ['Water'],
    '\x09': ['Stationary water'],
    '\x0a': ['Lava'],
    '\x0b': ['Stationary lava'],
    '\x0c': ['Sand'],
    '\x0d': ['Gravel'],
    '\x0e': ['Gold ore'],
    '\x0f': ['Iron ore'],
    '\x10': ['Coal ore'],
    '\x11': ['Log'],
    '\x12': ['Leaves'],
    '\x13': ['Sponge'],
    '\x14': ['Glass'],
    '\x15': ['Red cloth'],
    '\x16': ['Orange cloth'],
    '\x17': ['Yellow cloth'],
    '\x18': ['Lime cloth'],
    '\x19': ['Green cloth'],
    '\x1a': ['Aqua green cloth'],
    '\x1b': ['Cyan cloth'],
    '\x1c': ['Blue cloth'],
    '\x1d': ['Purple cloth'],
    '\x1e': ['Indigo cloth'],
    '\x1f': ['Violet cloth'],
    '\x20': ['Magenta cloth'],
    '\x21': ['Pink cloth'],
    '\x22': ['Black cloth'],
    '\x23': ['Gray / white cloth'],
    '\x24': ['White cloth'],
    '\x25': ['Yellow flower'],
    '\x26': ['Red rose'],
    '\x27': ['Brown mushroom'],
    '\x28': ['Red mushroom'],
    '\x29': ['Gold block'],
    '\x2a': ['Iron block'],
    '\x2b': [
        'Double slab',
        'Double step'],
    '\x2c': [
        'Stone slab',
        'Step'],
    '\x2d': ['Brick'],
    '\x2e': ['TNT'],
    '\x2f': ['Bookshelf'],
    '\x30': [
        'Moss stone',
        'Mossy cobblestone'],
    '\x31': ['Obsidian'],
    '\x32': ['Torch'],
    '\x33': ['Fire'],
    '\x34': [
        'Monster spawner',
        'Mob spawner'],
    '\x35': ['Wooden stairs'],
    '\x36': ['Chest'],
    '\x37': ['Redstone wire'],
    '\x38': ['Diamond ore'],
    '\x39': ['Diamond block'],
    '\x3a': ['Workbench'],
    '\x3b': ['Crops'],
    '\x3c': ['Soil'],
    '\x3d': ['Furnace'],
    '\x3e': ['Burning furnace'],
    '\x3f': ['Sign post'],
    '\x40': ['Wooden door'],
    '\x41': ['Ladder'],
    '\x42': [
        'Minecart tracks',
        'Rails'],
    '\x43': ['Cobblestone stairs'],
    '\x44': ['Wall sign'],
    '\x45': ['Lever'],
    '\x46': ['Stone pressure plate'],
    '\x47': ['Iron door'],
    '\x48': ['Wooden pressure plate'],
    '\x49': ['Redstone ore'],
    '\x4a': ['Glowing redstone ore'],
    '\x4b': ['Redstone torch [off]'],
    '\x4c': ['Redstone torch [on]'],
    '\x4d': ['Stone button'],
    '\x4e': ['Snow'],
    '\x4f': ['Ice'],
    '\x50': ['Snow block'],
    '\x51': ['Cactus'],
    '\x52': ['Clay'],
    '\x53': [
        'Reed',
        'Bamboo',
        'Papyrus'],
    '\x54': ['Jukebox'],
    '\x55': ['Fence'],
    '\x56': ['Pumpkin'],
    '\x57': [
        'Netherrack',
        'Bloodstone',
        'Hellstone',
        'Netherstone',
        'Red mossy cobblestone'],
    '\x58': [
        'Soul sand',
        'Hell mud',
        'Mud',
        'Nethermud',
        'Slow sand'],
    '\x59': [
        'Lightstone',
        'Brittle gold',
        'Brightstone',
        'Australium',
        'Brimstone'],
    '\x5a': ['Portal'],
    '\x5b': ['Jack-o-lantern'],
    '\x5c': ['Cake block'],
    '\x5d': [UNUSED_NAME],
    '\x5e': [UNUSED_NAME],
    '\x5f': [UNUSED_NAME],
    '\x60': [UNUSED_NAME],
    '\x61': [UNUSED_NAME],
    '\x62': [UNUSED_NAME],
    '\x63': [UNUSED_NAME],
    '\x64': [UNUSED_NAME],
    '\x65': [UNUSED_NAME],
    '\x66': [UNUSED_NAME],
    '\x67': [UNUSED_NAME],
    '\x68': [UNUSED_NAME],
    '\x69': [UNUSED_NAME],
    '\x6a': [UNUSED_NAME],
    '\x6b': [UNUSED_NAME],
    '\x6c': [UNUSED_NAME],
    '\x6d': [UNUSED_NAME],
    '\x6e': [UNUSED_NAME],
    '\x6f': [UNUSED_NAME],
    '\x70': [UNUSED_NAME],
    '\x71': [UNUSED_NAME],
    '\x72': [UNUSED_NAME],
    '\x73': [UNUSED_NAME],
    '\x74': [UNUSED_NAME],
    '\x75': [UNUSED_NAME],
    '\x76': [UNUSED_NAME],
    '\x77': [UNUSED_NAME],
    '\x78': [UNUSED_NAME],
    '\x79': [UNUSED_NAME],
    '\x7a': [UNUSED_NAME],
    '\x7b': [UNUSED_NAME],
    '\x7c': [UNUSED_NAME],
    '\x7d': [UNUSED_NAME],
    '\x7e': [UNUSED_NAME],
    '\x7f': [UNUSED_NAME],
    '\x80': [UNUSED_NAME],
    '\x81': [UNUSED_NAME],
    '\x82': [UNUSED_NAME],
    '\x83': [UNUSED_NAME],
    '\x84': [UNUSED_NAME],
    '\x85': [UNUSED_NAME],
    '\x86': [UNUSED_NAME],
    '\x87': [UNUSED_NAME],
    '\x88': [UNUSED_NAME],
    '\x89': [UNUSED_NAME],
    '\x8a': [UNUSED_NAME],
    '\x8b': [UNUSED_NAME],
    '\x8c': [UNUSED_NAME],
    '\x8d': [UNUSED_NAME],
    '\x8e': [UNUSED_NAME],
    '\x8f': [UNUSED_NAME],
    '\x90': [UNUSED_NAME],
    '\x91': [UNUSED_NAME],
    '\x92': [UNUSED_NAME],
    '\x93': [UNUSED_NAME],
    '\x94': [UNUSED_NAME],
    '\x95': [UNUSED_NAME],
    '\x96': [UNUSED_NAME],
    '\x97': [UNUSED_NAME],
    '\x98': [UNUSED_NAME],
    '\x99': [UNUSED_NAME],
    '\x9a': [UNUSED_NAME],
    '\x9b': [UNUSED_NAME],
    '\x9c': [UNUSED_NAME],
    '\x9d': [UNUSED_NAME],
    '\x9e': [UNUSED_NAME],
    '\x9f': [UNUSED_NAME],
    '\xa0': [UNUSED_NAME],
    '\xa1': [UNUSED_NAME],
    '\xa2': [UNUSED_NAME],
    '\xa3': [UNUSED_NAME],
    '\xa4': [UNUSED_NAME],
    '\xa5': [UNUSED_NAME],
    '\xa6': [UNUSED_NAME],
    '\xa7': [UNUSED_NAME],
    '\xa8': [UNUSED_NAME],
    '\xa9': [UNUSED_NAME],
    '\xaa': [UNUSED_NAME],
    '\xab': [UNUSED_NAME],
    '\xac': [UNUSED_NAME],
    '\xad': [UNUSED_NAME],
    '\xae': [UNUSED_NAME],
    '\xaf': [UNUSED_NAME],
    '\xb0': [UNUSED_NAME],
    '\xb1': [UNUSED_NAME],
    '\xb2': [UNUSED_NAME],
    '\xb3': [UNUSED_NAME],
    '\xb4': [UNUSED_NAME],
    '\xb5': [UNUSED_NAME],
    '\xb6': [UNUSED_NAME],
    '\xb7': [UNUSED_NAME],
    '\xb8': [UNUSED_NAME],
    '\xb9': [UNUSED_NAME],
    '\xba': [UNUSED_NAME],
    '\xbb': [UNUSED_NAME],
    '\xbc': [UNUSED_NAME],
    '\xbd': [UNUSED_NAME],
    '\xbe': [UNUSED_NAME],
    '\xbf': [UNUSED_NAME],
    '\xc0': [UNUSED_NAME],
    '\xc1': [UNUSED_NAME],
    '\xc2': [UNUSED_NAME],
    '\xc3': [UNUSED_NAME],
    '\xc4': [UNUSED_NAME],
    '\xc5': [UNUSED_NAME],
    '\xc6': [UNUSED_NAME],
    '\xc7': [UNUSED_NAME],
    '\xc8': [UNUSED_NAME],
    '\xc9': [UNUSED_NAME],
    '\xca': [UNUSED_NAME],
    '\xcb': [UNUSED_NAME],
    '\xcc': [UNUSED_NAME],
    '\xcd': [UNUSED_NAME],
    '\xce': [UNUSED_NAME],
    '\xcf': [UNUSED_NAME],
    '\xd0': [UNUSED_NAME],
    '\xd1': [UNUSED_NAME],
    '\xd2': [UNUSED_NAME],
    '\xd3': [UNUSED_NAME],
    '\xd4': [UNUSED_NAME],
    '\xd5': [UNUSED_NAME],
    '\xd6': [UNUSED_NAME],
    '\xd7': [UNUSED_NAME],
    '\xd8': [UNUSED_NAME],
    '\xd9': [UNUSED_NAME],
    '\xda': [UNUSED_NAME],
    '\xdb': [UNUSED_NAME],
    '\xdc': [UNUSED_NAME],
    '\xdd': [UNUSED_NAME],
    '\xde': [UNUSED_NAME],
    '\xdf': [UNUSED_NAME],
    '\xe0': [UNUSED_NAME],
    '\xe1': [UNUSED_NAME],
    '\xe2': [UNUSED_NAME],
    '\xe3': [UNUSED_NAME],
    '\xe4': [UNUSED_NAME],
    '\xe5': [UNUSED_NAME],
    '\xe6': [UNUSED_NAME],
    '\xe7': [UNUSED_NAME],
    '\xe8': [UNUSED_NAME],
    '\xe9': [UNUSED_NAME],
    '\xea': [UNUSED_NAME],
    '\xeb': [UNUSED_NAME],
    '\xec': [UNUSED_NAME],
    '\xed': [UNUSED_NAME],
    '\xee': [UNUSED_NAME],
    '\xef': [UNUSED_NAME],
    '\xf0': [UNUSED_NAME],
    '\xf1': [UNUSED_NAME],
    '\xf2': [UNUSED_NAME],
    '\xf3': [UNUSED_NAME],
    '\xf4': [UNUSED_NAME],
    '\xf5': [UNUSED_NAME],
    '\xf6': [UNUSED_NAME],
    '\xf7': [UNUSED_NAME],
    '\xf8': [UNUSED_NAME],
    '\xf9': [UNUSED_NAME],
    '\xfa': [UNUSED_NAME],
    '\xfb': [UNUSED_NAME],
    '\xfc': [UNUSED_NAME],
    '\xfd': [UNUSED_NAME],
    '\xfe': [UNUSED_NAME],
    '\xff': [UNUSED_NAME]}

DEFAULT_BLOCK_TYPES = [
    'clay',
    'coal ore',
    'diamond ore',
    'gold ore',
    'iron ore',
    'obsidian',
    '49']

CHUNK_SIZE_Y = 128
CHUNK_SIZE_Z = 16
CHUNK_SIZE_X = CHUNK_SIZE_Y * CHUNK_SIZE_Z

signal(SIGPIPE, SIG_DFL)
"""Avoid 'Broken pipe' message when canceling piped command."""


def lookup_block_type(block_type):
    """
    Find block types based on input string.

    @param block_type: Name or hex ID of a block type.
    @return: Subset of BLOCK_TYPES.keys().
    """

    if block_type is None or len(block_type) == 0:
        warnings.warn('Empty block type')
        return set([])

    block_type = block_type.lower()

    if len(block_type) == 2 and all(char in HEXDIGITS for char in block_type):
        # Look up single block type by hex value
        for block_hex, block_names in BLOCK_TYPES.iteritems():
            if block_hex == unhexlify(block_type):
                return set([block_hex])

    # Name substring search, could have multiple results
    result = set([])
    for block_hex, block_names in BLOCK_TYPES.iteritems(): # Block
        for block_name in block_names: # Synonyms
            if block_name.lower().find(block_type) != -1:
                result.add(block_hex)

    if result == set([]):
        warnings.warn('Unknown block type %s' % block_type)
    return result


def print_block_types():
    """Print the block block_names and hexadecimal IDs"""
    for block_hex, block_names in sorted(
        BLOCK_TYPES.iteritems(),
        key=itemgetter(0)):
        if block_names != [UNUSED_NAME]:
            print hex(ord(block_hex))[2:].upper().zfill(2), ', '.join(block_names)


def plot(counts, bt_hexes, title):
    """
    Actual plotting of data.

    @param counts: Integer counts per layer.
    @param bt_hexes: Subset of BLOCK_TYPES.keys().
    """
    fig = plt.figure() 
    fig.canvas.set_window_title(title)

    for index, block_counts in enumerate(counts):
        plt.plot(
            block_counts,
            label = BLOCK_TYPES[bt_hexes[index]][0],
            linewidth = 1)

    plt.legend()
    plt.ylabel('Count')
    plt.xlabel('Y (world height)')

    plt.show()


def mian(world_dir, bt_hexes, nether):
    """
    Runs through the DAT files and gets the layer counts for the plot.

    @param world_dir: Path to existing Minecraft world directory.
    @param bt_hexes: Subset of BLOCK_TYPES.keys().
    @param nether: Whether or not to graph The Nether.
    """

    title = split(world_dir)[1]

    # All world blocks are stored in DAT files
    if nether:
        paths = glob(join(world_dir, 'DIM-1/*/*/*.dat'))
        title += ' Nether'
    else:
        paths = glob(join(world_dir, '*/*/*.dat'))

    # Unpack block format
    # <http://www.minecraftwiki.net/wiki/Alpha_Level_Format#Block_Format>
    raw_blocks = ''
    for path in paths:
        nbtfile = NBTFile(path, 'rb')

        raw_blocks += nbtfile['Level']['Blocks'].value

        nbtfile.file.close()

    layers = [raw_blocks[i::128] for i in xrange(127)]
    
    counts = [[] for i in xrange(len(bt_hexes))]
    for bt_index in range(len(bt_hexes)):
        bt_hex = bt_hexes[bt_index]
        for layer in layers:
            counts[bt_index].append(layer.count(bt_hex))

    plot(counts, bt_hexes, title)


def main(argv = None):
    """Argument handling."""

    if argv is None:
        argv = sys.argv

    # Defaults
    block_type_names = DEFAULT_BLOCK_TYPES
    nether = False

    try:
        opts, args = getopt(
            argv[1:],
            'b:ln',
            ['blocks=', 'list', 'nether'])
    except GetoptError, err:
        sys.stderr.write(str(err) + '\n')
        return 2

    for option, value in opts:
        if option in ('-b', '--blocks'):
            block_type_names = value.split(',')
        elif option in ('-n', '--nether'):
            nether = True
        elif option in ('-l', '--list'):
            print_block_types()
            return 0
        else:
            sys.stderr.write('Unhandled option %s\n' % option)
            return 2

    assert len(args) == 1, 'You need to specify exactly one save directory.'
    world_dir = args[0]

    # Look up block_types
    bt_hexes = []
    for name in block_type_names:
        bt_hexes.extend(lookup_block_type(name))

    mian(world_dir, bt_hexes, nether)


if __name__ == '__main__':
    sys.exit(main())
