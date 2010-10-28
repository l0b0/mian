#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mian - Mine analysis - Graph block types to height in a Minecraft save game
<http://github.com/l0b0/mian>

Default syntax:

mian [-b|--blocks=<list>] [-l|--list] [-o|--output=path] <World directory>

Options:

-b, --blocks    Specify block types to include as a comma-separated list, using
                either the block_names or hex values from the list.
-l, --list      List available block types (from
                <http://www.minecraftwiki.net/wiki/Data_values>).
-o, --output    Output file name, defaults to WorldX.png.

Description:

Creates a file with a graph of how much the given materials occur at each
layer of the map.

Examples:

$ mian ~/.minecraft/saves/World1
Creates World1.png in the current directory with the graph.

$ mian --blocks="diamond ore,mob spawner,obsidian" ~/.minecraft/saves/World1
Ditto, showing only the specified block types

$ mian --list
Show a list of block types that can be searched for
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
import Gnuplot
from itertools import izip
from nbt.nbt import NBTFile
from os.path import join, split
from signal import signal, SIGPIPE, SIG_DFL
from string import hexdigits
import sys
import warnings

ARG_ERROR = 'You need to specify exactly one save directory.'

BLOCK_TYPES = {
    'Air': '\x00',
    'Stone': '\x01',
    'Grass': '\x02',
    'Dirt': '\x03',
    'Cobblestone': '\x04',
    'Wood': '\x05',
    'Sapling': '\x06',
    'Bedrock': '\x07',
    'Water': '\x08',
    'Stationary water': '\x09',
    'Lava': '\x0a',
    'Stationary lava': '\x0b',
    'Sand': '\x0c',
    'Gravel': '\x0d',
    'Gold ore': '\x0e',
    'Iron ore': '\x0f',
    'Coal ore': '\x10',
    'Log': '\x11',
    'Leaves': '\x12',
    'Sponge': '\x13',
    'Glass': '\x14',
    'Red cloth': '\x15',
    'Orange cloth': '\x16',
    'Yellow cloth': '\x17',
    'Lime cloth': '\x18',
    'Green cloth': '\x19',
    'Aqua green cloth': '\x1a',
    'Cyan cloth': '\x1b',
    'Blue cloth': '\x1c',
    'Purple cloth': '\x1d',
    'Indigo cloth': '\x1e',
    'Violet cloth': '\x1f',
    'Magenta cloth': '\x20',
    'Pink cloth': '\x21',
    'Black cloth': '\x22',
    'Gray / white cloth': '\x23',
    'White cloth': '\x24',
    'Yellow flower': '\x25',
    'Red rose': '\x26',
    'Brown mushroom': '\x27',
    'Red mushroom': '\x28',
    'Gold block': '\x29',
    'Iron block': '\x2a',
    'Double step': '\x2b',
    'Step': '\x2c',
    'Brick': '\x2d',
    'TNT': '\x2e',
    'Bookshelf': '\x2f',
    'Mossy cobblestone': '\x30',
    'Obsidian': '\x31',
    'Torch': '\x32',
    'Fire': '\x33',
    'Mob spawner': '\x34',
    'Wooden stairs': '\x35',
    'Chest': '\x36',
    'Redstone wire': '\x37',
    'Diamond ore': '\x38',
    'Diamond block': '\x39',
    'Workbench': '\x3a',
    'Crops': '\x3b',
    'Soil': '\x3c',
    'Furnace': '\x3d',
    'Burning furnace': '\x3e',
    'Sign post': '\x3f',
    'Wooden door': '\x40',
    'Ladder': '\x41',
    'Minecart tracks': '\x42',
    'Cobblestone stairs': '\x43',
    'Wall sign': '\x44',
    'Lever': '\x45',
    'Stone pressure plate': '\x46',
    'Iron door': '\x47',
    'Wooden pressure plate': '\x48',
    'Redstone ore': '\x49',
    'Glowing redstone ore': '\x4a',
    'Redstone torch (off)': '\x4b',
    'Redstone torch (on)': '\x4c',
    'Stone button': '\x4d',
    'Snow': '\x4e',
    'Ice': '\x4f',
    'Snow block': '\x50',
    'Cactus': '\x51',
    'Clay': '\x52',
    'Reed': '\x53',
    'Jukebox': '\x54',
    'Fence': '\x55'}

DEFAULT_BLOCK_TYPES = [
    'Clay',
    'Coal ore',
    'Diamond ore',
    'Gold ore',
    'Iron ore',
    'Obsidian',
    'Redstone ore']

CHUNK_SIZE_Y = 128
CHUNK_SIZE_Z = 16
CHUNK_SIZE_X = CHUNK_SIZE_Y * CHUNK_SIZE_Z

signal(SIGPIPE, SIG_DFL)
"""Avoid 'Broken pipe' message when canceling piped command."""


def _lookup_block_type(block_type):
    """
    Find block types based on input string.
    
    @param block_type: Name or hex ID of a block type.
    @return: Subset of BLOCK_TYPES.
    
    Examples:
    >>> sorted(_lookup_block_type('gold'))
    ['Gold block', 'Gold ore']
    >>> _lookup_block_type('20')
    {'Magenta cloth': ' '}
    """

    if block_type is None or len(block_type) == 0:
        warnings.warn('Empty block type')
        return None

    block_type = block_type.lower()

    if len(block_type) == 2 and all(char in hexdigits for char in block_type):
        # Look up single block type by hex value
        for key, value in BLOCK_TYPES.iteritems():
            if value == unhexlify(block_type):
                return {key: value}

    # Name substring search
    result = {}
    for name in sorted(BLOCK_TYPES):
        if name.lower().find(block_type) != -1:
            result[name] = BLOCK_TYPES[name]

    if result == []:
        warnings.warn('Unknown block type %s' % block_type)
    return result


def print_block_types():
    """Print the block block_names and hexadecimal IDs"""
    max_length = len(max(BLOCK_TYPES.keys(), key=len))
    for name in sorted(BLOCK_TYPES):
        print \
            name.ljust(max_length),\
            hex(ord(BLOCK_TYPES[name]))[2:].upper().zfill(2)


def mian(world_dir, output_file, block_types):
    """
    Runs through the DAT files and creates the output.
    
    @param world_dir: Path to existing Minecraft world directory.
    @param output_file: Path to file which should be written.
    @param block_types: Subset of BLOCK_TYPES.
    """
    paths = glob(join(world_dir, '*/*/*.dat')) # All world blocks

    xyz_values = []

    # Unpack block format
    # <http://www.minecraftwiki.net/wiki/Alpha_Level_Format#Block_Format>
    for path in paths:
        nbtfile = NBTFile(path,'rb')
        
        yzx_block = nbtfile["Level"]["Blocks"].value
        
        yzx_block_list = [iter(yzx_block)]
        
        xyz_block = izip(
                *yzx_block_list * CHUNK_SIZE_Y)

        xyz_values.extend(xyz_block)

        nbtfile.file.close()

    zxy_values = izip(*xyz_values)

    bt_names = block_types.keys()
    bt_hexes = block_types.values()

    def count_block_types(layer):
        def filter_block(bname):
            return len([block for block in layer if block == bname])

        return map(filter_block, bt_hexes)

    y_counts = []
    for layer in zxy_values:
        y_counts.append(count_block_types(layer))
    
    data = izip(*y_counts)
    print data

    gnuplot = Gnuplot.Gnuplot()
    gnuplot('set term png')
    gnuplot('set out "%s"' % output_file)
    gnuplot('set style data lines')
    
    plot_data = (
        Gnuplot.PlotItems.Data(
            list(enumerate(block)),
            title=bt_names[index]) for index, block in enumerate(data))

    gnuplot.plot(*plot_data)


def main(argv = None):
    """Argument handling."""

    if argv is None:
        argv = sys.argv

    # Defaults
    block_block_names = DEFAULT_BLOCK_TYPES
    output_file = None

    try:
        opts, args = getopt(
            argv[1:],
            'b:lo:',
            ['blocks=', 'list', 'output='])
    except GetoptError, err:
        sys.stderr.write(str(err) + '\n')
        return 2

    for option, value in opts:
        if option in ('-b', '--blocks'):
            block_block_names = value.split(',')
        elif option in ('-l', '--list'):
            print_block_types()
            return 0
        elif option in ('-o', '--output'):
            output_file = value

    assert len(args) == 1, ARG_ERROR
    world_dir = args[0]
    
    if output_file is None:
        # Use savegame directory name
        output_file = split(world_dir)[1] + '.png'

    # Look up block_types
    block_types = {}
    for name in block_block_names:
        block_types.update(_lookup_block_type(name))

    mian(world_dir, output_file, block_types)


if __name__ == '__main__':
    sys.exit(main())