# read json from main.adofai, save to data

import json
import math
import os
import sys
import shutil
import zipfile

# print program info

print("ADOFAI to Minecraft Datapack Converter v1")
print("Warning: This program is still in development and may not work as expected.")
print("Warning: Do NOT put any important files in folder 'adofai-mc'!")
print("Use instructions: ")
print("1. Make sure you have put your .adofai file and .adofai-convertor file "
      "in the same folder as this program.")
print("2. Enter the position of the level in Minecraft, and the name of your .adofai file.")
print("3. Wait for the program to finish processing the data.")
print("4. Put the generated zip file in the 'datapacks' folder of your Minecraft world.")
print("5. Activate the datapack by typing '/datapack enable adofai-mc' in the game.")
print("6. Type '/reload' to reload the world.")
print("7. Use '/function adofai:level' to load the level in your world.")
print("8. Use '/function adofai:start_level' to start the level.")
print("9. Use '/scoreboard players set auto_play level 1' to enable auto-play.")
print("10. Enjoy your adofai level in Minecraft!")

# user input

x = float(input("Enter x position: "))
y = float(input("Enter y position: "))
z = float(input("Enter z position: "))
file_name = input("Enter adofai file name: ")

origin_x = x
origin_y = y
origin_z = z

# read from adofai file

print(f"Reading {file_name}.adofai...")

try:
    with open(f'{file_name}.adofai', 'r', encoding='utf-8') as f:
        content = f.read()
        if content.startswith('\ufeff'):
            content = content[1:]
        content = content.replace(', }', ' }')
        data = json.loads(content)
except json.JSONDecodeError as e:
    print(f"JSON解析错误: {e}")
    print(f"错误发生在字符位置: {e.pos}")
    print(f"错误行号: {e.lineno}")
    print(f"错误列号: {e.colno}")
    print("请检查JSON数据格式是否正确。")
    raise e

actions = {}

# process actions

print("Processing actions...")

position_offsets = {}

for action in data['actions']:
    floor = action['floor']
    if floor not in actions:
        actions[floor] = []
    actions[floor].append(action)
    if action['eventType'] == 'PositionTrack' and not action['editorOnly']:
        if action['floor'] not in position_offsets:
            position_offsets[action['floor']] = {
                'x': action['positionOffset'][1],
                'z': action['positionOffset'][0]
            }
        else:
            position_offsets[action['floor']]['x'] += action['positionOffset'][1]
            position_offsets[action['floor']]['z'] += action['positionOffset'][0]
        if action['justThisTile']:
            if action['floor']+1 not in position_offsets:
                position_offsets[action['floor']+1] = {
                    'x': -action['positionOffset'][1],
                    'z': -action['positionOffset'][0]
                }
            else:
                position_offsets[action['floor']+1]['x'] -= action['positionOffset'][1]
                position_offsets[action['floor']+1]['z'] -= action['positionOffset'][0]

# process tiles

print("Processing tiles...")


def normalize_angle(_angle):
    if _angle < 0:
        _angle += 360
    elif _angle >= 360:
        _angle -= 360
    return _angle


bpm = data['settings']['bpm']
reverse = False
length = len(data['angleData'])

pivot_offset = 0.2  # constant

tiles = []

display_blocks = []

