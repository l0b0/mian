from nbt import nbt
from itertools import izip_longest, repeat
import glob
import Gnuplot

files = glob.glob("/Users/pepijndevos/Library/Application Support/minecraft/saves/World2/*/*/*.dat")
output = "minecraft.png"

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
    'Obsedian': '\x31',
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