from typing import Optional

import tcod.event

from actions import Action, EscapeAction, MovementAction

class EventHandler(tcod.event.EventDispatch[Action]):
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        match event.sym:
            case tcod.event.KeySym.UP:
                return MovementAction(dx=0, dy=-1)
            case tcod.event.KeySym.DOWN:
                return MovementAction(dx=0, dy=1)
            case tcod.event.KeySym.LEFT:
                return MovementAction(dx=-1, dy=0)
            case tcod.event.KeySym.RIGHT:
                return MovementAction(dx=1, dy=0)
            case tcod.event.KeySym.ESCAPE:
                return EscapeAction()
            case _:
                return None
