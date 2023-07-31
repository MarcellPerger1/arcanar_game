from __future__ import annotations

import pprint
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, replace as d_replace, field
from itertools import zip_longest
from typing import TypeVar, Generator, Iterable, cast, Any, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeGuard

T = TypeVar('T')


# region my_enum
# home-made enum that allows subclasses!
class ColorEnumMeta(type):
    def __init__(cls, name: str, bases: tuple[type, ...], ns: dict[str, Any], **kwargs):
        super().__init__(name, bases, ns, **kwargs)
        if not hasattr(cls, '_allowed_names_'):
            cls._allowed_names_: tuple[str, ...] = ()
        if not hasattr(cls, '_name_to_inst_'):
            cls._name_to_inst_: dict[str, Color] = {}

    def __new__(mcls, name, bases, ns, **kwargs):
        return super().__new__(mcls, name, bases, ns, **kwargs)

    def __contains__(cls, item):
        if isinstance(item, cls):
            return item in cls._name_to_inst_.values()
        return item in cls._name_to_inst_

    def __iter__(self) -> Generator[Color, None, None]:
        yield from self._name_to_inst_.values()

    def __len__(self):
        return len(self._allowed_names_)

    def _register(cls, name: str):
        cls._allowed_names_ = cls._allowed_names_ + (name,)
        inst = cls(name)
        setattr(cls, name, inst)
        cls._name_to_inst_[name] = inst
        return inst

    def _finalize(cls):
        cls._is_final = True

    def _init_subclass(cls, **_kwargs):
        cls._is_final = False  # reopen subclass
        cls._name_to_inst_ = cls._name_to_inst_.copy()


@dataclass(init=False, frozen=True)
class ColorEnum(metaclass=ColorEnumMeta):
    _allowed_names_ = ()  # type: tuple[str, ...]
    _name_to_inst_ = {}  # type: dict[str, ColorEnum]
    name: str

    def __init__(self, name: str | ColorEnum):
        def set_name(v: str):
            object.__setattr__(self, 'name', v)

        if isinstance(name, type(self)):
            name = name.name
        else:
            assert isinstance(name, str)
        if name not in self._allowed_names_:
            raise ValueError(f"Invalid name for {type(self).__name__}")
        set_name(name)

    def __new__(cls, name: str | ColorEnum):
        if isinstance(name, cls):
            return name
        if name not in cls._allowed_names_:
            raise ValueError(f"Invalid name for {cls.__name__}")
        return super().__new__(cls)

    @classmethod
    def register(cls, name: str, is_final=False) -> Color:
        if cls._is_final:
            raise ValueError(f"Can't register new "
                             f"{cls.__name__} after finalisation")
        inst = cls._register(name)
        if is_final:
            cls.finalize()
        return inst

    @classmethod
    def finalize(cls):
        cls._finalize()

    def __init_subclass__(cls, **kwargs):
        cls._init_subclass(**kwargs)


# endregion


# region enums
class Color(ColorEnum):
    purple = green = red = blue = yellow = None  # type: Color  # type: ignore


ColorT = TypeVar('ColorT', covariant=True, bound=Color)

Color.register('purple')
Color.register('green')
Color.register('red')
Color.register('blue')
Color.register('yellow', is_final=True)

REAL_COLORS = tuple(Color)
COLOR_ADJACENCY: dict[Color, tuple[Color, ...]] = {
    Color.purple: (Color.green,),
    Color.green: (Color.purple, Color.red),
    Color.red: (Color.green, Color.blue),
    Color.blue: (Color.red, Color.yellow),
    Color.yellow: (Color.blue,)
}


class CardType(Color):
    artifact = spell = None  # type: CardType  # type: ignore


CardType.register('artifact')
# todo rename 'spell' to 'event' as this is ambiguous
CardType.register('spell', is_final=True)


class ColorFilter(Color):
    any_color = except_red = except_yellow = None  # type: ColorFilter  # type: ignore


ColorFilter.register('any_color')
ColorFilter.register('except_red')
ColorFilter.register('except_yellow', is_final=True)


class MoonPhase(Color):
    last_turn = None  # type: MoonPhase


MoonPhase.register('last_turn', is_final=True)


# endregion


class IPaymentMethod(ABC):
    @abstractmethod
    def get_required_resources(self) -> dict[Color, int]:
        ...

    def can_be_bought_by(self, player: Player):
        return player.has_resources(self.get_required_resources())


class ColorPaymentMethod(IPaymentMethod):
    def __init__(self, card: Card):
        self.card = card

    def get_required_resources(self) -> dict[Color, int]:
        if self.card.cost is None:
            return {}
        return {self.card.cost.color: self.card.cost.color_cost}


class WildcardPaymentMethod(IPaymentMethod):
    def __init__(self, card: Card, resources: dict[Color, int]):
        self.card = card
        self.resources = resources

    def get_required_resources(self) -> dict[Color, int]:
        assert sum(self.resources.values()) == self.card.cost.wildcard_cost
        return self.resources


class IAction(ABC):
    def __init__(self, card: Card):
        self.card = card

    card_action: str

    @abstractmethod
    def run(self, game: Game, player: Player):
        ...


class PlaceAction(IAction):
    card_action = 'buy'

    def run(self, game: Game, player: Player):
        player.hand.remove(self.card)
        player.pay_for(self.card)
        player.place_card(self.card)


class RunMagicsAction(IAction):
    card_action = 'discard'

    def run(self, game: Game, player: Player):
        player.discard_from_hand(self.card)
        player.run_magics()


