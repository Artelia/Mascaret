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
import csv
import datetime
import io
import os
import traceback

import pandas as pd
import numpy as np
from matplotlib.dates import date2num
from qgis.PyQt.QtCore import Qt, QDateTime, QVariant, qVersion
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem, QKeySequence, QColor, QPalette
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QLineEdit,
    QLabel,
    QDialogButtonBox,
    QShortcut,
    QAbstractItemView,
    QItemEditorFactory,
    QFormLayout,
    QDoubleSpinBox,
    QStyledItemDelegate,
    QStyle,
)

from qgis.PyQt.uic import loadUi
from .Graphic.GraphCommon import GraphCommon
from ..ui.custom_control import ClassWarningBox

QT_VERSION = [int(v) for v in qVersion().split(".")][0]


class ClassEventObsDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.filling_tab = False

        self.cur_station = ""

        self.cur_var = ""
        self.box = ClassWarningBox()

        self.graph_home = None
        self.graph_edit = None
        self.axes = None
        self.courbe = None

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_event_obs.ui"), self)

        self.ui.tab_values.sCut_del = QShortcut(QKeySequence("Del"), self)
        self.ui.tab_values.sCut_del.activated.connect(self.short_cut_row_del)

        styled_item_delegate = QStyledItemDelegate()
        styled_item_delegate.setItemEditorFactory(ItemEditorFactory())
        self.ui.tab_values.setItemDelegate(styled_item_delegate)

        self.ui.actionB_edit.triggered.connect(self.edit_station)
        self.ui.actionB_new.triggered.connect(self.new_station)
        self.ui.actionB_deleteV.triggered.connect(self.delete_var_station)
        self.ui.actionB_delete.triggered.connect(self.delete_station)
        self.ui.actionB_import.triggered.connect(self.import_csv)
        self.ui.actionB_addLine.triggered.connect(self.new_time)
        self.ui.actionB_delLine.triggered.connect(self.delete_time)
        self.ui.b_OK_page2.accepted.connect(self.accept_page2)
        self.ui.b_OK_page2.rejected.connect(self.reject_page2)
        self.ui.b_OK_page1.accepted.connect(self.reject)
        self.ui.cb_var.currentIndexChanged.connect(self.var_changed)
        if QT_VERSION > 5:
            self.ui.tab_stations.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        else:
            self.ui.tab_stations.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.seld = SelectDelegate(self)
        self.ui.tab_stations.setItemDelegate(self.seld)
        self.init_ui()

    def init_ui(self):
        """initializes GUI"""
        self.ui.Obs_pages.setCurrentIndex(0)
        self.graph_home = GraphObservation(self.mgis, self.ui.lay_graph_home)
        self.graph_edit = GraphObservation(self.mgis, self.ui.lay_graph_edit)
        self.fill_lst_stations()

    def fill_lst_stations(self, id=None):
        """
        Fill stations table in function of
        :param id: id of station
        :return:
        """
        model = QStandardItemModel()
        model.setColumnCount(3)
        model.setHorizontalHeaderLabels(["Station", "H", "Q"])
        self.ui.tab_stations.setModel(model)
        self.ui.tab_stations.setColumnWidth(0, 140)
        self.ui.tab_stations.setColumnWidth(1, 10)
        self.ui.tab_stations.setColumnWidth(2, 10)
        self.ui.tab_stations.selectionModel().selectionChanged.connect(self.station_changed)
        if QT_VERSION > 5:
            qt_alig_left = Qt.AlignmentFlag.AlignLeft
            qt_alig_vcentre = Qt.AlignmentFlag.AlignVCenter
            qt_alig_hcentre = Qt.AlignmentFlag.AlignHCenter
        else:
            qt_alig_left = Qt.AlignLeft
            qt_alig_vcentre = Qt.AlignVCenter
            qt_alig_hcentre = Qt.AlignHCenter
        sql = (
            "SELECT DISTINCT sta.code, not cnt_h isNull as h, not cnt_q isNull as q "
            "FROM ({schema}.observations as sta LEFT JOIN "
            "(SELECT code, count(*) as cnt_h FROM {schema}.observations "
            "WHERE type = 'H' GROUP BY code) as sta_h ON sta.code = sta_h.code) "
            "LEFT JOIN (SELECT code, count(*) as cnt_q FROM {schema}.observations "
            "WHERE type = 'Q' GROUP BY code) as sta_q ON sta.code = sta_q.code "
            "ORDER BY sta.code"
        )
        rows = self.mdb.run_query(sql, fetch=True, schema=True)
        if rows is None:
            rows = []
        for i, row in enumerate(rows):
            for j, field in enumerate(row):
                new_itm = QStandardItem()
                if j == 0:
                    new_itm.setTextAlignment(qt_alig_left | qt_alig_vcentre)

                    txt = str(row[j]).strip()
                else:
                    new_itm.setTextAlignment(qt_alig_hcentre | qt_alig_vcentre)
                    if row[j] is True:
                        txt = "X"
                    else:
                        txt = ""
                new_itm.setText(txt)
                new_itm.setEditable(False)
                self.ui.tab_stations.model().setItem(i, j, new_itm)

        if id:
            for r in range(self.ui.tab_stations.model().rowCount()):
                if str(self.ui.tab_stations.model().item(r, 0).text()) == str(id):
                    self.ui.tab_stations.setCurrentIndex(
                        self.ui.tab_stations.model().item(r, 0).index()
                    )
                    break
        else:
            self.station_changed()

    def station_changed(self):
        """
        graphic change  when the station change
        :return:
        """
        cur_var = self.ui.cb_var.currentText()
        if self.ui.tab_stations.selectedIndexes():
            line = self.ui.tab_stations.selectedIndexes()[0].row()
            self.cur_station = self.ui.tab_stations.model().item(line, 0).text()
            self.seld.set_selected_cell(line)
        else:
            self.cur_station = ""

        self.ui.cb_var.blockSignals(True)
        self.ui.cb_var.clear()
        if self.cur_station:
            sql = "SELECT DISTINCT type FROM {schema}.observations WHERE code = %s ORDER BY type"
            rows = self.mdb.run_query(sql, fetch=True, schema=True, params=[self.cur_station])
            for row in rows:
                self.ui.cb_var.addItem(row[0])
        self.ui.cb_var.setCurrentText(cur_var)
        self.ui.cb_var.blockSignals(False)
        self.var_changed()

    def var_changed(self):
        """graphic change  when the variable changes"""
        self.cur_var = self.ui.cb_var.currentText()
        if self.cur_var:
            self.ui.b_edit.setText("Edit {} Values".format(self.cur_var))
            self.ui.b_deleteV.setText("Delete {} Values".format(self.cur_var))
            if self.cur_station:
                self.graph_home.init_graph([self.cur_station, self.cur_var])
            else:
                self.graph_home.init_graph(None)
        else:
            self.ui.b_edit.setText("Edit Values")
            self.ui.b_deleteV.setText("Delete Values")
            self.graph_home.init_graph(None)

    def create_tab_model(self, cur_var):
        """create model table"""
        model = QStandardItemModel()
        model.insertColumns(0, 3)
        if QT_VERSION > 5:
            qt_hori = Qt.Orientation.Horizontal
            qt_disr = Qt.ItemDataRole.DisplayRole
        else:
            qt_hori = Qt.Horizontal
            qt_disr = Qt.DisplayRole
        for idcol, ncol in enumerate(["Date", cur_var, "Comment"]):
            model.setHeaderData(idcol, qt_hori, ncol, qt_disr)
        model.itemChanged.connect(self.on_tab_data_change)
        return model

    def short_cut_row_del(self):
        """
        Delete station
        :return:
        """
        self.filling_tab = True
        upd = False
        if self.ui.tab_values.hasFocus():
            model = self.ui.tab_values.model()
            selection = self.ui.tab_values.selectedIndexes()
            for idx in selection:
                if idx.column() == 1:
                    model.item(idx.row(), idx.column()).setData(None, 0)
                    upd = True
                elif idx.column() == 2:
                    model.item(idx.row(), idx.column()).setData("", 0)
        self.filling_tab = False

        if upd:
            self.update_courbe()

    def fill_tab_values(self, cur_station, cur_var):
        """
        Fill tableau
        :param cur_station: Station name
        :param cur_var: Variable name
        :return:
        """
        self.filling_tab = True
        self.ui.tab_values.setModel(self.create_tab_model(cur_var))
        self.ui.tab_values.setColumnWidth(0, 120)
        self.ui.tab_values.setColumnWidth(1, 80)
        self.ui.tab_values.setColumnWidth(2, 120)
        model = self.ui.tab_values.model()

        if self.cur_station:
            sql = (
                "SELECT UNNEST(date) as date, "
                "UNNEST(valeur) as valeur, UNNEST(comment) as comment "
                "FROM {schema}.observations "
                "WHERE code = %s AND type = %s "
                "ORDER BY date"
            )
            rows = self.mdb.run_query(sql, fetch=True, schema=True, params=[cur_station, cur_var])
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    itm = QStandardItem()
                    if c == 0:
                        itm.setData(QDateTime(val), 0)
                    else:
                        itm.setData(val, 0)
                    model.setItem(r, c, itm)

        self.txt_cur_station.setText(cur_station)
        self.txt_cur_var.setText(cur_var)

        self.filling_tab = False

    def import_csv(self):
        """import CSV file"""
        dlg = ClassObsImportDialog(self.mgis)
        if QT_VERSION > 5:
            dlg.exec()  # PyQt6
        else:
            dlg.exec_()  # PyQt5
        if dlg.result() == 0:
            return False
        typ_f = dlg.type_f
        file_name_path, _ = QFileDialog.getOpenFileNames(
            None, "File Selection", self.mgis.repProject, filter="CSV (*.csv);;File (*)"
        )
        if not file_name_path:
            return
        self.mgis.up_rep_project(file_name_path[0])

        if typ_f == "csv":
            succes, recs = self.read_csv(file_name_path)
        elif typ_f == "octave":
            succes, recs = self.read_octave(file_name_path)
        else:
            succes, recs = self.read_csv(file_name_path)

        # recs data frame
        dbls = None
        if succes:
            duplic = recs[recs.duplicated(subset=["code", "type", "date"])]
            if len(duplic):
                txt_lst = [
                    "{} - date  : {}".format(fil, dat)
                    for j, (fil, dat) in enumerate(
                        zip(duplic["fichier"].tolist(), duplic["date"].tolist())
                    )
                    if j < 5
                ]

                msg = (
                    "No recording of observations due to \n"
                    "duplicate elements (code, type, date) having different values.\n\n"
                    "Check the files (the first 5) : \n"
                    "{0}".format("\n".join(txt_lst))
                )
                QMessageBox.warning(None, "WARNING:", msg)
                return

            sql = """
                    DROP TABLE  IF EXISTS {schema}.tmp_observations;
                    CREATE TABLE IF NOT EXISTS {schema}.tmp_observations  AS 
                    SELECT DISTINCT code,type,
                    UNNEST(comment) as comment, UNNEST(valeur) as valeur ,UNNEST(date) as date  
                    FROM {schema}.observations  WITH NO DATA;
                    ALTER TABLE {schema}.tmp_observations
                    ADD CONSTRAINT constraint_obs UNIQUE (code,type,date);
                """
            self.mdb.execute(sql, schema=True)
            recs = recs.drop(columns=["fichier"])
            recs = recs[["code", "date", "type", "comment", "valeur"]]

            rows_to_insert = []
            for rec in recs.itertuples(index=False, name=None):
                clean_row = []
                for val in rec:
                    if isinstance(val, str) and len(val) >= 2 and val[0] == "'" and val[-1] == "'":
                        clean_row.append(val[1:-1])
                    else:
                        clean_row.append(val)
                rows_to_insert.append(tuple(clean_row))

            sql = (
                "INSERT INTO {schema}.tmp_observations "
                "(code, date, type, comment, valeur) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            err = self.mdb.run_query(
                sql,
                schema=True,
                many=True,
                list_many=rows_to_insert,
            )
            if err:
                msg = "Incorrect format for observations"
                QMessageBox.warning(None, "WARNING:", msg)
                return

            # check if type and code existant
            dbls = self.mdb.run_query(
                "SELECT DISTINCT code, type FROM {schema}.observations As obs WHERE EXISTS "
                "(SELECT 1 FROM {schema}.tmp_observations AS tmp WHERE obs.code = tmp.code "
                " AND obs.type = tmp.type)",
                fetch=True,
                schema=True,
            )
        else:
            return
        # si couple date,typ existe
        if dbls:
            txt_sta = ""
            for d, dbl in enumerate(dbls):
                if d < 5:
                    txt_sta += "- " + dbl[0].strip() + " : " + dbl[1] + "\n"
                else:
                    txt_sta += "- and more ...\n"
                    break

            txt_mess = (
                "Duplicates exist for these configurations (the first 5) : \n" + txt_sta + "\n"
            )
            dlg = ClassObsDuplicDialog(self.mgis, txt_mess)
            if QT_VERSION > 5:
                dlg.exec()  # PyQt6
            else:
                dlg.exec_()  # PyQt5
            if dlg.result() == 0:
                return False
            typ_s = dlg.type_save

            sql_tab = """
                    DROP TABLE  IF EXISTS {schema}.obs_ref;
                    CREATE TABLE {schema}.obs_ref AS  SELECT  code,type,UNNEST(comment) as comment, 
                        UNNEST(valeur) as valeur ,UNNEST(date) as date  
                        FROM {schema}.observations WHERE (code,type) 
                        in (SELECT code,type FROM {schema}.tmp_observations) 
                        order by code, date;
                """
            sql_over = """
                    INSERT INTO {schema}.tmp_observations (code, type, comment, valeur, date)
                        SELECT ref.code, ref.type, ref.comment, ref.valeur, ref.date
                        FROM {schema}.obs_ref ref
                        ON CONFLICT (code, type, date) DO NOTHING;
                """
            sql_no = """
                     INSERT INTO {schema}.tmp_observations (code, type, comment, valeur, date)
                        SELECT ref.code, ref.type, ref.comment, ref.valeur, ref.date
                        FROM {schema}.obs_ref ref ON CONFLICT (code, type, date) 
                        DO UPDATE SET (comment,valeur) = (EXCLUDED.comment, EXCLUDED.valeur);
                """
            sqldp = """
                        DELETE FROM {schema}.obs_ref WHERE
                            (code,type,date) in (
                                SELECT ref.code,ref.type, ref.date 
                                FROM {schema}.obs_ref ref, 
                                (SELECT code, type, MIN(date) as mindate, 
                                MAX(date) as maxdate FROM {schema}.tmp_observations 
                                GROUP BY code,type) tmp
                                WHERE ref.code = tmp.code  and ref.type =tmp.type 
                                and ref.date >= tmp.mindate AND date <= tmp.maxdate);
                        """
            self.mdb.run_query(sql_tab, schema=True)
            if typ_s == "no_overw":
                self.mdb.run_query(sql_no, schema=True)
            elif typ_s == "overw":
                self.mdb.run_query(sql_over, schema=True)
            elif typ_s == "plage_overw":
                self.mdb.run_query(sqldp, schema=True)
                self.mdb.run_query(sql_over, schema=True)
            elif typ_s == "replace":
                pass
            else:
                return
            # integration table observation
            self.mdb.run_query(
                "DELETE FROM {schema}.observations WHERE (code, type) IN "
                "(SELECT DISTINCT code,type FROM {schema}.tmp_observations);"
                "",
                schema=True,
            )
            self.mdb.execute("DROP TABLE IF EXISTS {schema}.obs_ref;", schema=True)
        sql_insert = """INSERT INTO {schema}.observations(code, type, comment, valeur, date) 
                             SELECT code,type,  
                             array_agg(comment ORDER BY date), 
                             array_agg(valeur ORDER BY date), 
                             array_agg(date ORDER BY date) 
                             FROM {schema}.tmp_observations GROUP BY code,type;
                       """

        self.mdb.run_query(sql_insert, schema=True)

        # nettoyage table tempo
        self.mdb.execute("DROP TABLE IF EXISTS {schema}.tmp_observations;", schema=True)

        self.fill_lst_stations(self.cur_station)

    def safe_float(self, val, default=-99.99):
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def read_csv(self, data_file):
        """
        Read the default CSV  format
        :param data_file: list file to read
        :return: pd.DataFrame
        """
        try:
            recs = []
            for file in data_file:
                if not os.path.isfile(file):
                    continue
                with open(file, "r") as fichier:
                    codes = fichier.readline().strip().split(";")[1:]
                    types = fichier.readline().strip().split(";")[1:]
                    nom_stat = fichier.readline().strip().split(";")[1:]
                    for ligne in fichier:
                        temp = ligne.strip().split(";")
                        for i, val in enumerate(temp[1:]):
                            if val == "":
                                continue
                            if self.safe_float(val) == -99.99:
                                continue
                            rec = list()
                            rec.append(self.fmt_col(codes[i]))
                            date = self.fmt_date(temp[0])
                            if date:
                                rec.append(self.fmt_col(date))
                            else:
                                msg = f"Error in date format for file : '{file}')"
                                QMessageBox.warning(None, "WARNING:", msg)
                                return False, None
                            rec.append(self.fmt_col(types[i]))
                            rec.append(self.fmt_col(nom_stat[i]))
                            rec.append(val)
                            rec.append(os.path.basename(file))
                            recs.append(rec)
            tmp = pd.DataFrame(
                recs, columns=["code", "date", "type", "comment", "valeur", "fichier"]
            )
            recs = tmp.drop_duplicates()
            recs = recs.dropna()

            return True, recs
        except Exception as e:
            self.mgis.add_info("Loading to observations is an echec.")
            error_info = repr(e)
            if self.mgis.DEBUG:
                error_info = error_info + "\n" + traceback.format_exc()
            self.mgis.add_info(error_info)

            return False, None

    def read_octave(self, data_file):
        """
        Read  the OCTAVE format
        :param data_file: list file to read
        :return: pd.DataFrame
        """
        try:
            tmp = pd.DataFrame()
            lst_cols = ["date", "valeur", "type", "code"]
            converters = {col: self.fmt_col for col in lst_cols if col != "valeur"}

            for file in data_file:
                if os.path.isfile(file):
                    df_tmp = pd.read_csv(
                        file, sep=";", names=lst_cols, na_values=-99.99, converters=converters
                    )

                    df_tmp["comment"] = [
                        self.fmt_col(os.path.splitext(os.path.basename(file))[0])
                    ] * df_tmp.count()[0]
                    df_tmp["fichier"] = [os.path.basename(file)] * df_tmp.count()[0]

                    tmp = pd.concat([tmp, df_tmp])
            # supprime les lignes en double
            recs = tmp.drop_duplicates()
            recs = recs.dropna()
            return True, recs
        except Exception as e:
            self.mgis.add_info("Loading to observations is an echec.")
            error_info = repr(e)
            if self.mgis.DEBUG:
                error_info = error_info + "\n" + traceback.format_exc()
            self.mgis.add_info(error_info)
            return False, None

    @staticmethod
    def fmt_date(date):
        ldate = len(date.strip())
        val = None
        if ldate == 16:
            val = datetime.datetime.strptime(date, "%d/%m/%Y %H:%M")
        elif ldate == 19:
            val = datetime.datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
        return val

    @staticmethod
    def fmt_col(col):
        return "'{}'".format(col)

    def on_tab_data_change(self, itm):
        if not self.filling_tab:
            if itm.column() == 0:
                model = itm.model()
                model.sort(0)
                self.ui.tab_values.scrollTo(itm.index(), 0)
                self.update_courbe()
            elif itm.column() == 1:
                self.update_courbe()

    def update_courbe(self):
        data = {}
        lx, ly = [], []
        for r in range(self.ui.tab_values.model().rowCount()):
            lx.append(date2num(self.ui.tab_values.model().item(r, 0).data(0).toPyDateTime()))
            ly.append(self.ui.tab_values.model().item(r, 1).data(0))
        data[0] = {"x": lx, "y": ly}
        self.graph_edit.maj_courbes(data)

    def new_station(self):
        dlg = NewStationDialog()
        if dlg.exec():
            new_station = dlg.txt_station.text()
            new_var = dlg.cb_var.currentText()
            if new_station:
                rows = self.mdb.run_query(
                    "SELECT COUNT(*) FROM {schema}.observations WHERE code = %s AND type = %s",
                    fetch=True,
                    schema=True,
                    params=[new_station, new_var],
                )
                if rows[0][0]:
                    if QT_VERSION > 5:
                        ok_button = QMessageBox.StandardButton.Ok
                    else:
                        ok_button = QMessageBox.Ok
                    QMessageBox.critical(
                        self,
                        "Error",
                        "{} data set already exists for the {} station".format(
                            new_var, new_station
                        ),
                        ok_button,
                    )
                else:
                    self.tab_stations.clearSelection()
                    self.fill_tab_values(new_station, new_var)
                    self.ui.Obs_pages.setCurrentIndex(1)
                    self.graph_edit.init_graph([new_station, new_var])

    def edit_station(self):
        # charger les informations
        # changer de page
        if self.cur_station:
            self.fill_tab_values(self.cur_station, self.cur_var)
            self.ui.Obs_pages.setCurrentIndex(1)
            self.graph_edit.init_graph([self.cur_station, self.cur_var])

    def delete_station(self):
        # charger les informations
        # changer de page
        tab = self.ui.tab_stations
        indexes = tab.selectionModel().selectedRows()
        rows = [index.row() for index in indexes]
        if len(rows) > 0:
            sup_ind = 0
            for row in rows:
                station = tab.model().data(tab.model().index(row - sup_ind, 0))

                if self.box.ok_cancel_q(
                    self,
                    "Delete {} observations ?".format(str(station).strip()),
                    "Observations of Events",
                ):
                    self.mgis.add_info(
                        "Deletion of {} Observations of Events".format(station), dbg=True
                    )
                    self.mdb.run_query(
                        "DELETE FROM {schema}.observations WHERE code = %s",
                        schema=True,
                        params=[station],
                    )
                    self.fill_lst_stations()
                    sup_ind += 1

    def delete_var_station(self):
        # charger les informations
        # changer de page
        if self.cur_station:
            if self.box.ok_cancel_q(
                self,
                "Delete {0} values for {1} station ?".format(
                    self.cur_var, self.cur_station.strip()
                ),
                "Observations of Events",
            ):
                self.mgis.add_info(
                    "Deletion of {} Observations of Events".format(self.cur_station), dbg=True
                )
                self.mdb.run_query(
                    "DELETE FROM {schema}.observations WHERE code = %s AND type = %s",
                    schema=True,
                    params=[self.cur_station, self.cur_var],
                )
                self.fill_lst_stations(self.cur_station)

    def new_time(self):
        """add line"""
        self.filling_tab = True
        model = self.ui.tab_values.model()
        r = model.rowCount()
        model.insertRow(r)
        itm_date, itm_val, itm_com = QStandardItem(), QStandardItem(), QStandardItem()
        if r == 0:
            v_date = QDateTime().currentDateTime()
        elif r == 1:
            v_date = model.item(r - 1, 0).data(0).addDays(1)
        else:
            d = (
                model.item(r - 2, 0)
                .data(0)
                .addDays(1)
                .secsTo(model.item(r - 1, 0).data(0).addDays(1))
            )
            v_date = model.item(r - 1, 0).data(0).addSecs(d)

        itm_date.setData(v_date, 0)
        itm_val.setData(None, 0)
        itm_com.setData("", 0)

        model.setItem(r, 0, itm_date)
        model.setItem(r, 1, itm_val)
        model.setItem(r, 2, itm_com)

        self.ui.tab_values.scrollToBottom()
        self.filling_tab = False
        self.update_courbe()

    def delete_time(self):
        """delete line"""
        if self.ui.tab_values.selectedIndexes():
            rows = [idx.row() for idx in self.ui.tab_values.selectedIndexes()]
            rows = list(set(rows))
            rows.sort(reverse=True)
            for row in rows:
                model = self.ui.tab_values.model()
                model.removeRow(row)
            self.update_courbe()

    def accept_page2(self):
        # save Info
        # modificaito liste page 1
        # change de page
        if self.ui.tab_values.model().rowCount() > 0:
            name_stat = str(self.ui.txt_cur_station.text())
            name_var = str(self.ui.txt_cur_var.text())
            if self.cur_station == "":
                self.mgis.add_info(
                    "Addition of {0} Observations for {1}".format(name_var, name_stat), dbg=True
                )
            else:
                self.mgis.add_info(
                    "Editing of {0} Observations for {1}".format(name_var, name_stat), dbg=True
                )
                self.mdb.run_query(
                    "DELETE FROM {schema}.observations WHERE code = %s AND type = %s",
                    schema=True,
                    params=[name_stat, name_var],
                )
            d_rec = {}
            for r in range(self.ui.tab_values.model().rowCount()):
                if (name_stat, name_var) not in d_rec.keys():
                    d_rec[(name_stat, name_var)] = {"date": [], "val": [], "com": []}
                d_rec[(name_stat, name_var)]["date"].append(
                    self.ui.tab_values.model().item(r, 0).data(0).toPyDateTime()
                )
                d_rec[(name_stat, name_var)]["val"].append(
                    self.ui.tab_values.model().item(r, 1).data(0)
                )
                com = self.ui.tab_values.model().item(r, 2).data(0)
                if com == "":
                    com = "''"
                d_rec[(name_stat, name_var)]["com"].append(com)
            recs = []
            for (name_stat, name_var), var in d_rec.items():
                recs.append(
                    [
                        name_stat,
                        name_var,
                        "{" + ",".join(str(i) for i in var["date"]) + "}",
                        "{" + ",".join(str(i) for i in var["val"]) + "}",
                        "{" + ",".join(str(i) for i in var["com"]) + "}",
                    ]
                )
            self.mdb.run_query(
                "INSERT INTO {schema}.observations (code, type, date, valeur, comment) "
                "VALUES (%s, %s, %s, %s, %s)",
                schema=True,
                many=True,
                list_many=recs,
            )

            self.fill_lst_stations(name_stat)
            self.cb_var.setCurrentText(name_var)
            self.ui.Obs_pages.setCurrentIndex(0)
            self.graph_edit.init_graph(None)
        else:
            self.reject_page2()

    def reject_page2(self):
        """
        cancel button
        :return:
        """

        self.mgis.add_info("Cancel of Observations of Events", dbg=True)
        self.ui.Obs_pages.setCurrentIndex(0)
        self.graph_edit.init_graph(None)

    def copier(self):
        """copier la zone sélectionnée dans le clipboard"""
        selection = self.ui.tab_values.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[""] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                try:
                    data = index.data().toString("dd/MM/yyyy HH:mm")
                except AttributeError:
                    data = index.data()
                table[row][column] = data

            stream = io.StringIO()
            csv.writer(stream).writerows(table)
            QApplication.instance().clipboard().setText(stream.getvalue())

    def keyPressEvent(self, event):
        if self.ui.tab_values.hasFocus():
            # ----------------------------------------------------------------
            # Ctle-C: copier
            if QT_VERSION > 5:
                qt_key = Qt.Key
                qt_ctr_modif = Qt.KeyboardModifier.ControlModifier
            else:
                qt_key = Qt
                qt_ctr_modif = Qt.ControlModifier
            if event.key() == qt_key.Key_C and (event.modifiers() & qt_ctr_modif):
                self.copier()
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()


class SelectDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)
        self.row = None

    def paint(self, painter, option, index):
        # check if selected
        if QT_VERSION > 5:
            q_styl = QStyle.StateFlag
            active = QPalette.ColorGroup.Active
            q_pcolor = QPalette.ColorRole
            q_color = Qt.GlobalColor

        else:
            q_styl = QStyle
            active = QPalette.Active
            q_pcolor = QPalette
            q_color = Qt
        selected = option.state & q_styl.State_Selected
        if bool(selected) and index.row() == self.row:
            background_color = QColor(q_color.green)
            text_color = QColor(q_color.black)
            option.palette.setColor(q_pcolor.Highlight, background_color)
            option.palette.setColor(q_pcolor.HighlightedText, text_color)
        else:
            # Reset the background color for non-selected cells
            option.palette.setColor(
                q_pcolor.Highlight, option.palette.color(active, q_pcolor.Highlight)
            )

        super().paint(painter, option, index)

    def set_selected_cell(self, row):
        self.row = row


class ItemEditorFactory(QItemEditorFactory):
    def __init__(self):
        QItemEditorFactory.__init__(self)

    def createEditor(self, user_type, parent):
        if user_type == QVariant.Double or user_type == 0:
            double_spin_box = QDoubleSpinBox(parent)
            double_spin_box.setDecimals(4)
            double_spin_box.setMinimum(-99999.99)  # The default maximum value is 99.99.
            double_spin_box.setMaximum(99999.99)  # The default maximum value is 99.99.
            return double_spin_box
        else:
            return QItemEditorFactory().createEditor(user_type, parent)


