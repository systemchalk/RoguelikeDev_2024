from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import tcod.event

from actions import Action, BumpAction, EscapeAction

if TYPE_CHECKING:
    from engine import Engine

class EventHandler(tcod.event.EventDispatch[Action]):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            action = self.dispatch(event)

            if action is None:
                continue

            action.perform()

            self.engine.handle_enemy_turns()
            self.engine.update_fov() # Update the FOV before the player's next action.

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        player = self.engine.player
        
        match event.sym:
            case tcod.event.KeySym.UP:
                return BumpAction(player, dx=0, dy=-1)
            case tcod.event.KeySym.DOWN:
                return BumpAction(player, dx=0, dy=1)
            case tcod.event.KeySym.LEFT:
                return BumpAction(player, dx=-1, dy=0)
            case tcod.event.KeySym.RIGHT:
                return BumpAction(player, dx=1, dy=0)
            case tcod.event.KeySym.ESCAPE:
                return EscapeAction(player)
            case _:
                return None
