from typing import Any, List

from v4l2 cimport (V4L2_CTRL_FLAG_DISABLED, V4L2_CTRL_FLAG_GRABBED,
                   V4L2_CTRL_FLAG_READ_ONLY, V4L2_CTRL_FLAG_UPDATE,
                   V4L2_CTRL_FLAG_INACTIVE, V4L2_CTRL_FLAG_WRITE_ONLY)


class CameraControl:
    def __init__(self, id_: int, type_: int, name: str, default_value: Any,
                 minimum: int, maximum: int, step: int, menu: List[str],
                 flags: int):
        self.id = id_
        self.type = type_
        self.name = name
        self.default_value = default_value
        self.minimum = minimum
        self.maximum = maximum
        self.step = step
        self.menu = menu
        self._flags = flags

    @property
    def is_disabled(self) -> bool:
        """This control is permanently disabled and should be ignored
        by the application."""
        return self._flags & V4L2_CTRL_FLAG_DISABLED

    @property
    def is_grabbed(self) -> bool:
        """This control is temporarily unchangeable, for example because
        another application took over control of the respective resource."""
        return self._flags & V4L2_CTRL_FLAG_GRABBED

    @property
    def is_read_only(self) -> bool:
        """This control is permanently readable only."""
        return self._flags & V4L2_CTRL_FLAG_READ_ONLY

    @property
    def updates_others(self) -> bool:
        """A hint that changing this control may affect the value of other
        controls within the same control class."""
        return self._flags & V4L2_CTRL_FLAG_UPDATE

    @property
    def is_inactive(self) -> bool:
        """This control is not applicable to the current configuration and
        should be displayed accordingly in a user interface."""
        return self._flags & V4L2_CTRL_FLAG_INACTIVE

    @property
    def is_write_only(self) -> bool:
        """This control is permanently writable only. Any attempt to read the
         control will result in an EACCES error code error code."""
        return self._flags & V4L2_CTRL_FLAG_WRITE_ONLY
