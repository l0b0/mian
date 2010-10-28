#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mian - Mine analysis - Graph blocks to height in a Minecraft save game
<http://github.com/l0b0/mian>

Default syntax:

mian -

Options:

-m, --materials    Specify materials to include as a comma-separated list
-l, --list         List materials
-o, --output       Output file name, defaults to WorldX.png

Description:


Examples:

$ mian ~/.minecraft/saves/World1

"""

__author__ = 'Pepijn de Vos, Victor Engmark'
__copyright__ = 'Copyright (C) 2010 Pepijn de Vos, Victor Engmark'
__credits__ = ['Pepijn de Vos', 'Victor Engmark']
__maintainer__ = 'Victor Engmark'
__email__ = 'victor.engmark@gmail.com'
__license__ = 'GPL v3 or newer'

from getopt import getopt, GetoptError
from glob import glob
import Gnuplot
from itertools import izip_longest, repeat
from nbt import nbt
from os.path import dirname, join, split
from signal import signal, SIGPIPE, SIG_DFL
import sys

ARG_ERROR = 'You need to specify exactly one save directory'

signal(SIGPIPE, SIG_DFL)
"""Avoid 'Broken pipe' message when canceling piped command."""


def mian(save_directory, output):
    """"""
    files = glob(join(save_directory, '*/*/*.dat'))

    col = []

    for file in files:
        print file
        file = nbt.NBTFile(file,'rb')

        col.extend(izip_longest(*[iter(file["Level"]["Blocks"].value)]*128))

        file.file.close()

    layers = zip(*col)

    minerals = {
        #'Bedrock': '\x07',
        #'Water': '\x09',
        #'Lava': '\x0B',
        #'Sand': '\x0C',
        #'Gravel': '\x0D',
        'Gold': '\x0E',
        'Iron': '\x0F',
        'Coal': '\x10',
        'Obsidian': '\x31',
        'Diamond': '\x38',
        'Redstone': '\x49',
        'Clay': '\x52',
    }

    names = minerals.keys()
    hexes = minerals.values()

    def count_minerals(layer):
        def filter_mineral(mineral):
            count = len([block for block in layer if block == mineral])
            return count

        m = map(filter_mineral, hexes)
        return m

    g = Gnuplot.Gnuplot(debug=1)
    g('set term png')
    g('set out "%s"' % output)
    g('set style data lines')

    data = zip(*(count_minerals(layer) for layer in layers))

    data = (Gnuplot.PlotItems.Data(list(enumerate(mineral)), title=names[index]) for index, mineral in enumerate(data))

    g.plot(*data)


def main(argv = None):
    """Argument handling."""

    if argv is None:
        argv = sys.argv

    # Defaults
    materials = []
    output = None

    try:
        opts, args = getopt(
            argv[1:],
            'o:',
            ['output='])
    except GetoptError, err:
        sys.stderr.write(str(err) + '\n')
        return 2

    for option, value in opts:
        if option in ('-o', '--output'):
            output = value

    assert args != [], ARG_ERROR
    assert len(args) == 1, ARG_ERROR
    save_directory = args[0]
    
    if output is None:
        # Use savegame directory name
        output = split(save_directory)[1] + '.png'

    mian(save_directory, output)


if __name__ == '__main__':
    main()