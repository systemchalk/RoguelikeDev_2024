"""Log of actions and events in game."""
from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING, Iterable, Reversible

import color

if TYPE_CHECKING:
    import tcod


class Message:
    """Messages are text, colours, and number of occurances."""

    def __init__(self, text: str, fg: tuple[int, int, int]) -> None:
        """Intialize a message with text, a foreground colour, and count=1."""
        self.plain_text = text
        self.fg = fg
        self.count = 1

    @property
    def full_text(self) -> str:
        """The full text of this message, including the count if necessary."""
        if self.count > 1:
            return f"{self.plain_text} (x{self.count})"
        return self.plain_text


class MessageLog:
    """MessageLog collects messages and renders them."""

    def __init__(self) -> None:
        """Prepare a MessageLog with an empty list of messages."""
        self.messages: list[Message] = []

    def add_message(
        self, text: str, fg: tuple[int, int, int] = color.white, *,
        stack: bool = True,
    ) -> None:
        """Add a message to this log.

        'text' is the message text, 'fg' is the text color.
        If 'stack' is True then the message can stack with a previous message
        of the same text.
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(
        self, console: tcod.console.Console, x: int, y: int, width: int,
        height: int,
    ) -> None:
        """Render this log over the given area.

        'x', 'y', 'width', 'height' is the rectangular region to render onto
        the 'console'.
        """
        self.render_messages(console, x, y, width, height, self.messages)

    @staticmethod
    def wrap(string: str, width: int) -> Iterable[str]:
        """Return a wrapped text mssage."""
        for line in string.splitlines():  # Handle newlines in messages.
            yield from textwrap.wrap(
                line, width, expand_tabs=True,
            )

    @classmethod
    def render_messages(  # noqa: PLR0913
        cls,
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
        messages: Reversible[Message],
    ) -> None:
        """Render the messages provided.

        The 'messages' are rendered starting at the last message and working
        backwards.
        """
        y_offset = height - 1

        for message in reversed(messages):
            for line in reversed(list(cls.wrap(message.full_text, width))):
                console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
                y_offset -= 1
                if y_offset < 0:
                    return  # No more space to print messages.
