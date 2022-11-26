from typing import List

class CrawlerStatus:
    status: str
    running: bool
    dirty: bool
    num: str

    def __init__(self, num) -> None:
        self.num = num
        self.status = "Starting"
        self.running = True

    def set_status(self, new_status):
        self.dirty = True
        self.status = new_status

    def clean_dirty(self):
        self.dirty = False

status: List[CrawlerStatus]
status = []

def display_status(screen):
    x_coord = 0
    y_coord = 0
    dirty = True

    while True:
        for s in status:
            if s.dirty:
                dirty = True
                break
        if dirty:
            screen.clear_buffer(0, 0, 0)
            for i in range(len(status)):
                screen.print_at(
                    status[i].num + status[i].status,
                    x_coord, 
                    y_coord + i,
                )
            screen.refresh()
            dirty = False
        ev = screen.get_key()
        if ev:
            dirty = True
        if ev in (ord('Q'), ord('q')):
            return
        if ev == -203:
            x_coord += 1
        if ev == -204:
            y_coord += 1
        if ev == -205:
            x_coord -= 1
        if ev == -206:
            y_coord -= 1