class NewStationDialog(QDialog):
    """window for New station button"""

    def __init__(self, flds=None, parent=None):
        super(NewStationDialog, self).__init__(parent)

        layout = QFormLayout()

        self.txt_station = QLineEdit()

        self.cb_var = QComboBox()
        self.cb_var.addItem("H")
        self.cb_var.addItem("Q")
        if QT_VERSION > 5:
            self.btn_box = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                parent=self,
            )
        else:
            self.btn_box = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
            )

        self.btn_box.accepted.connect(self.accept)
        self.btn_box.rejected.connect(self.reject)

        layout.addRow(QLabel("Code"), self.txt_station)
        layout.addRow(QLabel("Type"), self.cb_var)
        layout.addRow(self.btn_box)

        self.setLayout(layout)


class GraphObservation(GraphCommon):
    """class Dialog GraphWaterQ"""

    def __init__(self, mgis=None, lay=None):
        GraphCommon.__init__(self, mgis)
        self.mdb = self.mgis.mdb
        self.init_ui_common_p()
        self.gui_graph(lay)
        self.init_ui()

    def init_ui(self):
        """initializes  GUI"""
        self.axes = self.fig.add_subplot(111)
        self.axes.tick_params(axis="both", labelsize=7.0)
        self.axes.grid(True)

        (self.courbe,) = self.axes.plot([], [], zorder=99, label="None", rasterized=True)
        self.courbes.append(self.courbe)

        self.fig.canvas.mpl_connect("pick_event", self.onpick)
        self.init_legende()

    def get_max_plot_points(self, default_points=2000):
        """Adapte le nombre max de points à la largeur utile (en pixels)."""
        try:
            width_px = self.canvas.width()
            if width_px <= 0:
                width_px = int(self.fig.get_figwidth() * self.fig.dpi)
        except Exception:
            width_px = 0

        if width_px <= 0:
            return default_points

        return max(400, min(default_points, int(width_px)))

    def resample_data(self, data_x, data_y, max_points=None):
        """
        Resamples the data to improve rendering performance.
        Limits the number of displayed points while preserving overall trends.

        :param data_x: List/array of x-coordinates
        :param data_y: List/array of y-coordinates
        :param max_points: Maximum number of points (default: canvas width)
        :return: Tuple (resampled_data_x, resampled_data_y)
        """
        if max_points is None:
            max_points = self.get_max_plot_points()

        if len(data_x) <= max_points or max_points <= 0:
            return data_x, data_y

        step = max(1, int(np.ceil(float(len(data_x)) / float(max_points))))
        resampled_x = list(data_x[::step])
        resampled_y = list(data_y[::step])

        if resampled_x and resampled_x[-1] != data_x[-1]:
            resampled_x.append(data_x[-1])
            resampled_y.append(data_y[-1])

        return resampled_x, resampled_y

    def init_graph(self, config):
        """initializes  Graphic"""
        self.maj_unit_x("date")
        leglines = self.leg.get_lines()

        lst = [[], []]
        if config is not None:
            self.leg.get_texts()[0].set_text(config[1])
            sql = (
                "SELECT UNNEST(date), UNNEST(valeur) FROM {schema}.observations "
                "WHERE code = %s and type = %s "
                "ORDER BY date"
            )
            rows = self.mdb.run_query(sql, fetch=True, schema=True, params=[config[0], config[1]])
            if len(rows) > 0:
                lst = list(zip(*rows))
                data_x, data_y = self.resample_data(lst[0], lst[1])
                lst = [data_x, data_y]
        else:
            self.leg.get_texts()[0].set_text("None")

        self.courbes[0].set_data([date2num(lval) for lval in lst[0]], lst[1])
        self.courbes[0].set_visible(True)
        leglines[0].set_alpha(1.0)

        self.maj_limites()


