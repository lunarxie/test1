from enum import Enum


class NodeType(Enum):
    SUSCEPTIBLE = 1
    EXPOSED = 2
    INFECT = 3
    RECOVERED = 4

    BIRTH = 5
    DEATH = 6
