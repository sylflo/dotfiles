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
