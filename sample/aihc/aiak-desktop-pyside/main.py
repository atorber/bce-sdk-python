#!/usr/bin/env python3
# coding=utf-8

import sys
from PySide6.QtWidgets import QApplication
from ui.app import ParameterConfigApp
from config.parameters import input_params


def main():
    app = QApplication(sys.argv)
    window = ParameterConfigApp(input_params)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
