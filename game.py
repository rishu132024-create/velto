player_x = 5
player_y = 5

enemy_x = 10
enemy_y = 5

say "=== VELTO 2D GAME ==="
say "Player"
say player_x
say player_y

say "Enemy"
say enemy_x
say enemy_y

if player_x == enemy_x:
    say "Collision!"
else:
    say "No collision"

for step in (1, 2, 3, 4, 5):
    player_x = player_x + 1
    say player_x