for i in range(length + 1):
    twirl = False
    bpm_last = bpm
    # process events
    if i in actions:
        for action in actions[i]:
            if action['eventType'] == 'SetSpeed':
                if action['speedType'] == 'Bpm':
                    bpm = action['beatsPerMinute']
                elif action['speedType'] == 'Multiplier':
                    bpm *= action['bpmMultiplier']
                else:
                    print(f"未知的速度类型: {action['speedType']}")
                    raise ValueError
            elif action['eventType'] == 'Twirl':
                twirl = True
                reverse = not reverse
    # process tile direction
    if i == 0:
        in_adofai_direction = 180
        out_adofai_direction = data['angleData'][i]
    elif i == length:
        in_adofai_direction = normalize_angle(data['angleData'][i - 1] - 180)
        out_adofai_direction = in_adofai_direction
        if i < length and data['angleData'][i - 1] == 999:
            in_adofai_direction = normalize_angle(data['angleData'][i - 2])
    else:
        in_adofai_direction = normalize_angle(data['angleData'][i - 1] - 180)
        out_adofai_direction = data['angleData'][i]
        if i < length and data['angleData'][i - 1] == 999:
            in_adofai_direction = normalize_angle(data['angleData'][i - 2])
        if i < length and data['angleData'][i] == 999:
            out_adofai_direction = normalize_angle(data['angleData'][i - 1] - 180)
    if i != 0:
        prev_out_adofai_direction = data['angleData'][i - 1]
        if i < length and data['angleData'][i - 1] == 999:
            prev_out_adofai_direction = normalize_angle(data['angleData'][i - 2] - 180)
    else:
        prev_out_adofai_direction = 0
    # convert adofai angle format to mc format
    in_mc_direction = normalize_angle(-in_adofai_direction)
    out_mc_direction = normalize_angle(-out_adofai_direction)
    # process position track event
    if i in position_offsets:
        x += position_offsets[i]['x']
        z += position_offsets[i]['z']
    # calculate output
    rpt = bpm / 60.0 / 20.0 * 180.0
    first_rotation = in_mc_direction * 1.0
    is_twirl = 1 if twirl else 0
    max_rotation = normalize_angle(out_adofai_direction - in_adofai_direction)
    max_rotation = max_rotation if reverse else -max_rotation
    max_rotation = normalize_angle(max_rotation) * 1.0
    if i != 0:
        x += math.sin(math.radians(prev_out_adofai_direction))
        z += math.cos(math.radians(prev_out_adofai_direction))
    if i < length and data['angleData'][i] == 999:
        max_rotation = 0.0
    elif max_rotation == 0.0:
        max_rotation = 360.0
    tiles.append({
        'rpt': rpt,
        'first_rotation': first_rotation,
        'is_twirl': is_twirl,
        'max_rotation': max_rotation,
        'x': x,
        'z': z
    })
    print(f"Tile {i}: rpt={rpt}, first_rotation={first_rotation}, "
          f"is_twirl={is_twirl}, max_rotation={max_rotation}, "
          f"x={x:.4f}, z={z:.4f}")
    # process display blocks
    # tile display
    if i == 0:
        display_blocks.append({
            'texture': 'minecraft:stone_brick_wall',
            'rotation': out_mc_direction,
            'x': x + pivot_offset * math.sin(math.radians(out_adofai_direction)),
            'z': z + pivot_offset * math.cos(math.radians(out_adofai_direction))
        })
    elif i == length:
        if data['angleData'][i - 1] != 999:
            display_blocks.append({
                'texture': 'minecraft:stone_brick_wall',
                'rotation': in_mc_direction,
                'x': x + pivot_offset * math.sin(math.radians(in_adofai_direction)),
                'z': z + pivot_offset * math.cos(math.radians(in_adofai_direction))
            })
        else:
            display_blocks.append({
                'texture': 'minecraft:sandstone_wall',
                'rotation': in_mc_direction,
                'x': x + pivot_offset * math.sin(math.radians(in_adofai_direction)),
                'z': z + pivot_offset * math.cos(math.radians(in_adofai_direction))
            })
    else:
        if data['angleData'][i] != 999:
            display_blocks.append({
                'texture': 'minecraft:stone_brick_wall',
                'rotation': in_mc_direction,
                'x': x + pivot_offset * math.sin(math.radians(in_adofai_direction)),
                'z': z + pivot_offset * math.cos(math.radians(in_adofai_direction))
            })
            display_blocks.append({
                'texture': 'minecraft:stone_brick_wall',
                'rotation': out_mc_direction,
                'x': x + pivot_offset * math.sin(math.radians(out_adofai_direction)),
                'z': z + pivot_offset * math.cos(math.radians(out_adofai_direction))
            })
        else:
            display_blocks.append({
                'texture': 'minecraft:sandstone_wall',
                'rotation': in_mc_direction,
                'x': x + pivot_offset * math.sin(math.radians(in_adofai_direction)),
                'z': z + pivot_offset * math.cos(math.radians(in_adofai_direction))
            })
    # event display
    block_mc_rotation = normalize_angle((in_mc_direction + out_mc_direction) / 2.0)
    if bpm != bpm_last:
        if bpm > bpm_last:
            display_blocks.append({
                'texture': 'minecraft:fire_coral_block',
                'rotation': block_mc_rotation,
                'small': True,
                'x': x,
                'z': z
            })
        else:
            display_blocks.append({
                'texture': 'minecraft:tube_coral_block',
                'rotation': block_mc_rotation,
                'small': True,
                'x': x,
                'z': z
            })
    if twirl:
        display_blocks.append({
            'texture': 'minecraft:brain_coral_block',
            'rotation': block_mc_rotation,
            'small': True,
            'x': x,
            'z': z
        })
    if i == length:
        display_blocks.append({
            'texture': 'minecraft:bubble_coral_block',
            'rotation': block_mc_rotation,
            'small': True,
            'x': x,
            'z': z
        })

# save processed tiles to mcfunction

print("Creating datapack...")

os.makedirs('adofai-mc\\data\\adofai\\functions', exist_ok=True)

pack_meta = {
    'pack': {
        'pack_format': 12,
        'description': f'ADOFAI In MC - {data["settings"]["artist"]} - {data["settings"]["song"]}'
    }
}

with open('adofai-mc\\pack.mcmeta', 'w', encoding='utf-8') as f:
    f.write(json.dumps(pack_meta, indent=2))

function_path = 'adofai-mc\\data\\adofai\\functions\\'  # constant
try:
    preset_functions = zipfile.ZipFile('functions.adofai-convertor')
