"""food class module"""
from dataclasses import dataclass

@dataclass
class Food():
    x : int
    y : int
    is_eaten : bool = False
    time_spawn : int = 0
