import nflreadpy


player_stats = nflreadpy.load_player_stats([2025])

df = player_stats.to_pandas()
total = 0

for k, row in df.iterrows():
    player_name = row["player_name"]
    player_pos = row["position"]

    if player_pos == "K" and row["def_tackles_solo"] > 0:
        print(f"{player_name} Week {row["week"]} {row["def_tackles_solo"]}")
        total += 1

print(total)