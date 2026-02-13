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

@dataclass
class Brick(Passenger): pass

@dataclass
class VIP(Passenger): pass

@dataclass
class Mechanic(Passenger): pass

@dataclass
class Elevator:
    floor: int = 0
    doors_open: bool = True
    going_to: list[int] = field(default_factory = list[int])
    capacity: int = 0
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
    score: int = 0
    failed: bool = False
    time: int = 0
    power: int = 0

    floors: list[Floor] = field(default_factory = list[Floor])
    elevators: list[Elevator] = field(default_factory = list[Elevator])

passenger_pool = {
    Passenger: 10,
    Brick: 0,
    VIP: 3,
    Mechanic: 1,
}
passenger_pool_total = sum(v for v in passenger_pool.values())

def main_loop(initial_state: State):
    state = initial_state
    events = []
    while (not state.failed):
        print()
        pprint(state, width = 1)
        for event in events:
            print(event)

        action: Action = input('> ')
        state, events = handle(state, action)
    
    print()
    pprint(state, width = 1)
    for event in events:
        print(event)

def handle(state: State, action: Action) -> tuple[State, list[Event]]:
    if action == 'quit': exit()

    elif action == '': return update(state)
    
    elif action.startswith('go'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            if len(args) != 2: raise Exception()
            if args[0] >= len(state.elevators) or args[1] >= len(state.floors): raise Exception()
            if args[0] < 0 or args[1] < 0: raise Exception()
            
            state.elevators[args[0]].going_to.append(args[1])

        except Exception:
            print('Invalid "go" command, need <elevator>, <target floor>.')
    
    elif action.startswith('dump'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            if len(args) != 1: raise Exception()
            if args[0] < 0 or args[0] >= len(state.elevators): raise Exception

            elevator = state.elevators[args[0]]
            if elevator.floor < len(state.floors)-1: raise Exception()
            
            print(f'{len(elevator.passengers)} passengers dumped into the pit.')
            elevator.passengers = []

        except Exception:
            print(f'Invalid "dump" command, need <elevator> on floor {len(state.floors)-1}.')

    elif action.startswith('close'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            if len(args) != 1: raise Exception()
            if args[0] < 0 or args[0] >= len(state.elevators): raise Exception

            elevator = state.elevators[args[0]]
            
            print(f"Forcibly closed elevator {args[0]}'s door.")
            elevator.doors_open = False

        except Exception:
            print(f'Invalid "close" command, need <elevator>.')

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
                # Only the front passenger can get out.
                passenger = elevator.passengers.pop(0)

                if passenger.target_floor == elevator.floor:
                    state, debark_events = handle_debark(state, passenger)
                    events.append(f'🎉 Elevator {i} dropped off a passenger.')
                    events.extend(debark_events)
                else:
                    # Push to front of line.
                    floor.passengers.insert(0, passenger)

            elif floor.passengers and len(elevator.passengers) < elevator.capacity:
                # Elevator passengers are a stack.
                elevator.passengers.insert(0, floor.passengers.pop(0))
                if len(elevator.passengers) == elevator.capacity:
                    events.append(f'⛔  Elevator {i} is now full.')

            else:
                elevator.doors_open = False
                if not elevator.going_to:
                    events.append(f'❇️  Elevator {i} ready to move.')
        
        elif elevator.going_to:
            if elevator.going_to[0] == elevator.floor:
                elevator.going_to.pop(0)
                elevator.doors_open = True
            elif elevator.going_to[0] < elevator.floor:
                elevator.floor -= 1
                state.power -= 1
            else:
                elevator.floor += 1
    
    # Randomly add passengers
    if random.random() < state.config.arrival_rate:

        origin_floor = random.randrange(0, len(state.floors))

        # Choose among the other floors at random
        target_floor = random.randrange(0, len(state.floors) - 1)
        if target_floor >= origin_floor:
            target_floor += 1
        
        # Choose among available passengers
        passenger_roll = random.randrange(0, passenger_pool_total)
        for PassengerConstructor, weight in passenger_pool.items():
            if passenger_roll < weight:
                passenger = PassengerConstructor(target_floor = target_floor)
                break
            else:
                passenger_roll -= weight
        else:
            raise Exception('Passenger roll mechanism generated an invalid roll.')

        state.floors[origin_floor].passengers.append(passenger)
        events.append(f'‼️  New passenger waiting at floor {origin_floor}.')

    if state.power <= 0:
        state.failed = True
        events.append(f'⚡  Power lost, game over. Final score: {state.score}')

    return state, events

def handle_debark(state: State, passenger: Passenger) -> tuple[State, list[Event]]:
    events: list[Event] = []
    if isinstance(passenger, VIP):
        state.score += 10
        events.append('Bonus score!')
    elif isinstance(passenger, Mechanic):
        state.power += 5
        events.append('Gained power!')
    elif isinstance(passenger, Brick):
        state.score -= 5
        events.append('Lost points by delivering brick.')
    else:
        state.score += 1
    
    return state, events

if __name__ == '__main__':
    main_loop(State(
        config = Config(float(sys.argv[3])),
        power = 20,
        floors = [Floor() for _ in range(int(sys.argv[1]))],
        elevators = [Elevator(floor=0, capacity=5) for _ in range(int(sys.argv[2]))],
    ))
