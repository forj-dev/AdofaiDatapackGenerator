
# This function is called every tick and increments the progress of the current tile.
scoreboard players set next level 0

scoreboard players operation tile_progress level += rpt level

scoreboard players operation rotation level = first_rotation level
execute if score is_reverse level matches 0 run scoreboard players operation rotation level += tile_progress level
execute if score is_reverse level matches 1 run scoreboard players operation rotation level -= tile_progress level


# process click event

execute if entity @e[type=fishing_bobber] run scoreboard players set clicked level 1
kill @e[type=fishing_bobber]


# update planet display
execute if score planet_id level matches 0 store result entity @e[type=armor_stand,tag=fire_planet,limit=1] Rotation.[0] float 1 run scoreboard players get rotation level
execute if score planet_id level matches 1 store result entity @e[type=armor_stand,tag=ice_planet,limit=1] Rotation.[0] float 1 run scoreboard players get rotation level
execute if score planet_id level matches 0 run execute as @e[type=armor_stand,tag=fire_planet] at @s run tp @e[type=armor_stand,tag=ice_planet] ^ ^ ^1 facing entity @s
execute if score planet_id level matches 1 run execute as @e[type=armor_stand,tag=ice_planet] at @s run tp @e[type=armor_stand,tag=fire_planet] ^ ^ ^1 facing entity @s


# spawn particles
execute as @e[type=armor_stand,tag=fire_planet] at @s run particle dripping_lava ~ ~1.7 ~ 0.1 0.1 0.1 0.01 5
execute as @e[type=armor_stand,tag=ice_planet] at @s run particle dripping_water ~ ~1.7 ~ 0.1 0.1 0.1 0.01 5


execute unless score auto_play level matches 1 if score clicked level matches 1 run function adofai:process_click
execute if score auto_play level matches 1 run function adofai:process_autoplay

execute if score next level matches 1 run function adofai:next_tile

scoreboard players set clicked level 0
