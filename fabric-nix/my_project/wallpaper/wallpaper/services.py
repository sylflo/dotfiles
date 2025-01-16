from fabric.core.service import Service, Signal
from fabric.widgets.eventbox import EventBox


class Pagination(Service):
    @Signal
    def next_page(self) -> None:
        pass

    @Signal
    def previous_page(self) -> None:
        pass

    @Signal
    def go_to_page(self, page_number: int) -> None:
        pass

    @Signal
    def select_monitor(self, widget: EventBox, monitor_name: str) -> None:
        pass

    @Signal
    def select_image(self, widget: EventBox, image_name: str) -> None:
        pass