class IChooser(ABC):
    @abstractmethod
    def choose_spend(self, color: ColorFilter, amount: int,
                     player: Player) -> dict[Color, int] | None:
        ...

    @abstractmethod
    def choose_exec_which(self, i: int, total: int) -> Card:
        ...

    @abstractmethod
    def choose_color(self) -> Color:
        ...

    @abstractmethod
    def choose_not_color(self, options: Iterable[Color]) -> Color:
        ...

    @abstractmethod
    def choose_from_discard_of(self, target: Player) -> Card | None:
        """Choose which card to take from discard of target.
        DO NOT modify anything"""
        ...

    @abstractmethod
    def choose_move_which(self) -> Card | None:
        ...

    @abstractmethod
    def choose_move_where(self, options: Iterable[Color]) -> Color:
        ...

    @abstractmethod
    def choose_action(self, player: Player) -> IAction:
        ...

    @abstractmethod
    def choose_payment_method(self, card: Card) -> IPaymentMethod:
        ...


@dataclass(repr=False)
class EffectExecInfo:
    game: Game
    player: Player
    chooser: IChooser
    card: Card


# region card_effects
class CardEffect(ABC):
    @abstractmethod
    def execute(self, info: EffectExecInfo) -> bool:
        ...


@dataclass(frozen=True)
class NullEffect(CardEffect):
    def execute(self, info: EffectExecInfo) -> bool:
        return True


@dataclass(frozen=True)
class GainResource(CardEffect):
    color: Color
    amount: int

    def execute(self, info: EffectExecInfo) -> bool:
        info.player.resources[self.color] += self.amount
        return True


@dataclass(frozen=True)
class GainPoints(CardEffect):
    amount: int

    def execute(self, info: EffectExecInfo) -> bool:
        info.player.points += self.amount
        return True


@dataclass(frozen=True)
class SpendResource(CardEffect):
    color: ColorFilter
    amount: int

    def execute(self, info: EffectExecInfo) -> bool:
        if isinstance(self.color, ColorFilter):
            resources = info.chooser.choose_spend(
                self.color, self.amount, info.player)
            if resources is None:
                return False
            assert info.player.has_resources(resources)
            info.player.subtract_resources(resources)
        if info.player.resources[self.color] >= self.amount:
            info.player.resources[self.color] -= self.amount
            return True
        return False


@dataclass(frozen=True)
class Convert(CardEffect):
    spend: SpendResource | CardEffect
    gain: GainResource | CardEffect
    effect: CardEffect = field(default_factory=NullEffect)

    def __post_init__(self):
        if self.effect is None:
            object.__setattr__(self, 'effect', NullEffect())

    def execute(self, info: EffectExecInfo) -> bool:
        if not self.spend.execute(info):
            return False
        self.gain.execute(info)
        self.effect.execute(info)
        return True


@dataclass(frozen=True)
class AddMarker(CardEffect):
    amount: int = 1

    def execute(self, info: EffectExecInfo) -> bool:
        info.card.markers += self.amount
        return True


@dataclass(frozen=True)
class ForEachMarker(CardEffect):
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        # easiest way to do it (but rather inefficient)
        for _ in range(info.card.markers):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ForEachCardOfType(CardEffect):
    color: CardType
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        for _ in range(info.player.num_cards_of_type(self.color)):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ForEachCardSet(CardEffect):
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        # NOT including artifacts
        n_sets = min(info.player.num_cards_of_type(c) for c in Color)
        for _ in range(n_sets):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ForEachDiscard(CardEffect):
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        for _ in range(len(info.player.discard)):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ForEachMagic(CardEffect):
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        n_cards = sum(info.player.num_cards_of_type(c) for c in Color)
        for _ in range(n_cards):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ForEachEmptyColor(CardEffect):
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        n_types = len(
            [c for c in Color if info.player.num_cards_of_type(c) == 0])
        for _ in range(n_types):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ForEachOfChosenColor(CardEffect):
    effect: CardEffect

    def execute(self, info: EffectExecInfo) -> bool:
        color: Color = info.chooser.choose_color()
        assert color in Color
        for _ in range(info.player.num_cards_of_type(color)):
            self.effect.execute(info)
        return True


@dataclass(frozen=True)
class ChooseFromDiscardOf(CardEffect):
    player_offset: int

    # player_offset:
    # +1 = to left of
    # 0 = this player
    # -1 = to right of
    def execute(self, info: EffectExecInfo) -> bool:
        target = info.game.nth_player_left_of(info.player, self.player_offset)
        if len(target.discard) == 0:
            return False
        card = info.chooser.choose_from_discard_of(target)
        if card is None:
            return False
        assert card.color in Color
        target.discard.remove(card)
        info.player.place_card(card)
        return True


@dataclass(frozen=True)
class ExecuteAnyColorTwice(CardEffect):
    do_evergreens: bool = False

    def execute(self, info: EffectExecInfo) -> bool:
        color: Color = info.chooser.choose_color()
        for c in info.player.magics[color]:
            c.execute_from_other(info)
        if not self.do_evergreens:
            return True
        for this_color in Color:
            if color == this_color or not self.do_evergreens:
                continue
            for c in info.player.magics[color]:
                if c.always_triggers:
                    # need to run twice as normal magics were ran twice
                    c.execute_from_other(info)
                    c.execute_from_other(info)
        return True


