import sys
import random
from functools import partial
from typing import Any, Callable, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    _RECENT_GENERATIONS = 2
    _CACHE_LIMIT_BY_LAB = {1: 2, 2: 2, 3: 3}

    _TITLE_STYLE = (
        "margin: 0 0 10px 0; "
        "font-size: 18px; "
        "font-weight: bold; "
        "color: #b4b4b4;"
    )
    _ITEM_STYLE = "margin: 4px 0;"
    _FOOTER_STYLE = (
        "margin-top: 20px; "
        "padding-top: 15px; "
        "border-top: 2px solid #3a3a3a; "
        "font-weight: bold;"
    )

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Lab Variant Picker")
        self.setGeometry(100, 100, 800, 600)

        self.cache: dict[int, list[list[int]]] = {lab: [] for lab in range(1, 8)}

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panel = QWidget()
        left_panel.setFixedWidth(250)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        self.buttons: list[QPushButton] = []
        for lab in range(1, 8):
            btn = QPushButton(f"Pick variant for lab {lab}")
            clicked = cast(Any, btn.clicked)
            clicked.connect(partial(self.pick_variant, lab))
            left_layout.addWidget(btn)
            self.buttons.append(btn)

        left_layout.addStretch()

        self.results_panel = QLabel("Click a lab button to generate variants")
        self.results_panel.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )
        self.results_panel.setWordWrap(True)
        self.results_panel.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.results_panel.setObjectName("results")

        scroll = QScrollArea()
        scroll.setWidget(self.results_panel)
        scroll.setWidgetResizable(True)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(scroll, 1)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                font-family: -apple-system, BlinkMacSystemFont,
                             "Segoe UI", Roboto, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                border-radius: 8px;
                padding: 15px;
                text-align: left;
                color: #d4d4d4;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
            QLabel#results {
                background-color: #252525;
                border-radius: 12px;
                padding: 25px;
                color: #d4d4d4;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            """
        )

    def pick_variant(self, lab_num: int, _checked: bool = False) -> None:
        if lab_num == 1:
            html = self._generate_lab(
                lab_num=1,
                ranges=[(1, 33, 1),
                        (34, 48, 1),
                        (49, 84, 1)],
                label_for_index=lambda _: "Question",
            )
        elif lab_num == 2:
            html = self._generate_lab(
                lab_num=2,
                ranges=[(1, 26, 1),
                        (27, 45, 1),
                        (46, 67, 2),
                        (68, 88, 1),
                        (89, 106, 2)
                        ],
                label_for_index=lambda _: "Question",
            )
        elif lab_num == 3:
            html = self._generate_lab(
                lab_num=3,
                ranges=[
                    (1, 24, 1),
                    (25, 55, 2),
                    (56, 82, 2),
                    (83, 100, 2),
                    (101, 141, 2),
                    (142, 179, 2),
                    (180, 200, 2),
                ],
                label_for_index=lambda idx: "Task" if idx >= 5 else "Question",
            )
        else:
            html = self.generate_not_done(lab_num)

        self.results_panel.setText(html)

    def get_recent_numbers(self, lab_num: int) -> set[int]:
        recent: set[int] = set()
        for generation in self.cache[lab_num][-self._RECENT_GENERATIONS:]:
            recent.update(generation)
        return recent

    @staticmethod
    def generate_unique_number(start: int, end: int, used_numbers: set[int]) -> int:
        pool = [n for n in range(start, end + 1) if n not in used_numbers]
        if pool:
            return random.choice(pool)
        return random.randint(start, end)

    def _update_cache(self, lab_num: int, generation: list[int]) -> None:
        self.cache[lab_num].append(generation)
        limit = self._CACHE_LIMIT_BY_LAB.get(lab_num, self._RECENT_GENERATIONS)
        while len(self.cache[lab_num]) > limit:
            self.cache[lab_num].pop(0)

    def _generate_lab(
        self,
        lab_num: int,
        ranges: list[tuple[int, int, int]],
        label_for_index: Callable[[int], str],
    ) -> str:
        used_numbers = self.get_recent_numbers(lab_num)
        current_generation: list[int] = []

        parts: list[str] = ["<div style='line-height: 1.6;'>", f"<div style='{self._TITLE_STYLE}'>"
                                                               f"Lab {lab_num}"
                                                               "</div>"]

        total_points = 0
        for idx, (start, end, points) in enumerate(ranges, 1):
            local_used = used_numbers | set(current_generation)
            num = self.generate_unique_number(start, end, local_used)

            current_generation.append(num)
            total_points += points

            point_word = "Point" if points == 1 else "Points"
            label = label_for_index(idx)

            parts.append(
                f"<div style='{self._ITEM_STYLE}'>"
                f"{idx}. {label} {num} ({points} {point_word})"
                "</div>"
            )

        self._update_cache(lab_num, current_generation)

        parts.append(
            f"<div style='{self._FOOTER_STYLE}'>"
            f"Maximum score for theory part: {total_points}"
            "</div>"
        )
        parts.append("</div>")

        return "".join(parts)

    @staticmethod
    def generate_not_done(lab_num: int) -> str:
        title = (
            "<div style='margin: 0 0 10px 0; "
            "font-size: 18px; "
            "font-weight: bold; "
            "color: #b4b4b4;'>"
        )
        parts = [
            "<div style='line-height: 1.6;'>",
            f"{title}Lab {lab_num}</div>",
            "<div style='color: #888;'>",
            "Haven't done yet",
            "</div>",
            "</div>",
        ]
        return "".join(parts)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
