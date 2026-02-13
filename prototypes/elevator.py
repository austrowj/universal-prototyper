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
    time_remaining: int = 0

    floors: list[Floor] = field(default_factory = list[Floor])
    elevators: list[Elevator] = field(default_factory = list[Elevator])

    events: list[Event] = field(default_factory = list[Event])

passenger_pool = {
    Passenger: 10,
    Brick: 0,
    VIP: 3,
    Mechanic: 1,
}
passenger_pool_total = sum(v for v in passenger_pool.values())

def main_loop(initial_state: State):
    state = initial_state
    while (sum(len(x.passengers) for x in state.floors) == 0):
        state = update(state)

    while (not state.failed):
        print()
        pprint(state, width = 80)

        action: Action = input('> ')
        state.events = []
        state = handle_action(state, action)
    
    print()
    pprint(state, width = 80)

def handle_action(state: State, action: Action) -> State:
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
            state.events.append('❌ Invalid "go" command, need <elevator>, <target floor>.')
    
    elif action.startswith('dump'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            if len(args) != 1: raise Exception()
            if args[0] < 0 or args[0] >= len(state.elevators): raise Exception

            elevator = state.elevators[args[0]]
            if elevator.floor < len(state.floors)-1: raise Exception()
            
            state.events.append(f'{len(elevator.passengers)} passengers dumped into the pit.')
            elevator.passengers = []

        except Exception:
            state.events.append(f'❌ Invalid "dump" command, need <elevator> on floor {len(state.floors)-1}.')

    elif action.startswith('close'):
        try:
            args = [int(x) for x in action.split(' ')[1:]]
            if len(args) != 1: raise Exception()
            if args[0] < 0 or args[0] >= len(state.elevators): raise Exception

            elevator = state.elevators[args[0]]
            
            state.events.append(f"🔒 Forcibly closed elevator {args[0]}'s door.")
            elevator.doors_open = False

        except Exception:
            state.events.append(f'❌ Invalid "close" command, need <elevator>.')

    else:
        state.events.append(f'❌ Invalid action: "{action}".')
    
    return state

def update(state: State) -> State:
    state.time_remaining -= 1

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
                    state.events.append(f'🎉 Elevator {i} dropped off a passenger.')
                    state = handle_debark(state, passenger)
                else:
                    # Push to front of line.
                    floor.passengers.insert(0, passenger)

            elif floor.passengers and len(elevator.passengers) < elevator.capacity:
                # Elevator passengers are a stack.
                elevator.passengers.insert(0, floor.passengers.pop(0))
                if len(elevator.passengers) == elevator.capacity:
                    state.events.append(f'⛔  Elevator {i} is now full.')

            else:
                elevator.doors_open = False
                if not elevator.going_to:
                    state.events.append(f'❇️  Elevator {i} ready to move.')
        
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
        state.events.append(f'‼️  New passenger waiting at floor {origin_floor}.')

    if state.time_remaining <= 0:
        state.failed = True
        state.events.append(f'⌛ Out of time. Final score: {state.score}')

    return state

def handle_debark(state: State, passenger: Passenger) -> State:
    if isinstance(passenger, VIP):
        state.score += 11
        state.events.append('📈  +10 bonus score!')
    elif isinstance(passenger, Mechanic):
        state.time_remaining += 20
        state.events.append('⏳  +20 time gained!')
    elif isinstance(passenger, Brick):
        state.score -= 5
        state.events.append('😞 -5 score from delivering brick.')
    else:
        state.score += 1
    
    return state

if __name__ == '__main__':
    main_loop(State(
        config = Config(float(sys.argv[3])),
        time_remaining = 110,
        floors = [Floor() for _ in range(int(sys.argv[1]))],
        elevators = [Elevator(floor=0, capacity=5) for _ in range(int(sys.argv[2]))],
    ))