@dataclass(frozen=True)
class ExecuteColorsNotBiggest(CardEffect):
    do_evergreens: bool = True

    def execute(self, info: EffectExecInfo) -> bool:
        n_max = 0
        max_colors = []
        for c in Color:
            n = info.player.num_cards_of_type(c)
            if n > n_max:
                n_max = n
                max_colors = [c]
            elif n == n_max:
                max_colors.append(c)
        assert len(max_colors) > 0
        if len(max_colors) == 1:
            not_color = max_colors[0]
        else:
            not_color = info.chooser.choose_not_color(max_colors)
        for color in Color:
            if color != not_color:
                for card in info.player.magics[color]:
                    card.execute_from_other(info)
            elif self.do_evergreens:
                for card in info.player.magics[color]:
                    if card.always_triggers:
                        card.execute_from_other(info)
        return True


@dataclass(frozen=True)
class Execute3TimesAndDiscard(CardEffect):
    def execute(self, info: EffectExecInfo) -> bool:
        card = info.chooser.choose_exec_which(0, 1)
        for _ in range(3):
            if card.is_alive:
                card.execute_from_other(info)
        card.is_alive = False
        return True


@dataclass(frozen=True)
class MoveCardAndRunColor(CardEffect):
    def execute(self, info: EffectExecInfo) -> bool:
        card = info.chooser.choose_move_which()
        if card is None:
            return False
        orig_color = card.effective_color
        assert orig_color is not None
        new_color: Color = info.chooser.choose_move_where(
            COLOR_ADJACENCY[orig_color])
        # move the card
        card.effective_color = new_color
        info.player.magics[orig_color].remove(card)
        info.player.magics[new_color].append(card)
        # execute new color
        for c in info.player.magics[new_color]:
            c.execute_from_other(info)
        return True


@dataclass(frozen=True)
class DiscardThis(CardEffect):
    def execute(self, info: EffectExecInfo) -> bool:
        # IMPORTANT:
        #  We need to be careful when running this as
        #  we might be deleting ourselves from the list currently
        #  being iterated over and executed, causing all sorts of problems.
        #  The easiest way to avoid the problems is to use `for c in cards`,
        #  NOT `for i in range(len(cards))` as python will handle it
        #  correctly that way.
        info.card.setstate_discarded()
        assert info.card.effective_color is not None
        info.player.magics[info.card.effective_color].remove(info.card)
        info.player.discard.append(info.card)
        return True


@dataclass(frozen=True)
class ExecuteCardEffect(CardEffect):
    amount: int = 1

    def execute(self, info: EffectExecInfo) -> bool:
        for i in range(self.amount):
            card_to_exec = info.chooser.choose_exec_which(i, self.amount)
            assert card_to_exec.is_alive
            new_info = d_replace(info, card=card_to_exec)
            card_to_exec.effect.execute(new_info)
        return True


@dataclass(frozen=True)
class ConditionalEffect(CardEffect):
    cond: ICondition
    if_true: CardEffect = field(default_factory=NullEffect)
    if_false: CardEffect = field(default_factory=NullEffect)

    def execute(self, info: EffectExecInfo) -> bool:
        if self.cond.is_true(info):
            self.if_true.execute(info)
        else:
            self.if_false.execute(info)
        return True


def is_iterable(x) -> TypeGuard[Iterable]:
    try:
        iter(x)
    except (TypeError, NotImplementedError):
        return False
    return True


@dataclass(frozen=True, init=False)
class EffectGroup(CardEffect):
    effects: tuple[CardEffect, ...]

    @overload
    def __init__(self, *effects: CardEffect): ...
    @overload
    def __init__(self, effect: tuple[CardEffect, ...], /): ...

    def __init__(self, *effects: CardEffect | tuple[CardEffect, ...]):
        if len(effects) == 1:
            if is_iterable(effects[0]):
                effects = tuple(effects[0])
        object.__setattr__(self, 'effects', effects)

    def execute(self, info: EffectExecInfo) -> bool:
        for e in self.effects:
            e.execute(info)
        return True


class ICondition(ABC):
    @abstractmethod
    def is_true(self, info: EffectExecInfo) -> bool:
        ...


@dataclass(frozen=True)
class DiscardedMin(ICondition):
    amount: int

    def is_true(self, info: EffectExecInfo) -> bool:
        return len(info.player.discard) >= self.amount


@dataclass(frozen=True)
class HasMagicsOfType(ICondition):
    color: CardType
    amount: int

    def is_true(self, info: EffectExecInfo) -> bool:
        return info.player.num_cards_of_type(self.color) >= self.amount


@dataclass(frozen=True)
class MostMagicsOfType(ICondition):
    color: CardType

    def is_true(self, info: EffectExecInfo) -> bool:
        player_magics = info.player.num_cards_of_type(self.color)
        for p in info.game.players:
            num_magics = p.num_cards_of_type(self.color)
            # false if tie for 1st place
            if p != info.player and num_magics >= player_magics:
                return False
        return True


@dataclass(frozen=True)
class HasResource(ICondition):
    color: Color
    amount: int

    def is_true(self, info: EffectExecInfo) -> bool:
        return info.player.resources[self.color] >= self.amount


@dataclass(frozen=True)
class HasMarkers(ICondition):
    amount: int = 1

    def is_true(self, info: EffectExecInfo) -> bool:
        return info.card.markers >= self.amount
# endregion


@dataclass
class Card:
    # static values:
    color: CardType | Color
    effect: CardEffect
    cost: CardCost
    always_triggers: bool = False

    # runtime values:
    effective_color: Color | CardType | None = field(default=None, repr=False)
    is_starting_card: bool = False
    markers: int = 0
    is_alive: bool = field(default=True, repr=False)

    def execute_from_other(self, info: EffectExecInfo):
        return self.effect.execute(d_replace(info, card=self))

    def setstate_discarded(self):
        assert not self.is_starting_card
        self.is_alive = False
        self.effective_color = self.color  # reset position in magics
        # remove all markers
        self.markers = 0


