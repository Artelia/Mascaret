# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Mascaret
Description          : Pre and Postprocessing for Mascaret for QGIS
Date                 : June,2017
copyright            : (C) 2017 by Artelia
email                :
***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from pathlib import Path

from qgis.PyQt.QtCore import QDir, QModelIndex, QSortFilterProxyModel, qVersion
from qgis.PyQt.QtGui import QTextCursor
from qgis.PyQt.QtWidgets import QDialog
try:
    from qgis.PyQt.QtWidgets import QFileSystemModel
except ImportError:
    from qgis.PyQt.QtGui import QFileSystemModel

from qgis.PyQt.uic import loadUi
from qgis.core import QgsApplication
from qgis.utils import QDesktopServices, QUrl

QT_VERSION = [int(v) for v in qVersion().split('.')][0]

class LisFilterProxy(QSortFilterProxyModel):
    """Filter proxy model for .lis and .assim_lis files in QFileSystemModel."""

    def filterAcceptsRow(self, row: int, parent: QModelIndex) -> bool:
        """Filter to show directories and .lis/.assim_lis files only.

        :param row: Row index in source model.
        :param parent: Parent model index.
        :return: ``True`` if row should be shown, ``False`` otherwise.
        """
        model: QFileSystemModel = self.sourceModel()
        idx = model.index(row, 0, parent)
        return (
            model.isDir(idx)
            or model.fileName(idx).endswith(".lis")
            or model.fileName(idx).endswith(".assim_lis")
        )


UI_FILE = os.path.join(os.path.dirname(__file__), "..", "ui", "ui_lis_viewer.ui")


class ClassLisDialog(QDialog):
    """Dialog widget for browsing and viewing .lis output files."""

    def __init__(self, root_path):
        """Initialize LIS file viewer dialog.

        :param root_path: Root directory path for file browser.
        :return: None
        """
        super().__init__()
        self.ui = loadUi(UI_FILE, self)
        self._root_path = root_path
        self._load_root(root_path)
        self.tree_view.clicked.connect(self._on_item_clicked)
        self.bt_open_folder.clicked.connect(self._on_open_folder)
        self.bt_open_folder.setIcon(QgsApplication.getThemeIcon("/mActionFileOpen.svg"))

    def _load_root(self, path):
        """Initialize file system model and set up tree view.

        :param path: Root directory path to display.
        :return: None
        """
        self.fs_model = QFileSystemModel()

        # Set options with Qt5/Qt6 compatibility
        if QT_VERSION >= 6:
            self.fs_model.setOption(QFileSystemModel.Option.DontWatchForChanges, True)
            self.fs_model.setOption(QFileSystemModel.Option.DontResolveSymlinks, True)
            self.fs_model.setFilter(
                QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
            )
        else:
            self.fs_model.setOption(QFileSystemModel.DontWatchForChanges, True)
            self.fs_model.setOption(QFileSystemModel.DontResolveSymlinks, True)
            self.fs_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        # Optimization 3: connect proxy BEFORE setRootPath
        # to avoid unnecessary recalculations during population
        self.proxy = LisFilterProxy()
        self.proxy.setSourceModel(self.fs_model)

        self.tree_view.setModel(self.proxy)
        for col in range(1, self.fs_model.columnCount()):
            self.tree_view.hideColumn(col)

        # Optimization 4: setRootPath after proxy, single triggering
        self.fs_model.setRootPath(path)

        root_idx = self.fs_model.index(path)
        proxy_root = self.proxy.mapFromSource(root_idx)
        self.tree_view.setRootIndex(proxy_root)

        # Optimization 5: replace expandAll() (very slow on large trees)
        # with lazy expansion at first level only
        self._expand_first_level(proxy_root)

    def _expand_first_level(self, proxy_root: QModelIndex):
        """Expand only first level – user opens the rest on demand.

        :param proxy_root: Root index in proxy model.
        :return: None
        """
        row_count = self.proxy.rowCount(proxy_root)
        for row in range(row_count):
            child = self.proxy.index(row, 0, proxy_root)
            self.tree_view.expand(child)

    def _on_item_clicked(self, proxy_index: QModelIndex):
        """Handle tree view item click to load .lis file.

        :param proxy_index: Clicked item index in proxy model.
        :return: None
        """
        source_index = self.proxy.mapToSource(proxy_index)
        path = self.fs_model.filePath(source_index)
        if path.endswith(".lis") or path.endswith(".assim_lis"):
            self._read_lis(path)

    def _read_lis(self, path: str):
        """Load and display .lis file content in text editor.

        :param path: Path to .lis file.
        :return: None
        """
        try:
            content = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        # Optimization 6: block signals during text update
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(content)
        cursor = self.text_edit.textCursor()
        # Qt5/Qt6 compatibility for cursor.Start
        if QT_VERSION >= 6:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
        else:
            cursor.movePosition(QTextCursor.Start)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.blockSignals(False)

        self.file_label.setText(f"  {_from_mascaret(path)}")

    def _on_open_folder(self):
        """Ouvre dans l'explorateur le dossier du fichier sélectionné,
        ou le dossier racine si rien n'est sélectionné.

        :return: None
        """
        folder = self._root_path  # fallback : racine

        indexes = self.tree_view.selectedIndexes()
        if indexes:
            source_index = self.proxy.mapToSource(indexes[0])
            path = self.fs_model.filePath(source_index)
            folder = path if self.fs_model.isDir(source_index) else str(Path(path).parent)

        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


def _from_mascaret(full_path: str, anchor: str = "mascaret") -> str:
    """Extract relative path from mascaret root directory.

    :param full_path: Full absolute path.
    :param anchor: Directory name to use as anchor (default 'mascaret').
    :return: Relative path from anchor directory or full path if anchor not found.
    """
    parts = Path(full_path.replace("\\", "/")).parts
    for i, part in enumerate(parts):
        if part.lower() == anchor.lower():
            return "/".join(parts[i:])
    return full_path
