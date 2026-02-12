#!/usr/bin/env python3

from dataclasses import dataclass, field
from pprint import pprint
import random
import sys

type Action = str

@dataclass
class Passenger:
    target_floor: int
    value: int

@dataclass
class Elevator:
    floor: int = 0
    doors_open: bool = True
    pressed: list[int] = field(default_factory = list[int])
    passengers: list[Passenger] = field(default_factory = list[Passenger])

@dataclass
class Floor:
    passengers: list[Passenger] = field(default_factory = list[Passenger])

@dataclass
class Config:
    arrival_rate: float = 0

@dataclass
class State:
    config: Config = field(default_factory = lambda: Config())
    failed: bool = False
    time: int = 0
    score: int = 0

    floors: list[Floor] = field(default_factory = list[Floor])
    elevators: list[Elevator] = field(default_factory = list[Elevator])

def main_loop(initial_state: State):
    state = initial_state
    while (not state.failed):
        print()
        pprint(state, width=1)
        action: Action = input('> ')
        state = handle(state, action)

def handle(state: State, action: Action) -> State:
    if action == 'quit': exit()
    elif action == '': return update(state)
    elif action.startswith('press'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            state.elevators[args[0]].pressed.append(args[1])
        except Exception:
            print('Invalid "press" command, need <floor>, <elevator>, <target floor>.')

    else:
        print('Invalid action.')
    
    return state

def update(state: State) -> State:
    state.time += 1

    # Move passengers out of elevators
    for _, elevator in enumerate(state.elevators):

        if elevator.doors_open:
            floor = state.floors[elevator.floor]

            getting_out = -1
            for j, passenger in enumerate(elevator.passengers):
                if passenger.target_floor == elevator.floor:
                    getting_out = j

            if getting_out >= 0:
                state.score += elevator.passengers.pop(getting_out).value
            elif floor.passengers:
                elevator.passengers.append(floor.passengers.pop(0))
            else:
                elevator.doors_open = False
        
        elif elevator.pressed:
            if elevator.pressed[0] == elevator.floor:
                elevator.pressed.pop(0)
                elevator.doors_open = True
            elif elevator.pressed[0] < elevator.floor:
                elevator.floor -= 1
            else:
                elevator.floor += 1
    
    # Randomly add passengers
    if random.random() < state.config.arrival_rate:
        random.choice(state.floors).passengers.append(Passenger(
            target_floor = random.randrange(0, len(state.floors)),
            value = 1
        ))

    return state

if __name__ == '__main__':
    main_loop(State(
        config = Config(float(sys.argv[3])),
        floors = [Floor() for _ in range(int(sys.argv[1]))],
        elevators = [Elevator(floor=0) for _ in range(int(sys.argv[2]))],
    ))