@dataclass(frozen=True)
class CardCost:
    color: Color
    color_cost: int
    wildcard_cost: int


def _make_starting_card(color: Color, effect: CardEffect | None = None):
    if effect is None:
        effect = GainResource(color, 1)
    return Card(color, effect, CardCost(Color.red, 0, 0),
                False, color, is_starting_card=True)


def _make_starting_cards_for_color(color: CardType):
    if color == Color.yellow:
        return [_make_starting_card(Color.yellow, Convert(
            SpendResource(ColorFilter.except_yellow, 1),
            GainResource(Color.yellow, 1)))]
    if color == CardType.artifact:
        return []
    return [_make_starting_card(color)]


class Player:
    def __init__(self, game: Game, idx: int):
        self.game = game
        self.resources: dict[Color, int] = {c: 1 for c in REAL_COLORS}
        self.hand: list[Card] = []
        self.magics: dict[Color | CardType, list[Card]] = self.get_starting_magics()
        self.points = 0
        self.discard: list[Card] = []
        self.idx = idx
        self.chooser: IChooser = TextChooser(self.game, self)
        self.total_points: int | None = None

    def discard_from_hand(self, card: Card):
        self.hand.remove(card)
        card.is_alive = False
        self.discard.append(card)

    @classmethod
    def get_starting_magics(cls):
        return {c: _make_starting_cards_for_color(c)
                for c in (*Color, CardType.artifact)}

    def num_cards_of_type(self, color: CardType | Color) -> int:
        n = 0
        for c in self.magics[color]:
            if not c.is_starting_card:
                n += 1
        return n

    def draw_start_cards(self, deck: list[Card]):
        self.hand = [d_replace(deck.pop()) for _ in range(6)]

    def place_card(self, card: Card, target: CardType | Color | None = None):
        if target is None:
            target = card.color
        if target == CardType.spell:
            card.execute_from_other(self.make_info(card))
            return
        self.magics[target].append(card)
        card.effective_color = target
        card.is_alive = True

    def make_info(self, card: Card):
        return EffectExecInfo(self.game, self, self.chooser, card)

    def run_magics(self):
        for color in Color:
            for card in self.magics[color]:
                is_last = card is self.magics[color][-1]
                if (card.always_triggers
                        or self.game.does_color_run(color, is_last)):
                    card.execute_from_other(self.make_info(card))

    def do_turn(self):
        if __debug__:
            starting_cards = len(self.hand)
            self.chooser.choose_action(self).run(self.game, self)
            assert len(self.hand) == starting_cards - 1
        else:
            self.chooser.choose_action(self).run(self.game, self)

    def pay_for(self, card: Card):
        method = self.chooser.choose_payment_method(card)
        resources = method.get_required_resources()
        self.subtract_resources(resources)

    def subtract_resources(self, resources: dict[Color, int]):
        for color, n in resources.items():
            self.resources[color] -= n

    def count_points(self):
        self.total_points = 0
        for artifact in self.magics[CardType.artifact]:
            artifact.execute_from_other(self.make_info(artifact))
        self.total_points += self.points
        for c in Color:
            # floordiv!
            self.total_points += self.resources[c] // RESOURCE_PER_POINT[c]

    def has_resources(self, resources: dict[Color, int]):
        return all(self.resources[color] >= n
                   for color, n in resources.items())


RESOURCE_PER_POINT: dict[Color, int] = {
    Color.purple: 3,
    Color.green: 3,
    Color.red: -1,
    Color.blue: 3,
    Color.yellow: 1
}
MOON_COLOR_POOL: tuple[Color, ...] = (*Color, *Color)


class Game:
    moon_phases: tuple[tuple[MoonPhase, MoonPhase], ...]
    turn: int
    round_i: int
    winners: list[Player]

    def __init__(self, n_players: int):
        # NOTE: ordering goes clockwise, person to left = index + 1:
        #     2
        #    ^  \
        #   /    v
        #  1     3
        #  ^    /
        #   \  v
        #     0
        self.players = [Player(self, i) for i in range(n_players)]
        self.round_i = 0

    def nth_player_left_of(self, p: Player, n: int = 1):
        return self.players[(p.idx + n) % len(self.players)]

    def prepare_moon_phases(self):
        raw_moon_phases = shuffled(MOON_COLOR_POOL)
        moon_phases = [cast('tuple[MoonPhase, MoonPhase]',
                            tuple(raw_moon_phases.pop() for _ in range(2)))
                       for _ in range(5)] + [(MoonPhase.last_turn,) * 2]
        self.moon_phases = tuple(moon_phases)

    @property
    def current_moon(self) -> tuple[MoonPhase, MoonPhase]:
        return self.moon_phases[self.turn]

    def does_color_run(self, color: Color, is_last: bool) -> bool:
        if self.current_moon != (MoonPhase.last_turn,) * 2:
            return color in self.current_moon
        return is_last

    def prepare_hands(self, round_i: int):
        deck = shuffled(DECKS[round_i])
        for p in self.players:
            p.draw_start_cards(deck)

    def prepare_round(self):
        self.prepare_moon_phases()
        self.prepare_hands(self.round_i)

    def prepare_next_turn(self):
        # rotate cards
        direction = GIVE_DIRN[self.round_i]
        hands_old = [player.hand for player in self.players]
        n_players = len(self.players)
        hands_new: list[list[Card] | None] = [None] * n_players
        for i in range(n_players):
            hands_new[(i + direction) % n_players] = hands_old[i % n_players]
        for i, hand in enumerate(hands_new):
            assert hand is not None
            self.players[i].hand = hand

    def do_turn(self):
        for p in self.players:
            p.do_turn()

    def do_round(self):
        self.prepare_round()
        for self.turn in range(6):
            self.do_turn()
            if self.turn != 5:
                self.prepare_next_turn()

    def run_game(self):
        for self.round_i in range(3):
            self.do_round()
        self.count_points()

    @property
    def winner(self):
        return self.winners[0]

    def count_points(self):
        for p in self.players:
            p.count_points()

        def key(p2: Player):
            return p2.total_points

        self.winners = sorted(self.players, key=key)


