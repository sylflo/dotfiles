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
        #raise Exception(self, widget, monitor_name)

    # def select_image(self, image_name: str):
    #     if self._selected_image != image_name:
    #         self._selected_image = image_name
    #         self.image_selected.emit(image_name)

    # def get_selected_image(self):
    #     return self._selected_image
