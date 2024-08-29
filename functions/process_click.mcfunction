
scoreboard players operation error level = tile_progress level
scoreboard players operation error level -= max_rotation level
execute if score error level matches -35..35 run scoreboard players set next level 1
execute unless score error level matches -35..35 run function adofai:fail