# noinspection PyPep8Naming
def _make_decks() -> list[list[Card]]:
    def gain1(color: Color | CardType, cost: CardCost | None = None):
        if cost is None:
            cost = CardCost(r, 0, 0)
        return Card(color, GainResource(color, 1), cost)

    def gain2(color: Color | CardType, cost: CardCost):
        return Card(color, GainResource(color, 2), cost)

    def p_gain2_c1(cond_color: Color | CardType, cost_color: Color):
        cond_color = cast('CardType', cond_color)
        return Card(p,
                    ConditionalEffect(
                        HasMagicsOfType(cond_color, 1),
                        GainResource(p, 2)),
                    CardCost(cost_color, 1, 3))

    def exp_ef(ef: CardEffect):
        return EffectGroup(
            AddMarker(),
            ForEachMarker(ef)
        )

    def only2x(ef: CardEffect):
        return Group(
            ef,
            AddMarker(),
            ConditionalEffect(HasMarkers(), DiscardThis(), AddMarker())
        )

    def conv_ef(src_color: ColorFilter | Color, src_n: int,
                dest_color: Color, dest_n: int,
                effect: CardEffect = NullEffect()) -> CardEffect:
        src_color = cast('ColorFilter', src_color)
        return Convert(SpendResource(src_color, src_n),
                       GainResource(dest_color, dest_n), effect)

    def a_most_5pt(color: CardType | Color):
        color = cast('CardType', color)  # all Color are valid CardType
        return Card(
            a, ConditionalEffect(MostMagicsOfType(color), GainPoints(5)), free)

    def gain_rp(color: Color, color_amount: int, point_amount: int):
        return Group(GainResource(color, color_amount), GainPoints(point_amount))

    def p_cards_gain(req_color: CardType | Color, req_n: int,
                     p_n: int, pt_n: int, cost: CardCost):
        req_color = cast('CardType', req_color)  # all Color are valid CardType
        return Card(p, ConditionalEffect(
            HasMagicsOfType(req_color, req_n),
            gain_rp(p, p_n, pt_n)
        ), cost)

    def p_cards_3pt(req_color: CardType | Color, req_n: int, cost: CardCost):
        req_color = cast('CardType', req_color)  # all Color are valid CardType
        return Card(p, ConditionalEffect(
            HasMagicsOfType(req_color, req_n),
            GainPoints(3)
        ), cost)

    def a_2per_card(color: Color | CardType, pts: int = 2, cost: CardCost | None = None):
        color = cast('CardType', color)  # all Color are valid CardType
        if cost is None:
            cost = Cost(color, 2, 4)
        return Card(a, ForEachCardOfType(color, GainPoints(pts)), cost)

    p, g, r, b, y, a, s = CardType
    nr = ColorFilter.except_red
    ny = ColorFilter.except_yellow
    Cost = CardCost
    Group = EffectGroup
    Cond = ConditionalEffect
    free = Cost(r, 0, 0)
    # keeps these ordered in this way:
    # p, g, r, b, y, a, s
    return [
        [
            # purple
            gain1(p),
            gain2(p, CardCost(g, 2, 3)),
            p_gain2_c1(g, g),
            p_gain2_c1(r, y),
            p_gain2_c1(b, g),
            p_gain2_c1(y, y),
            # green
            gain1(g),
            gain2(g, CardCost(r, 2, 2)),
            Card(g, GainResource(g, 1), Cost(p, 1, 3), True),
            Card(g, GainResource(g, 1), Cost(r, 2, 2), True),
            Card(g, exp_ef(GainResource(g, 1)), Cost(r, 1, 1)),
            Card(g, GainResource(g, 3), Cost(r, 3, 3)),
            # red
            gain1(r),
            gain2(r, Cost(g, 1, 3)),
            Card(r, Group(GainResource(r, 1), GainPoints(1)), Cost(b, 2, 4)),
            Card(r, conv_ef(nr, 1, r, 1, GainPoints(1)), Cost(g, 1, 3)),
            Card(r, exp_ef(GainResource(r, 1)), Cost(b, 1, 3)),
            Card(r, GainResource(r, 3), Cost(g, 2, 4)),
            # blue
            gain1(b),
            gain2(b, Cost(y, 1, 3)),
            Card(b, only2x(GainResource(b, 2)), Cost(r, 2, 2)),
            Card(b, only2x(GainResource(b, 3)), Cost(y, 1, 3)),
            Card(b, only2x(Group(GainResource(b, 2), GainPoints(2))), Cost(y, 1, 3)),
            Card(b, ConditionalEffect(DiscardedMin(3), GainPoints(1)), free),
            # yellow
            Card(y, conv_ef(ny, 1, y, 1), free),
            Card(y, conv_ef(ny, 3, y, 2), Cost(b, 2, 3)),
            Card(y, conv_ef(p, 2, y, 2), Cost(b, 1, 3)),
            Card(y, conv_ef(p, 2, y, 2), Cost(p, 1, 3)),
            Card(y, conv_ef(r, 3, y, 2), Cost(b, 1, 3)),
            Card(y, conv_ef(b, 2, y, 2), Cost(p, 1, 3)),
            # artifacts
            a_most_5pt(p),
            a_most_5pt(g),
            a_most_5pt(r),
            a_most_5pt(b),
            a_most_5pt(y),
            a_most_5pt(a)
        ], [
            # purple
            Card(p, Group(GainResource(p, 3), GainPoints(1)), Cost(g, 3, 6)),
            p_cards_gain(g, 1, 2, 1, Cost(y, 1, 4)),
            p_cards_gain(b, 2, 2, 2, Cost(y, 2, 6)),
            p_cards_gain(b, 2, 2, 2, Cost(g, 1, 3)),
            p_cards_gain(g, 1, 2, 2, Cost(g, 2, 4)),
            # green
            Card(g, Cond(HasResource(g, 6), GainPoints(2)), Cost(p, 3, 5)),
            Card(g, GainPoints(1), Cost(p, 1, 3), True),
            Card(g, gain_rp(g, 1, 1), Cost(r, 4, 4), True),
            Card(g, gain_rp(g, 2, 1), Cost(p, 3, 5)),
            Card(g, exp_ef(gain_rp(g, 1, 1)), Cost(p, 4, 2)),
            # red
            Card(r, gain_rp(r, 2, 1), Cost(g, 2, 4)),
            Card(r, gain_rp(r, 3, 2), Cost(b, 4, 6)),
            Card(r, conv_ef(nr, 4, r, 4, ExecuteCardEffect(1)), Cost(g, 2, 4)),
            Card(r, conv_ef(nr, 3, r, 3, GainPoints(2)), Cost(b, 2, 4)),
            Card(r, exp_ef(gain_rp(r, 1, 1)), Cost(b, 4, 6)),
            # blue
            Card(b, gain_rp(b, 3, 1), Cost(r, 4, 4)),
            Card(b, only2x(GainPoints(2)), Cost(r, 2, 2)),
            Card(b, only2x(GainPoints(3)), Cost(y, 1, 4)),
            Card(b, only2x(gain_rp(b, 2, 2)), Cost(y, 1, 4)),
            Card(b, Cond(DiscardedMin(7), gain_rp(b, 2, 2)), Cost(r, 3, 3)),
            # yellow
            Card(y, conv_ef(ny, 4, y, 3), Cost(r, 5, 5)),
            Card(y, conv_ef(p, 3, y, 3), Cost(p, 2, 4)),
            Card(y, conv_ef(g, 3, y, 3), Cost(p, 2, 4)),
            Card(y, conv_ef(b, 3, y, 3), Cost(p, 2, 4)),
            Card(y, conv_ef(b, 3, y, 3), Cost(b, 2, 4)),
            # artifacts
            a_2per_card(p),
            a_2per_card(g),
            a_2per_card(r, 2, Cost(r, 4, 4)),
            a_2per_card(b, 3),
            a_2per_card(y),
            Card(a, ForEachCardSet(GainPoints(5)), Cost(y, 1, 3)),
            # spells
            Card(s, ChooseFromDiscardOf(1), Cost(g, 1, 3)),
            Card(s, ChooseFromDiscardOf(0), Cost(b, 2, 4)),
            Card(s, ChooseFromDiscardOf(-1), Cost(p, 1, 3)),
            Card(s, ExecuteAnyColorTwice(), Cost(r, 5, 5)),
            Card(s, ExecuteColorsNotBiggest(), Cost(y, 2, 6)),
        ], [
            # purple
            p_cards_3pt(p, 3, Cost(y, 2, 5)),
            p_cards_3pt(g, 2, Cost(y, 1, 4)),
            p_cards_3pt(r, 2, Cost(y, 1, 4)),
            p_cards_3pt(b, 1, Cost(g, 2, 4)),
            p_cards_3pt(y, 2, Cost(g, 2, 4)),
            # green
            Card(g, gain_rp(g, 2, 2), Cost(r, 4, 4)),
            Card(g, Cond(HasResource(g, 6), GainPoints(3)), Cost(r, 4, 4)),
            Card(g, GainPoints(2), Cost(p, 4, 6), True),
            Card(g, GainResource(g, 4), Cost(p, 4, 6), True),
            Card(g, exp_ef(gain_rp(g, 2, 2)), Cost(r, 4, 4)),
            # red
            Card(r, gain_rp(r, 3, 3), Cost(b, 4, 6)),
            Card(r, Cond(HasResource(r, 6), GainPoints(3)), Cost(b, 3, 6)),
            Card(r, conv_ef(nr, 2, r, 2, GainPoints(3)), Cost(g, 2, 5)),
            Card(r, conv_ef(nr, 2, r, 2, ExecuteCardEffect()), Cost(g, 3, 5)),
            Card(r, exp_ef(gain_rp(r, 2, 2)), Cost(g, 4, 7)),
            # blue
            Card(b, gain_rp(b, 2, 2), Cost(y, 1, 4)),
            Card(b, only2x(GainPoints(4)), Cost(y, 2, 6)),
            Card(b, only2x(gain_rp(b, 3, 3)), Cost(r, 6, 6)),
            Card(b, only2x(GainPoints(5)), Cost(r, 7, 7)),
            Card(b, Cond(DiscardedMin(7), GainPoints(3)), Cost(y, 2, 6)),
            # artifacts
            Card(a, GainPoints(4), Cost(r, 4, 4)),
            Card(a, GainPoints(8), Cost(p, 9, 13)),
            Card(a, ForEachEmptyColor(GainPoints(3)), Cost(g, 3, 5)),
            Card(a, ForEachOfChosenColor(GainPoints(2)), Cost(y, 2, 4)),
            Card(a, ForEachMagic(GainPoints(1)), Cost(y, 5, 10)),
            Card(a, ForEachDiscard(GainPoints(1)), Cost(b, 8, 12)),
            # spells
            Card(s, ChooseFromDiscardOf(0), Cost(r, 3, 3)),
            Card(s, ExecuteAnyColorTwice(), Cost(g, 4, 6)),
            Card(s, ExecuteColorsNotBiggest(), Cost(p, 3, 5)),
            Card(s, Execute3TimesAndDiscard(), Cost(b, 3, 5)),
            Card(s, MoveCardAndRunColor(), Cost(y, 2, 6)),
        ]
    ]


