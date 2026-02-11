#!/usr/bin/env python3
"""
Universal Prototyper - A simple text-based prototyping tool for rapidly testing 
simulation/strategy game mechanics.
"""

import json
import sys
from typing import List, Dict, Optional


class Card:
    """Represents a game object with name, effect, and tags."""
    
    def __init__(self, name: str, effect: str = "", tags: Optional[List[str]] = None):
        self.name = name
        self.effect = effect
        self.tags = tags if tags is not None else []
    
    def to_dict(self) -> Dict:
        """Convert card to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "effect": self.effect,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Card':
        """Create card from dictionary."""
        return cls(
            name=data.get("name", ""),
            effect=data.get("effect", ""),
            tags=data.get("tags", [])
        )
    
    def __str__(self) -> str:
        tags_str = ", ".join(self.tags) if self.tags else "none"
        return f"Card: {self.name}\n  Effect: {self.effect}\n  Tags: {tags_str}"
    
    def has_tag(self, tag: str) -> bool:
        """Check if card has a specific tag."""
        return tag in self.tags


class Pile:
    """Represents a collection of cards."""
    
    def __init__(self, name: str):
        self.name = name
        self.cards: List[Card] = []
    
    def add_card(self, card: Card):
        """Add a card to the pile."""
        self.cards.append(card)
    
    def remove_card(self, card: Card) -> bool:
        """Remove a card from the pile. Returns True if successful."""
        try:
            self.cards.remove(card)
            return True
        except ValueError:
            return False
    
    def find_card_by_name(self, name: str) -> Optional[Card]:
        """Find a card by exact name match."""
        for card in self.cards:
            if card.name == name:
                return card
        return None
    
    def find_cards_by_tag(self, tag: str) -> List[Card]:
        """Find all cards with a specific tag."""
        return [card for card in self.cards if card.has_tag(tag)]
    
    def to_dict(self) -> Dict:
        """Convert pile to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "cards": [card.to_dict() for card in self.cards]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Pile':
        """Create pile from dictionary."""
        pile = cls(data.get("name", ""))
        for card_data in data.get("cards", []):
            pile.add_card(Card.from_dict(card_data))
        return pile
    
    def __str__(self) -> str:
        if not self.cards:
            return f"Pile '{self.name}' is empty."
        
        result = f"Pile '{self.name}' contains {len(self.cards)} card(s):\n"
        for i, card in enumerate(self.cards, 1):
            result += f"\n{i}. {card.name}"
            if card.effect:
                result += f" - {card.effect}"
            if card.tags:
                result += f" [{', '.join(card.tags)}]"
        return result


class Prototyper:
    """Main REPL for the prototyping tool."""
    
    def __init__(self):
        self.piles: Dict[str, Pile] = {}
        self.running = True
    
    def create_pile(self, pile_name: str):
        """Create a new pile."""
        if pile_name in self.piles:
            print(f"Error: Pile '{pile_name}' already exists.")
            return
        
        self.piles[pile_name] = Pile(pile_name)
        print(f"Created pile '{pile_name}'.")
    
    def load_cards(self, pile_name: str, filename: str):
        """Load cards from JSON file into a pile."""
        if pile_name not in self.piles:
            print(f"Error: Pile '{pile_name}' does not exist. Create it first.")
            return
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Support both list of cards and object with cards array
            cards_data = data if isinstance(data, list) else data.get("cards", [])
            
            count = 0
            for card_data in cards_data:
                card = Card.from_dict(card_data)
                self.piles[pile_name].add_card(card)
                count += 1
            
            print(f"Loaded {count} card(s) into pile '{pile_name}' from '{filename}'.")
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file '{filename}'.")
        except Exception as e:
            print(f"Error loading cards: {e}")
    
    def move_card(self, from_pile: str, to_pile: str, identifier: str, by_tag: bool = False):
        """Move card(s) from one pile to another by name or tag."""
        if from_pile not in self.piles:
            print(f"Error: Source pile '{from_pile}' does not exist.")
            return
        
        if to_pile not in self.piles:
            print(f"Error: Destination pile '{to_pile}' does not exist.")
            return
        
        source = self.piles[from_pile]
        dest = self.piles[to_pile]
        
        if by_tag:
            # Move all cards with matching tag
            cards = source.find_cards_by_tag(identifier)
            if not cards:
                print(f"No cards with tag '{identifier}' found in pile '{from_pile}'.")
                return
            
            for card in cards:
                source.remove_card(card)
                dest.add_card(card)
            
            print(f"Moved {len(cards)} card(s) with tag '{identifier}' from '{from_pile}' to '{to_pile}'.")
        else:
            # Move single card by name
            card = source.find_card_by_name(identifier)
            if not card:
                print(f"Card '{identifier}' not found in pile '{from_pile}'.")
                return
            
            source.remove_card(card)
            dest.add_card(card)
            print(f"Moved card '{identifier}' from '{from_pile}' to '{to_pile}'.")
    
    def show_pile(self, pile_name: str):
        """Display contents of a pile."""
        if pile_name not in self.piles:
            print(f"Error: Pile '{pile_name}' does not exist.")
            return
        
        print(self.piles[pile_name])
    
    def list_piles(self):
        """List all existing piles."""
        if not self.piles:
            print("No piles created yet.")
            return
        
        print(f"Existing piles ({len(self.piles)}):")
        for pile_name, pile in self.piles.items():
            print(f"  - {pile_name} ({len(pile.cards)} cards)")
    
    def save_session(self, filename: str):
        """Save entire session state to JSON file."""
        try:
            data = {
                "piles": {name: pile.to_dict() for name, pile in self.piles.items()}
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"Session saved to '{filename}'.")
        
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def load_session(self, filename: str):
        """Load entire session state from JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.piles = {}
            for pile_name, pile_data in data.get("piles", {}).items():
                self.piles[pile_name] = Pile.from_dict(pile_data)
            
            print(f"Session loaded from '{filename}'. Loaded {len(self.piles)} pile(s).")
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in file '{filename}'.")
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def show_help(self):
        """Display help information."""
        help_text = """
