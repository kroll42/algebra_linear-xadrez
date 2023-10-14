from cor import Cor

class Tema:

    def __init__(self, light_bg, dark_bg, 
                       light_trace, dark_trace,
                       light_moves, dark_moves):
        
        self.bg = Cor(light_bg, dark_bg)
        self.trace = Cor(light_trace, dark_trace)
        self.moves = Cor(light_moves, dark_moves)