DECKS: list[list[Card]] = _make_decks()
GIVE_DIRN = [1, -1, 1]
# todo implement option to skip cards


class InvalidInput(BaseException):
    pass


def _make_str_to_color():
    d = {}
    for color in Color:
        d[color.name] = color
        d[color.name[0]] = color
    d['gold'] = Color.yellow
    return d


STR_TO_COLOR = _make_str_to_color()


# noinspection PyMethodMayBeStatic
class TextChooser(IChooser):
    def __init__(self, game: Game, player: Player):
        self.game = game
        self.player = player

    def choose_spend(self, color_filter: ColorFilter, amount: int,
                     player: Player) -> dict[Color, int] | None:
        self._print_resources()
        while True:
            try:
                return self._choose_spend(color_filter, amount)
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def _choose_spend(self, color_filter: ColorFilter, want_amount: int):
        print('Enter colors to spend (format: <color>=<amount>, ...):')
        s = input().lower().strip()
        if s == 'cancel':
            return None
        colors = self._parse_spend_list(s)
        if sum(colors.values()) != want_amount:
            raise InvalidInput(f"Need total of {want_amount} resources, "
                               f"got {sum(colors.values())}")
        if not self.player.has_resources(colors):
            raise InvalidInput("Not enough resources")
        self._check_resources_match_filter(colors, color_filter)
        return colors

    def _parse_spend_list(self, s: str):
        colors: dict[Color, int] = {c: 0 for c in Color}
        for e in s.split(','):
            if not (e := e.strip()):
                continue
            if len(sides := e.split('=')) != 2:
                raise InvalidInput("Each entry must be <color>=<amount>")
            colors[self._parse_color(sides[0])] += self._parse_int(sides[1])
        return colors

    def _check_resources_match_filter(self, resources: dict[Color, int],
                                      color_filter: ColorFilter):
        if color_filter == ColorFilter.any_color:
            pass
        elif color_filter == ColorFilter.except_yellow:
            if resources[Color.yellow] != 0:
                raise InvalidInput("Can't use yellow resource to spend here")
        elif color_filter == ColorFilter.except_red:
            if resources[Color.red] != 0:
                raise InvalidInput("Can't use red resource to spend here")
        else:
            raise ValueError("Invalid InputFilter")
        return True

    def choose_color(self) -> Color:
        while True:
            try:
                return self._parse_color(input('Choose color: '))
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def choose_not_color(self, options: Iterable[Color]) -> Color:
        options = tuple(options)
        assert len(options) > 1
        options_str = ', '.join(o.name for o in options)
        while True:
            try:
                s = input(f'Choose color not to run '
                          f'(choose from {options_str}): ').lower().strip()
                color = self._parse_color(s)
                if color not in options:
                    raise InvalidInput("Color not in available options")
                return color
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def choose_from_discard_of(self, target: Player) -> Card | None:
        cards = target.discard
        print('Choose a magic card (not artifact or spell)')
        print("Cards in that player's discard pile:")
        pprint.pp(cards)  # lazy method
        while True:
            try:
                s = input(
                    "Enter index of chosen card (0-based): ").strip().lower()
                if s == 'cancel':
                    return None
                i = self._parse_int(s)
                card = self._card_from_list(cards, i)
                if card.color not in Color:
                    # not magic card i.e. is artifact/spell
                    raise InvalidInput(
                        f"The card at index {i} is not a magic "
                        f"card, it is a {card.color.name} card")
                return card
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def choose_move_which(self) -> Card | None:
        print("Choose a magic card to move (not artifact)")
        print("Your magics:")
        pprint.pp(self.player.magics.items())
        while True:
            try:
                return self._choose_move_which()
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def _choose_move_which(self):
        s = input("Enter card to move (<color>,<index>)").strip().lower()
        if s == 'cancel':
            return None
        card = self._extract_card_from_str(s)
        if card.is_starting_card:
            raise InvalidInput(f"Can't move a starting card")
        return card

    def choose_exec_which(self, i: int, total: int) -> Card:
        print("Choose a magic card to run (not artifact)")
        self._print_magics()
        while True:
            try:
                s = input(
                    "Enter card to run (<color>,<index>)").strip().lower()
                return self._extract_card_from_str(s)
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def choose_move_where(self, options: Iterable[Color]) -> Color:
        self._print_magics()
        opts_str = ', '.join(o.name for o in options)
        print(f'Choose where to move the card (options: {opts_str})')
        while True:
            try:
                s = input('Choose which color to move the card to: ')
                color = self._parse_color(s)
                if color not in options:
                    raise InvalidInput("Color is not an available option")
                return color
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def choose_action(self, player: Player) -> IAction:
        print(f'Player {player.idx}\'s turn')
        self._print_magics()
        self._print_hand()
        self._print_resources()
        print('Moon phases', self.game.moon_phases)
        print(f'Current turn: {self.game.turn}')
        tp = self._choose_action_type()
        print(f"Choose a card to {tp.card_action}")
        while True:
            try:
                s = input(f"Enter index of card to {tp.card_action}: ")
                return tp(self._card_from_list(
                    self.player.hand, self._parse_int(s)))
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def _choose_action_type(self) -> type[IAction]:
        while True:
            s = input("Choose action type (buy/magic): ").strip().lower()
            if s in PLACE_ALIASES:
                return PlaceAction
            elif s in RUN_ALIASES:
                return RunMagicsAction
            else:
                print("Invalid input: Unknown action type")

    def choose_payment_method(self, card: Card) -> IPaymentMethod:
        self._print_resources()
        print('Card cost: ', card.cost)
        while True:
            try:
                s = input(
                    "Choose payment type (color/wildcard):").strip().lower()
                if s in COLOR_PAY_ALIASES:
                    method = ColorPaymentMethod(card)
                    if method.can_be_bought_by(self.player):
                        return method
                    raise InvalidInput(
                        f"Not enough resources to buy the card this way "
                        f"(need {card.cost.color_cost} "
                        f"{card.cost.color.name}, you have "
                        f"{self.player.resources[card.cost.color]})")
                elif s in WILDCARD_PAY_ALIASES:
                    if (resources := self._choose_spend(
                            ColorFilter.any_color,
                            card.cost.wildcard_cost)) is not None:
                        return WildcardPaymentMethod(card, resources)
                else:
                    raise InvalidInput("Unknown payment type")
            except InvalidInput as err:
                print("Invalid input:", str(err))

    def _parse_int(self, amount_str: str):
        try:
            return int(amount_str.strip())
        except ValueError:
            raise InvalidInput(f"Unknown number: {amount_str!r}")

    def _parse_color(self, color_str: str):
        try:
            return STR_TO_COLOR[color_str.lower().strip()]
        except KeyError:
            raise InvalidInput(f"Unknown color: {color_str!r}")

    def _card_from_list(self, cards_list: list[Card], idx: int) -> Card:
        try:
            return cards_list[idx]
        except IndexError:
            raise InvalidInput(f"There is no card with index {idx}")

    def _extract_card_from_str(self, s):
        parts = s.strip().lower().split(',', maxsplit=2)
        if len(parts) != 2:
            raise InvalidInput("A card must be in the format <color>,<idx>")
        return self._card_from_list(
            self.player.magics[self._parse_color(parts[0])],
            self._parse_int(parts[1]))

    def _print_resources(self):
        print('You have these resources: ',
              {color.name: self.player.resources[color] for color in Color})

    def _print_magics_2(self, magics: dict[CardType | Color, list[Card]] | None = None):
        if magics is None:
            magics = self.player.magics
        n_boxes_y = 0
        n_boxes_x = len(magics)
        for _, cards in magics.items():
            n_boxes_y = max(n_boxes_y, len(cards))
        want_box_w = 40
        strings = []
        box_ws = []
        box_hs = [0] * n_boxes_y
        for color, cards in magics.items():
            col_strings = []
            box_w = 0
            for i, card in enumerate(cards):
                string = pprint.pformat(card, width=want_box_w, compact=True)
                box_w = max(box_w, max(len(ln) for ln in string.splitlines()))
                box_h = len(string.splitlines())
                box_hs[i] = max(box_hs[i], box_h)
                col_strings.append(string)
            box_ws.append(box_w)
            if len(col_strings) < n_boxes_y:
                col_strings += [''] * (n_boxes_y - len(col_strings))
            strings.append(col_strings)
        rows: list[tuple[str, ...]] = list(zip(*strings))
        rows.insert(0, tuple(c.name.capitalize() for c in magics))
        for i, c in enumerate(magics):
            box_ws[i] = max(box_ws[i], len(c.name))
        for y, row in enumerate(rows):
            full_lines: list[tuple[str, ...]] = list(zip_longest(
                *(string.splitlines() for string in row), fillvalue=''))
            for full_line in full_lines:
                for x, sub_line in enumerate(full_line):
                    print('| ' + sub_line.ljust(box_ws[x]) + ' ', end='')
                print('|')
            for x in range(n_boxes_x):
                print('| ' + '-'*box_ws[x] + ' ', end='')
            print('|')

    def _print_magics(self):
        print("Your magics:")
        # pprint.pp(self.player.magics)
        return self._print_magics_2()

    def _print_hand(self):
        print('Cards in hand:')
        # # use Color to populate dict initially for correct ordering
        # magics: dict[CardType | Color, list[Card]] = {c: [] for c in CardType}
        # for card in self.player.hand:
        #     magics[card.color].append(card)
        # # remove unnecessary columns
        # for color in CardType:
        #     if len(magics[color]) == 0:
        #         del magics[color]
        magics = {_DictToAttr(name=str(i)): [v] for i, v in enumerate(self.player.hand)}
        return self._print_magics_2(magics)


class _DictToAttr:
    def __init__(self, d: dict[str, Any] = None, **kwargs):
        for k, v in ((d or {}) | kwargs).items():
            setattr(self, k, v)


PLACE_ALIASES = {'place', 'put', 'buy', 'purchase', 'get'}
RUN_ALIASES = {'run', 'cast', 'magic', 'execute', 'spells', 'magics'}
COLOR_PAY_ALIASES = {'color', 'colour', 'discount', 'specific', 'single',
                     'normal'}
WILDCARD_PAY_ALIASES = {'wildcard', 'combo', 'any', 'mix',
                        'multi', 'multiple', 'combination'}


def shuffled(it: Iterable[T]) -> list[T]:
    ls = list(it)
    random.shuffle(ls)
    return ls


def main():
    g = Game(3)
    g.run_game()


if __name__ == '__main__':
    main()
