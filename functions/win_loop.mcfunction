
#spin at speed of rpt
execute if score is_reverse level matches 0 run scoreboard players operation rotation level += rpt level
execute if score is_reverse level matches 1 run scoreboard players operation rotation level -= rpt level

# update planet display
execute if score planet_id level matches 0 store result entity @e[type=armor_stand,tag=fire_planet,limit=1] Rotation.[0] float 1 run scoreboard players get rotation level
execute if score planet_id level matches 1 store result entity @e[type=armor_stand,tag=ice_planet,limit=1] Rotation.[0] float 1 run scoreboard players get rotation level
execute if score planet_id level matches 0 run execute as @e[type=armor_stand,tag=fire_planet] at @s run tp @e[type=armor_stand,tag=ice_planet] ^ ^ ^1 facing entity @s
execute if score planet_id level matches 1 run execute as @e[type=armor_stand,tag=ice_planet] at @s run tp @e[type=armor_stand,tag=fire_planet] ^ ^ ^1 facing entity @s


# spawn particles
execute as @e[type=armor_stand,tag=fire_planet] at @s run particle dripping_lava ~ ~1.7 ~ 0.1 0.1 0.1 0.01 5
execute as @e[type=armor_stand,tag=ice_planet] at @s run particle dripping_water ~ ~1.7 ~ 0.1 0.1 0.1 0.01 5

