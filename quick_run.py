import connect4
from tensorflow.keras.models import model_from_json

with open("saved_model.json", "r") as file:
    loaded_model = model_from_json(file.read())
    game = connect4.Board(connect4.WIDTH, connect4.HEIGHT,
                          connect4.AI(1,loaded_model), connect4.Human_Player(2))
    game.run_board()
    print("Switching sides...")
    game = connect4.Board(connect4.WIDTH, connect4.HEIGHT,
                          connect4.Human_Player(1), connect4.AI(2,loaded_model))
    game.run_board()

