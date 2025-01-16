from fabric.core.service import Service, Signal

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
    def image_selected(self, image_name: str) -> None:
        pass

    # def select_image(self, image_name: str):
    #     if self._selected_image != image_name:
    #         self._selected_image = image_name
    #         self.image_selected.emit(image_name)

    # def get_selected_image(self):
    #     return self._selected_image