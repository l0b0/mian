# -*- coding: utf-8 -*-
"""
Minecraft block names and hex values from
http://www.minecraftwiki.net/wiki/Data_values
"""

UNUSED_NAME = '<unused>'

# The first name is the canonical one (for the moment).
# Subsequent names are synonyms.
# FIXME: index is now a character, not a byte. Change e.g. '\0x00' to 0x00.
BLOCK_TYPES = {
    '\x00': [
        'Air'],
    '\x01': [
        'Stone'],
    '\x02': [
        'Grass'],
    '\x03': [
        'Dirt'],
    '\x04': [
        'Cobblestone'],
    '\x05': [
        'Wooden Plank'],
    '\x06': [
        'Sapling'],
    '\x07': [
        'Bedrock',
        'Adminium'],
    '\x08': [
        'Water',
        'Flowing Water'],
    '\x09': [
        'Stationary Water'],
    '\x0a': [
        'Lava',
        'Flowing Lava'],
    '\x0b': [
        'Stationary Lava'],
    '\x0c': [
        'Sand'],
    '\x0d': [
        'Gravel'],
    '\x0e': [
        'Gold Ore'],
    '\x0f': [
        'Iron Ore'],
    '\x10': [
        'Coal Ore'],
    '\x11': [
        'Wood',
        'Log'],
    '\x12': [
        'Leaves'],
    '\x13': [
        'Sponge'],
    '\x14': [
        'Glass',
        'Glass Block'],
    '\x15': [
        'Lapis Lazuli Ore'],
    '\x16': [
        'Lapis Lazuli Block'],
    '\x17': [
        'Dispenser'],
    '\x18': [
        'Sandstone'],
    '\x19': [
        'Note Block'],
    '\x1a': [
        'Bed'],
    '\x1b': [
        'Powered Rail'],
    '\x1c': [
        'Detector Rail'],
    '\x1d': [
        'Sticky Piston'],
    '\x1e': [
        'Cobweb'],
    '\x1f': [
        'Tall Grass'],
    '\x20': [
        'Dead Bush',
        'Dead Shrubs'],
    '\x21': [
        'Piston'],
    '\x22': [
        'Piston Extension'],
    '\x23': [
        'Wool',
        'Cloth'],
    '\x24': [
        'Block Moved by Piston'],
    '\x25': [
        'Dandelion',
        'Yellow Flower'],
    '\x26': [
        'Red Rose',
        'Rose'],
    '\x27': [
        'Brown Mushroom'],
    '\x28': [
        'Red Mushroom'],
    '\x29': [
        'Gold Block',
        'Block of Gold'],
    '\x2a': [
        'Iron Block',
        'Block of Iron'],
    '\x2b': [
        'Double Slab',
        'Double Stone Slab',
        'Double Step'],
    '\x2c': [
        'Slab',
        'Step'],
    '\x2d': [
        'Brick'],
    '\x2e': [
        'Tnt'],
    '\x2f': [
        'Bookshelf'],
    '\x30': [
        'Moss Stone',
        'Mossy Cobblestone'],
    '\x31': [
        'Obsidian'],
    '\x32': [
        'Torch'],
    '\x33': [
        'Fire'],
    '\x34': [
        'Monster Spawner',
        'Mob Spawner'],
    '\x35': [
        'Wooden Stairs'],
    '\x36': [
        'Chest'],
    '\x37': [
        'Redstone Wire'],
    '\x38': [
        'Diamond Ore',
        'Emerald Ore'],
    '\x39': [
        'Diamond Block',
        'Emerald Block',
        'Block of Diamond'],
    '\x3a': [
        'Workbench',
        'Crafting Table'],
    '\x3b': [
        'Crops',
        'Wheat Crops',
        'Seed'],
    '\x3c': [
        'Farmland',
        'Soil'],
    '\x3d': [
        'Furnace'],
    '\x3e': [
        'Burning Furnace'],
    '\x3f': [
        'Sign Post'],
    '\x40': [
        'Wooden Door'],
    '\x41': [
        'Ladder'],
    '\x42': [
        'Minecart Track',
        'Rails'],
    '\x43': [
        'Cobblestone Stairs'],
    '\x44': [
        'Wall Sign'],
    '\x45': [
        'Lever'],
    '\x46': [
        'Stone Pressure Plate'],
    '\x47': [
        'Iron Door'],
    '\x48': [
        'Wooden Pressure Plate'],
    '\x49': [
        'Redstone Ore'],
    '\x4a': [
        'Glowing Redstone Ore'],
    '\x4b': [
        'Redstone Torch [off]'],
    '\x4c': [
        'Redstone Torch',
        'Redstone Torch [on]'],
    '\x4d': [
        'Stone Button'],
    '\x4e': [
        'Snow'],
    '\x4f': [
        'Ice'],
    '\x50': [
        'Snow Block'],
    '\x51': [
        'Cactus'],
    '\x52': [
        'Clay'],
    '\x53': [
        'Sugar Cane',
        'Reed',
        'Bamboo',
        'Papyrus'],
    '\x54': [
        'Jukebox'],
    '\x55': [
        'Fence'],
    '\x56': [
        'Pumpkin'],
    '\x57': [
        'Netherrack',
        'Bloodstone',
        'Hellstone',
        'Netherstone',
        'Red Mossy Cobblestone'],
    '\x58': [
        'Soul Sand',
        'Hell Mud',
        'Mud',
        'Nethermud',
        'Slow Sand'],
    '\x59': [
        'Glowstone',
        'Lightstone',
        'Brittle Gold',
        'Brightstone',
        'Australium',
        'Brimstone'],
    '\x5a': [
        'Portal'],
    '\x5b': [
        'Jack-O-Lantern'],
    '\x5c': [
        'Cake Block'],
    '\x5d': [
        'Redstone Repeater [off]'],
    '\x5e': [
        'Redstone Repeater [on]'],
    '\x5f': [
         'Locked Chest',
         'Aprils Fools Chest'],
    '\x60': [
         'Trapdoor'],
    '\x61': [
         'Hidden Silverfish',
         'Silverfish'],
    '\x62': [
         'Stone Brick'],
    '\x63': [
         'Huge Brown Mushroom'],
    '\x64': [
         'Huge Red Mushroom'],
    '\x65': [
         'Iron Bars'],
    '\x66': [
         'Glass Pane'],
    '\x67': [
         'Melon'],
    '\x68': [
         'Pumpkin Stem'],
    '\x69': [
         'Melon Stem'],
    '\x6a': [
         'Vines'],
    '\x6b': [
         'Fence Gate'],
    '\x6c': [
         'Brick Stairs'],
    '\x6d': [
         'Stone Brick Stairs'],
    '\x6e': [
         'Mycelium'],
    '\x6f': [
         'Lily Pad'],
    '\x70': [
         'Nether Brick'],
    '\x71': [
         'Nether Brick Fence'],
    '\x72': [
         'Nether Brick Stairs'],
    '\x73': [
         'Nether Wart'],
    '\x74': [
         'Enchantment Table'],
    '\x75': [
         'Brewing Stand'],
    '\x76': [
         'Cauldron'],
    '\x77': [
         'Air Portal'],
    '\x78': [
         'Air Portal Frame'],
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
