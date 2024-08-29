
scoreboard players remove debug_mode level 1
execute unless score debug_mode level matches 0 run scoreboard players set debug_mode level 1

execute if score debug_mode level matches 0 run scoreboard objectives setdisplay sidebar
execute if score debug_mode level matches 1 run scoreboard objectives setdisplay sidebar level
