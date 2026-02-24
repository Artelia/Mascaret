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
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from pathlib import Path

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *


class LisFilterProxy(QSortFilterProxyModel):
    def filterAcceptsRow(self, row: int, parent: QModelIndex) -> bool:
        model: QFileSystemModel = self.sourceModel()
        idx = model.index(row, 0, parent)
        return model.isDir(idx) or model.fileName(idx).endswith(".lis")


UI_FILE = os.path.join(os.path.dirname(__file__), "..", "ui", "ui_lis_viewer.ui")


class ClassLisDialog(QDialog):
    def __init__(self, root_path):
        super().__init__()
        self.ui = loadUi(UI_FILE, self)
        self._load_root(root_path)
        self.tree_view.clicked.connect(self._on_item_clicked)

    def _load_root(self, path):
        self.fs_model = QFileSystemModel()

        # ── Optimisation 1 : aucune surveillance des changements sur le disque ──
        self.fs_model.setOption(QFileSystemModel.DontWatchForChanges, True)

        # ── Optimisation 2 : on ne résout pas les liens symboliques (plus rapide) ──
        self.fs_model.setOption(QFileSystemModel.DontResolveSymlinks, True)

        self.fs_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)

        # ── Optimisation 3 : brancher le proxy AVANT setRootPath
        #    pour éviter des recalculs inutiles au moment du peuplement ──
        self.proxy = LisFilterProxy()
        self.proxy.setSourceModel(self.fs_model)

        self.tree_view.setModel(self.proxy)
        for col in range(1, self.fs_model.columnCount()):
            self.tree_view.hideColumn(col)

        # ── Optimisation 4 : setRootPath après le proxy, déclenchement unique ──
        self.fs_model.setRootPath(path)

        root_idx = self.fs_model.index(path)
        proxy_root = self.proxy.mapFromSource(root_idx)
        self.tree_view.setRootIndex(proxy_root)

        # ── Optimisation 5 : remplacer expandAll() (très lent sur grands arbres)
        #    par une expansion lazy au premier niveau uniquement ──
        self._expand_first_level(proxy_root)

    def _expand_first_level(self, proxy_root: QModelIndex):
        """Expand seulement le premier niveau – l'utilisateur ouvre le reste à la demande."""
        row_count = self.proxy.rowCount(proxy_root)
        for row in range(row_count):
            child = self.proxy.index(row, 0, proxy_root)
            self.tree_view.expand(child)


    def _on_item_clicked(self, proxy_index: QModelIndex):
        source_index = self.proxy.mapToSource(proxy_index)
        path = self.fs_model.filePath(source_index)
        if path.endswith(".lis"):
            self._read_lis(path)

    def _read_lis(self, path: str):
        try:
            content = Path(path).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        # ── Optimisation 6 : bloquer les signaux pendant la mise à jour du texte ──
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(content)
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.Start)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.blockSignals(False)

        self.file_label.setText(f"  {_from_mascaret(path)}")


def _from_mascaret(full_path: str, anchor: str = "mascaret") -> str:
    parts = Path(full_path.replace("\\", "/")).parts
    for i, part in enumerate(parts):
        if part.lower() == anchor.lower():
            return "/".join(parts[i:])
    return full_path