#!/usr/bin/env python3
#pyright: strict

from dataclasses import dataclass, field
from pprint import pprint
import random
import sys

type Action = str
type Event = str

@dataclass
class Passenger:
    target_floor: int
    t: int
    #value: int

@dataclass
class Elevator:
    floor: int = 0
    doors_open: bool = True
    going_to: list[int] = field(default_factory = list[int])
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
    events = []
    while (not state.failed):
        print()
        pprint(state, width=1)
        if (events):
            for event in events:
                print(event)

        action: Action = input('> ')
        state, events = handle(state, action)

def handle(state: State, action: Action) -> tuple[State, list[Event]]:
    if action == 'quit': exit()

    elif action == '': return update(state)
    
    elif action.startswith('go'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            if len(args) != 2:
                raise Exception()
            if args[0] >= len(state.elevators) or args[1] >= len(state.floors):
                raise Exception()
            if args[0] < 0 or args[1] < 0:
                raise Exception()
            
            state.elevators[args[0]].going_to.append(args[1])

        except Exception:
            print('Invalid "go" command, need <elevator>, <target floor>.')

    else:
        print('Invalid action.')
    
    return state, []

def update(state: State) -> tuple[State, list[Event]]:
    events: list[Event] = []
    state.time += 1

    # Move passengers out of elevators
    for i, elevator in enumerate(state.elevators):

        if elevator.doors_open:
            floor = state.floors[elevator.floor]

            getting_out = -1
            for j, passenger in enumerate(elevator.passengers):
                if passenger.target_floor == elevator.floor:
                    getting_out = j

            if getting_out >= 0:
                passenger = elevator.passengers.pop(getting_out)
                state.score += 1
                events.append(f'🎉 Passenger got out of elevator {i} at floor {elevator.floor} after waiting {state.time - passenger.t} minutes!')
            elif floor.passengers:
                elevator.passengers.append(floor.passengers.pop(0))
            else:
                elevator.doors_open = False
                if not elevator.going_to:
                    events.append(f'❇️  Elevator {i} ready to move')
        
        elif elevator.going_to:
            if elevator.going_to[0] == elevator.floor:
                elevator.going_to.pop(0)
                elevator.doors_open = True
            elif elevator.going_to[0] < elevator.floor:
                elevator.floor -= 1
            else:
                elevator.floor += 1
    
    # Randomly add passengers
    if random.random() < state.config.arrival_rate:

        origin_floor = random.randrange(0, len(state.floors))

        # Choose among the other floors at random
        target_floor = random.randrange(0, len(state.floors) - 1)
        if target_floor >= origin_floor:
            target_floor += 1

        state.floors[origin_floor].passengers.append(Passenger(target_floor = target_floor, t = state.time))
        events.append(f'‼️  New passenger waiting at floor {origin_floor}')

    return state, events

if __name__ == '__main__':
    main_loop(State(
        config = Config(float(sys.argv[3])),
        floors = [Floor() for _ in range(int(sys.argv[1]))],
        elevators = [Elevator(floor=0) for _ in range(int(sys.argv[2]))],
    ))
