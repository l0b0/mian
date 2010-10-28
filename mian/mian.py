#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mian - Mine analysis - Graph blocks to height in a Minecraft save game
<http://github.com/l0b0/mian>

Default syntax:

mian [-b|--blocks=<list>] [-l|--list] [-o|--output=filename] <World
directory>

Options:

-b, --blocks    Specify blocks to include as a comma-separated list, using
                either the names or hex values from the list.
-l, --list      List available blocks (from
                <http://www.minecraftwiki.net/wiki/Data_values>).
-o, --output    Output file name, defaults to WorldX.png.

Description:

Creates a file with a graph of how much the given materials occur at each
layer of the map.

Examples:

$ mian ~/.minecraft/saves/World1
Creates World1.png in the current directory with the graph.

$ mian --blocks="diamond ore,mob spawner,obsidian" ~/.minecraft/saves/World1
Ditto, showing only the specified blocks

$ mian --list
Show a list of blocks that can be searched for
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
from itertools import izip_longest
from nbt import nbt
from os.path import join, split
from signal import signal, SIGPIPE, SIG_DFL
from string import hexdigits
import sys
import warnings

ARG_ERROR = 'You need to specify exactly one save directory.'

BLOCKS = {
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

DEFAULT_BLOCKS = [
    'Clay',
    'Coal ore',
    'Diamond ore',
    'Gold ore',
    'Iron ore',
    'Obsidian',
    'Redstone ore']

signal(SIGPIPE, SIG_DFL)
"""Avoid 'Broken pipe' message when canceling piped command."""


def _lookup_block(block):
    """
    Find blocks based on input string.
    
    @param block: Name or hex ID of a block.
    @return: Subset of BLOCKS.
    
    Examples:
    >>> sorted(_lookup_block('gold'))
    ['Gold block', 'Gold ore']
    >>> _lookup_block('20')
    {'Magenta cloth': ' '}
    """

    if block is None or len(block) == 0:
        warnings.warn('Empty block')
        return None

    block = block.lower()

    if len(block) == 2 and all(char in hexdigits for char in block):
        # Look up single block by hex value
        for key, value in BLOCKS.iteritems():
            if value == unhexlify(block):
                return {key: value}

    # Name substring search
    result = {}
    for name in sorted(BLOCKS):
        if name.lower().find(block) != -1:
            result[name] = BLOCKS[name]

    if result == []:
        warnings.warn('Unknown block %s' % block)
    return result


def print_blocks():
    """Print the block names and hexadecimal IDs"""
    max_length = len(max(BLOCKS.keys(), key=len))
    for name in sorted(BLOCKS):
        print \
            name.ljust(max_length),\
            hex(ord(BLOCKS[name]))[2:].upper().zfill(2)


def mian(world_dir, output_file, blocks):
    """
    Runs through the files and creates the output.
    
    @param world_dir: Path to existing Minecraft world directory.
    @param output_file: Path to file which should be written.
    @param blocks: Subset of BLOCKS.
    """
    files = glob(join(world_dir, '*/*/*.dat')) # All world blocks

    col = []

    for file in files:
        #print file
        file = nbt.NBTFile(file,'rb')

        col.extend(izip_longest(*[iter(file["Level"]["Blocks"].value)]*128))

        file.file.close()

    layers = zip(*col)

    names = blocks.keys()
    hexes = blocks.values()

    def count_blocks(layer):
        def filter_block(bname):
            count = len([block for block in layer if block == bname])
            return count

        m = map(filter_block, hexes)
        return m

    gnuplot = Gnuplot.Gnuplot()
    gnuplot('set term png')
    gnuplot('set out "%s"' % output_file)
    gnuplot('set style data lines')

    data = zip(*(count_blocks(layer) for layer in layers))

    data = (
        Gnuplot.PlotItems.Data(
            list(enumerate(block)),
            title=names[index]) for index, block in enumerate(data))

    gnuplot.plot(*data)


def main(argv = None):
    """Argument handling."""

    if argv is None:
        argv = sys.argv

    # Defaults
    block_names = DEFAULT_BLOCKS
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
            block_names = value.split(',')
        elif option in ('-l', '--list'):
            print_blocks()
            return 0
        elif option in ('-o', '--output'):
            output_file = value

    assert len(args) == 1, ARG_ERROR
    world_dir = args[0]
    
    if output_file is None:
        # Use savegame directory name
        output_file = split(world_dir)[1] + '.png'

    # Look up blocks
    blocks = {}
    for name in block_names:
        blocks.update(_lookup_block(name))

    mian(world_dir, output_file, blocks)


if __name__ == '__main__':
    sys.exit(main())