except FileNotFoundError:
    # noinspection PyUnresolvedReferences,PyProtectedMember
    preset_functions = zipfile.ZipFile(os.path.join(sys._MEIPASS, 'functions.adofai-convertor'))

for file_name in preset_functions.namelist():
    preset_functions.extract(file_name, 'adofai-mc\\data\\adofai\\functions')

preset_functions.close()

max_chain_execute = 65400  # constant

# main function

print("Saving to level.mcfunction...")

with open(function_path + 'level.mcfunction', 'w', encoding='utf-8') as f:
    f.write('# Generated by ADOFAI Level Converter\n\n')
    f.write('# --------Level Info--------\n\n')
    f.write(f'# Song: {data["settings"]["song"]}\n')
    f.write(f'# Artist: {data["settings"]["artist"]}\n')
    f.write(f'# Artist Links: {data["settings"]["artistLinks"]}\n')
    f.write(f'# Author: {data["settings"]["author"]}\n')
    f.write(f'# Difficulty: {data["settings"]["difficulty"]}\n')
    f.write(f'# Description: {data["settings"]["levelDesc"]}\n\n')
    f.write('# --------Tiles--------\n\n')
    f.write(f'data merge storage adofai:level {{ level: {{ tiles: {json.dumps(tiles)} }} }}\n\n')
    f.write('# --------Planets--------\n\n')
    f.write('function adofai:spawn_planets\n\n')
    f.write('# --------Display Blocks--------\n\n')
    f.write('function adofai:display_blocks_0\n\n')
    f.write('# --------Init--------\n\n')
    f.write('function adofai:init_level\n\n')

# planets

print("Saving to spawn_planets.mcfunction...")

with open(function_path + 'spawn_planets.mcfunction', 'w', encoding='utf-8') as f:
    f.write('# Generated by ADOFAI Level Converter\n\n')
    f.write('# --------Planets--------\n\n')
    f.write(f'summon armor_stand {origin_x:.6f} {origin_y:.6f} {origin_z:.6f} '
            '{Invisible:1b,NoGravity:1b,Marker:1b,Invulnerable:1b,Tags:["fire_planet"]}\n')
    f.write(f'summon armor_stand {origin_x:.6f} {origin_y:.6f} {origin_z:.6f} '
            '{Invisible:1b,NoGravity:1b,Marker:1b,Invulnerable:1b,Tags:["ice_planet"]}\n\n')
    f.write('item replace entity @e[type=armor_stand,tag=fire_planet] armor.head with magma_block')
    f.write('\n')
    f.write('item replace entity @e[type=armor_stand,tag=ice_planet] armor.head with blue_ice')
    f.write('\n\n')

# display blocks

f = None

for i in range(len(display_blocks)):
    if i % max_chain_execute == 0:
        if f is not None:
            f.write('\n--------Spawn Next Batch--------\n\n')
            f.write(f'schedule function adofai:display_blocks_{i // max_chain_execute} 1t\n\n')
            f.close()
        print(f"Saving display_blocks_{i // max_chain_execute}.mcfunction...")
        f = open(function_path + f'display_blocks_{i // max_chain_execute}.mcfunction',
                 'w', encoding='utf-8')
        f.write('# Generated by ADOFAI Level Converter\n\n')
        f.write(f'# Song: {data["settings"]["song"]}\n\n')
        f.write(f'# --------Display Block Batch {i // max_chain_execute}/'
                f'{len(display_blocks) // max_chain_execute}--------\n\n')
    is_small = '1b' if 'small' in display_blocks[i] and display_blocks[i]['small'] else '0b'
    dy = 0.9 if 'small' in display_blocks[i] and display_blocks[i]['small'] else 0.0
    f.write(f'summon armor_stand '
            f'{display_blocks[i]["x"]:.6f} {y + dy:.6f} {display_blocks[i]["z"]:.6f} '
            f'{{ArmorItems:[{{}},{{}},{{}},{{id:"{display_blocks[i]["texture"]}",Count:1b}}],'
            f'Invisible:1b,NoGravity:1b,Marker:1b,Invulnerable:1b,Small:{is_small},'
            f'Rotation:[{display_blocks[i]["rotation"]:.6f}f,0.0f]}}\n')

if f is not None:
    f.write('\n')
    f.close()

print(f"Done: {len(tiles)} tiles processed from {length} angles.")

# compress folder 'adofai-mc' to 'adofai-mc.zip'

print("Compressing...")

current_dir = os.getcwd()


def zipdir(path, zip_h):
    # zip_h is zipfile handle
    os.chdir(path)
    for root, dirs, files in os.walk('.'):
        for file in files:
            zip_h.write(os.path.join(root, file).split('adofai-mc\\', 1)[0])


zip_f = zipfile.ZipFile('adofai-mc.zip', 'w', zipfile.ZIP_DEFLATED)
zipdir('adofai-mc', zip_f)
os.chdir(current_dir)
zip_f.close()

print("Cleaning up...")

shutil.rmtree('adofai-mc')

print("Done.")
