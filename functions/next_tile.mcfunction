
scoreboard players set next level 0

#read tile data

#rpt: rotation per tick
scoreboard players operation rpt_last level = rpt level

execute store result score rpt level run data get storage adofai:level level.tiles.[0].rpt

execute store result score first_rotation level run data get storage adofai:level level.tiles.[0].first_rotation

execute store result score is_twirl level run data get storage adofai:level level.tiles.[0].is_twirl

execute if score is_twirl level matches 1 run scoreboard players remove is_reverse level 1
execute if score is_twirl level matches 1 unless score is_reverse level matches 0 run scoreboard players set is_reverse level 1

#calcuate tile progress

scoreboard players operation error level = tile_progress level
scoreboard players operation error level -= max_rotation level
scoreboard players operation error level *= rpt level
scoreboard players operation error level /= rpt_last level
scoreboard players operation tile_progress level = error level

execute store result score max_rotation level run data get storage adofai:level level.tiles.[0].max_rotation


#planet_id: 0-fire 1-ice
scoreboard players remove planet_id level 1
execute unless score planet_id level matches 0 run scoreboard players set planet_id level 1

#set planet position

execute if score planet_id level matches 0 run data modify entity @e[type=armor_stand,tag=fire_planet,limit=1] Pos.[0] set from storage adofai:level level.tiles.[0].x
execute if score planet_id level matches 0 run data modify entity @e[type=armor_stand,tag=fire_planet,limit=1] Pos.[2] set from storage adofai:level level.tiles.[0].z
execute if score planet_id level matches 1 run data modify entity @e[type=armor_stand,tag=ice_planet,limit=1] Pos.[0] set from storage adofai:level level.tiles.[0].x
execute if score planet_id level matches 1 run data modify entity @e[type=armor_stand,tag=ice_planet,limit=1] Pos.[2] set from storage adofai:level level.tiles.[0].z

#pop stack

#data modify storage adofai:level level.passed_tiles append from storage adofai:level level.tiles.[0]
data remove storage adofai:level level.tiles.[0]

#win judgement

execute unless data storage adofai:level level.tiles.[0] run function adofai:win

#process mid-spin tiles

execute if score max_rotation level matches 0 run function adofai:next_tile

#special: auto-play no fail

execute if score auto_play level matches 1 run function adofai:process_autoplay
execute if score next level matches 1 run function adofai:next_tile
