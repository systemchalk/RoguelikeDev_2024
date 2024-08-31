"""Exceptions that are unique to the game."""


class Impossible(Exception):  # noqa: N818
    """Exception raised when an action is impossible to be performed.

    The reason is given as the exception message
    """


class QuitWithoutSaving(SystemExit):
    """Can be raised to exit the game without automatically saving."""
