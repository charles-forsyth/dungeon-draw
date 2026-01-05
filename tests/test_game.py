from dungeon_draw.main import DungeonDraw, Card


def test_card_initialization():
    card = Card("♠", 10)
    assert card.suit == "♠"
    assert card.value == 10
    assert card.name == "10"


def test_card_face_names():
    assert Card("♠", 11).name == "J"
    assert Card("♠", 12).name == "Q"
    assert Card("♠", 13).name == "K"
    assert Card("♠", 14).name == "A"


def test_eq_bonus():
    game = DungeonDraw(deck=[])
    game.equipment = 2
    assert game.get_eq_bonus() == 4


def test_initial_hand():
    # Provide a specific deck to ensure hand is drawn correctly
    deck = [Card("♠", i) for i in range(2, 12)]  # 10 cards
    game = DungeonDraw(deck=deck)
    assert len(game.hand) == 5
    assert len(game.deck) == 5


def test_healing_logic(monkeypatch):
    # Mock inputs for healing: "y" to heal, then "1" to discard first card
    inputs = iter(["y", "1"])
    monkeypatch.setattr("rich.prompt.Prompt.ask", lambda *args, **kwargs: next(inputs))
    monkeypatch.setattr(
        "rich.prompt.IntPrompt.ask", lambda *args, **kwargs: int(next(inputs))
    )

    game = DungeonDraw(deck=[])
    game.hp = 10
    game.hand = [Card("♠", 5)]
    heal_card = Card("♥", 10)

    game.handle_card(heal_card)

    assert game.hp == 20
    assert len(game.hand) == 0
