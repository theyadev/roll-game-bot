class Game():
    def __init__(self, max: int, game_type: str,team1_id: int,team2_id: int):
        self.max = max
        self.type = game_type
        self.players = {}
        self.team1_id = team1_id
        self.team2_id = team2_id
