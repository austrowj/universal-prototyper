# Universal Prototyper

A simple text-based prototyping tool for rapidly testing simulation/strategy game mechanics.

Hi.

## Overview

Universal Prototyper is an interactive REPL (Read-Eval-Print Loop) tool that allows game designers to quickly prototype and test game mechanics using a card-based system. Game objects are represented as cards with three fields:
- **Name**: The card's identifier
- **Effect**: Description of what the card does
- **Tags**: List of categories/properties for filtering and organizing

## Features

- **Interactive REPL**: Stateful command-line interface
- **Pile Management**: Create and manage multiple piles (collections) of cards
- **Card Operations**: Move cards between piles by name or tags
- **JSON Import/Export**: Load card lists and save/load entire session states
- **Simple and Fast**: Designed for rapid prototyping and iteration

## Installation

Simply download `prototyper.py` - no additional dependencies required (uses Python standard library only).

## Usage

### Starting the Prototyper

```bash
python3 prototyper.py
```

Or make it executable:

```bash
chmod +x prototyper.py
./prototyper.py
```

### Commands

#### Create a New Pile
```
create <pile_name>
```
Creates a new empty pile with the specified name.

**Example:**
```
prototyper> create deck
Created pile 'deck'.
```

#### Load Cards from JSON
```
load <pile_name> <filename>
```
Loads cards from a JSON file into the specified pile.

**Example:**
```
prototyper> load deck example_cards.json
Loaded 5 card(s) into pile 'deck' from 'example_cards.json'.
```

**JSON Format:**
```json
[
  {
    "name": "Fireball",
    "effect": "Deal 6 damage to target",
    "tags": ["spell", "fire", "damage"]
  },
  {
    "name": "Ice Shield",
    "effect": "Gain 5 armor",
    "tags": ["spell", "ice", "defense"]
  }
]
```

#### Move Card by Name
```
move <from_pile> <to_pile> <card_name>
```
Moves a single card (by name) from one pile to another.

**Example:**
```
prototyper> move deck hand Fireball
Moved card 'Fireball' from 'deck' to 'hand'.
```

#### Move Cards by Tag
```
movetag <from_pile> <to_pile> <tag>
```
Moves all cards with the specified tag from one pile to another.

**Example:**
```
prototyper> movetag deck spells spell
Moved 2 card(s) with tag 'spell' from 'deck' to 'spells'.
```

#### Display Pile Contents
```
show <pile_name>
```
Displays all cards in the specified pile.

**Example:**
```
prototyper> show hand
Pile 'hand' contains 1 card(s):

1. Fireball - Deal 6 damage to target [spell, fire, damage]
```

#### List All Piles
```
piles
```
Lists all existing piles and their card counts.

**Example:**
```
prototyper> piles
Existing piles (3):
  - deck (3 cards)
  - hand (1 card)
  - spells (2 cards)
```

#### Save Session
```
save <filename>
```
Saves the entire session state (all piles and cards) to a JSON file.

**Example:**
```
prototyper> save my_session.json
Session saved to 'my_session.json'.
```

#### Load Session
```
loadsession <filename>
```
Loads a previously saved session, replacing the current state.

**Example:**
```
prototyper> loadsession my_session.json
Session loaded from 'my_session.json'. Loaded 3 pile(s).
```

#### Help
```
help
```
Displays all available commands.

#### Exit
```
quit
```
or
```
exit
```
Exits the prototyper.

## Example Workflow

Here's a typical workflow for prototyping a card game:

```bash
# Start the prototyper
$ python3 prototyper.py

# Create piles for different game zones
prototyper> create deck
prototyper> create hand
prototyper> create discard

# Load some cards
prototyper> load deck example_cards.json

# View what we loaded
prototyper> show deck

# Simulate drawing cards
prototyper> move deck hand Fireball
prototyper> move deck hand Warrior

# View hand
prototyper> show hand

# Move all spell cards to a separate pile
prototyper> create spells
prototyper> movetag deck spells spell

# Check all piles
prototyper> piles

# Save the session for later
prototyper> save game_state.json

# Exit
prototyper> quit
```

## Use Cases

- **Card Game Prototyping**: Test deck compositions and card interactions
- **Strategy Game Mechanics**: Model unit types, abilities, and resource management
- **Simulation Testing**: Quickly iterate on game object properties and behaviors
- **Design Exploration**: Rapidly test different tag-based filtering and categorization schemes

## License

This project is open source and available for use in game design and prototyping.