class ClassObsImportDialog(QDialog):
    def __init__(self, mgis):
        QDialog.__init__(self)
        self.mgis = mgis
        self.type_f = "csv"

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_obs_import.ui"), self)
        dict_f = {
            "csv": "Default Format",
            "octave": "OCTAVE Format",
        }
        for key, itm in dict_f.items():
            self.cb_typ_file.addItem(itm, key)
        self.bt_ok.accepted.connect(self.accept_page)
        self.bt_ok.rejected.connect(self.reject_page)

    def accept_page(self):
        # save Info
        self.type_f = self.cb_typ_file.itemData(self.cb_typ_file.currentIndex())
        self.accept()

    def reject_page(self):
        # print('cancel')
        self.reject()


class ClassObsDuplicDialog(QDialog):
    def __init__(self, mgis, message):
        QDialog.__init__(self)
        self.mgis = mgis

        self.ui = loadUi(os.path.join(self.mgis.masplugPath, "ui/ui_obs_duplic.ui"), self)
        self.lst_ctr = [
            (self.rb_no_overw, "no_overw"),
            (self.rb_overw, "overw"),
            (self.rb_overw_plage, "plage_overw"),
            (self.rb_replace, "replace"),
        ]
        # default
        self.rb_no_overw.setChecked(True)
        self.type_save = "no_overw"
        for ctrl_, typ in self.lst_ctr:
            ctrl_.clicked.connect(self.check)
        self.lbl_message.setText(message)
        self.bt_ok.accepted.connect(self.accept_page)
        self.bt_ok.rejected.connect(self.reject_page)

    def check(self):
        sender_button = self.sender()

        for ctrl_, typ in self.lst_ctr:
            if ctrl_ == sender_button:
                self.type_save = typ
                ctrl_.setChecked(True)
            else:
                ctrl_.setChecked(False)

    def accept_page(self):
        self.accept()

    def reject_page(self):
        # print('cancel')
        self.type_save = None
        self.reject()