Universal Prototyper - Available Commands:

  create <pile_name>
      Create a new pile with the given name.
  
  load <pile_name> <filename>
      Load cards from a JSON file into the specified pile.
      JSON format: [{"name": "...", "effect": "...", "tags": ["..."]}]
  
  move <from_pile> <to_pile> <card_name>
      Move a card by name from one pile to another.
  
  movetag <from_pile> <to_pile> <tag>
      Move all cards with the specified tag from one pile to another.
  
  show <pile_name>
      Display the contents of a pile.
  
  piles
      List all existing piles and their card counts.
  
  save <filename>
      Save the entire session state to a JSON file.
  
  loadsession <filename>
      Load a previously saved session from a JSON file.
  
  help
      Display this help message.
  
  quit / exit
      Exit the prototyper.
"""
        print(help_text)
    
    def parse_command(self, line: str):
        """Parse and execute a command."""
        parts = line.strip().split()
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        try:
            if cmd in ('quit', 'exit'):
                self.running = False
                print("Goodbye!")
            
            elif cmd == 'help':
                self.show_help()
            
            elif cmd == 'create':
                if len(parts) < 2:
                    print("Usage: create <pile_name>")
                else:
                    self.create_pile(parts[1])
            
            elif cmd == 'load':
                if len(parts) < 3:
                    print("Usage: load <pile_name> <filename>")
                else:
                    self.load_cards(parts[1], parts[2])
            
            elif cmd == 'move':
                if len(parts) < 4:
                    print("Usage: move <from_pile> <to_pile> <card_name>")
                else:
                    # Allow card names with spaces (join remaining parts)
                    card_name = ' '.join(parts[3:])
                    self.move_card(parts[1], parts[2], card_name)
            
            elif cmd == 'movetag':
                if len(parts) < 4:
                    print("Usage: movetag <from_pile> <to_pile> <tag>")
                else:
                    # Allow tag names with spaces (join remaining parts)
                    tag = ' '.join(parts[3:])
                    self.move_card(parts[1], parts[2], tag, by_tag=True)
            
            elif cmd == 'show':
                if len(parts) < 2:
                    print("Usage: show <pile_name>")
                else:
                    self.show_pile(parts[1])
            
            elif cmd == 'piles':
                self.list_piles()
            
            elif cmd == 'save':
                if len(parts) < 2:
                    print("Usage: save <filename>")
                else:
                    self.save_session(parts[1])
            
            elif cmd == 'loadsession':
                if len(parts) < 2:
                    print("Usage: loadsession <filename>")
                else:
                    self.load_session(parts[1])
            
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
        
        except Exception as e:
            print(f"Error executing command: {e}")
    
    def run(self):
        """Start the REPL."""
        print("=" * 60)
        print("Universal Prototyper - Text-based Game Mechanic Tester")
        print("=" * 60)
        print("Type 'help' for available commands.")
        print()
        
        while self.running:
            try:
                line = input("prototyper> ")
                self.parse_command(line)
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nUse 'quit' or 'exit' to leave.")
                continue


def main():
    """Entry point for the prototyper."""
    prototyper = Prototyper()
    prototyper.run()


if __name__ == '__main__':
    main()
