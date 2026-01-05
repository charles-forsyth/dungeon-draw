import random
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.rule import Rule

console = Console()


class Card:
    def __init__(self, suit: str, value: int):
        self.suit = suit
        self.value = value
        self.name = self._get_name()

    def _get_name(self) -> str:
        names = {11: "J", 12: "Q", 13: "K", 14: "A"}
        return names.get(self.value, str(self.value))

    def __str__(self) -> str:
        color = "red" if self.suit in ["♥", "♦"] else "white"
        return f"[{color}]{self.name}{self.suit}[/{color}]"


class DungeonDraw:
    def __init__(self, deck: Optional[List[Card]] = None):
        suits = ["♠", "♣", "♥", "♦"]
        if deck is None:
            self.deck = [Card(s, v) for s in suits for v in range(2, 15)]
            random.shuffle(self.deck)
        else:
            self.deck = deck

        self.hp = 20
        self.hand: List[Card] = []
        self.equipment = 0  # Number of Diamonds equipped

        # Draw initial hand
        for _ in range(5):
            if self.deck:
                self.hand.append(self.deck.pop())

    def get_eq_bonus(self) -> int:
        return self.equipment * 2

    def display_status(self) -> None:
        status_table = Table(title="Character Status", show_header=False, box=None)
        status_table.add_row(
            f"HP: [bold red]{self.hp}[/bold red]",
            f"Equipment Bonus: [bold cyan]+{self.get_eq_bonus()}[/bold cyan]",
            f"Deck: {len(self.deck)} cards left",
        )

        hand_str = " | ".join([f"({i + 1}) {str(c)}" for i, c in enumerate(self.hand)])

        console.print(Panel(status_table))
        console.print(Panel(f"YOUR HAND: {hand_str}", title="Inventory"))

    def resolve_monster(self, monster: Card) -> None:
        console.print(f"\n[bold red]BATTLE:[/] You are facing a {monster}")
        self.display_status()

        choices = [str(i + 1) for i in range(len(self.hand))]
        idx = IntPrompt.ask("Choose a card from your hand to play", choices=choices) - 1
        played_card = self.hand.pop(idx)

        roll = random.randint(1, 20)
        suit_match = 5 if played_card.suit == monster.suit else 0
        eq_bonus = self.get_eq_bonus()

        total = played_card.value + roll + suit_match + eq_bonus

        console.print(
            f"\n[bold]Math:[/] {played_card.value} (Card) + {roll} (d20) + {suit_match} (Suit Match) + {eq_bonus} (EQ) = [yellow]{total}[/yellow]"
        )
        console.print("Target: [bold]15[/bold]")

        if total >= 15:
            console.print("[bold green]SUCCESS![/] The monster is defeated.")
        else:
            damage = monster.value
            self.hp -= damage
            console.print(f"[bold red]FAILURE![/] You took {damage} damage.")

        if roll == 1 and self.equipment > 0:
            self.equipment -= 1
            console.print(
                "[bold magenta]CRITICAL FAILURE![/] Your equipment broke! (-2 Bonus)"
            )

    def resolve_room(self) -> bool:
        if len(self.deck) < 6:
            return False

        # 1. ENTRANCE
        entrance = self.deck.pop()
        console.print(Rule(title="NEW ROOM: THE ENTRANCE"))
        self.handle_card(entrance)

        if self.hp <= 0:
            return False

        # 2. THE FORK
        console.print("\n[bold cyan]THE FORK:[/] Two paths lie ahead...")
        c1, c2 = self.deck.pop(), self.deck.pop()
        console.print(f"Left Path: {c1}  |  Right Path: {c2}")
        choice = Prompt.ask("Which path do you take?", choices=["left", "right"])
        self.handle_card(c1 if choice == "left" else c2)

        if self.hp <= 0:
            return False

        # 3. THE CHAMBER
        console.print("\n[bold yellow]THE CHAMBER:[/] Three encounters remain!")
        chamber = [self.deck.pop(), self.deck.pop(), self.deck.pop()]
        while chamber:
            console.print(
                "\nRemaining in Chamber: "
                + " | ".join([f"({i + 1}) {str(c)}" for i, c in enumerate(chamber)])
            )
            choices = [str(i + 1) for i in range(len(chamber))]
            c_idx = IntPrompt.ask("Choose which to face next", choices=choices) - 1
            self.handle_card(chamber.pop(c_idx))
            if self.hp <= 0:
                break

        # Refill Hand
        while len(self.hand) < 5 and self.deck:
            self.hand.append(self.deck.pop())

        return self.hp > 0

    def handle_card(self, card: Card) -> None:
        if card.suit in ["♠", "♣"]:
            self.resolve_monster(card)
        elif card.suit == "♦":
            console.print(f"\n[bold cyan]LOOT:[/] Found a {card}!")
            action = Prompt.ask(
                "Equip for permanent +2, or Stash in hand?", choices=["equip", "stash"]
            )
            if action == "equip":
                if self.equipment < 3:
                    self.equipment += 1
                else:
                    console.print("Equipment slots full! Replaced oldest Diamond.")
            else:
                self.hand.append(card)
        elif card.suit == "♥":
            console.print(
                f"\n[bold green]HEAL:[/] A fountain! Discard a card from hand to heal {card.value} HP?"
            )
            if Prompt.ask("Heal?", choices=["y", "n"]) == "y":
                self.display_status()
                if self.hand:
                    choices = [str(i + 1) for i in range(len(self.hand))]
                    idx = IntPrompt.ask("Discard which card?", choices=choices) - 1
                    self.hand.pop(idx)
                    self.hp += card.value
                    console.print(f"Healed to {self.hp} HP.")
                else:
                    console.print("No cards to discard for healing!")

    def play(self) -> None:
        console.print(
            Panel(
                "[bold green]WELCOME TO DUNGEON DRAW[/bold green]\nTarget: 15 | Suit Match: +5 | Diamonds: +2 EQ"
            )
        )
        while self.hp > 0 and len(self.deck) >= 6:
            if not self.resolve_room():
                break

        if self.hp > 0:
            console.print(
                Panel("[bold yellow]DUNGEON CLEARED![/] You survived the deck.")
            )
        else:
            console.print(
                Panel(
                    "[bold red]GAME OVER[/bold red]\nThe dungeon claimed another soul."
                )
            )


def main() -> None:
    game = DungeonDraw()
    game.play()


if __name__ == "__main__":
    main()
