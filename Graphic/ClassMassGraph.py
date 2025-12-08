import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.uic import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

from ..ui.custom_control import ClassWarningBox


class MassGraph:
    def __init__(self, mgis=None):
        self.mgis = mgis
        self.mdb = self.mgis.mdb
        self.box = ClassWarningBox()
        self.typ_seuil = ['Hyellow', 'Horange', 'Hred',
                          'Qyellow', 'Qorange', 'Qred']

    def check_col_outputs(self):
        """
        Checks if the columns used for massive graph plotting exist
        """
        cols = self.mdb.list_columns('outputs')
        # 'ordre': ['low', 'high'],
        dict_check = {
            'Hyellow': {'bool': False,
                        'val': [],
                        'ref': [['jaune_bas', 'jaune_haut'], ['yellow_low', 'yellow_high'],
                                ["hyb", "hyh"], ["hyl", "hyh"]],
                        'numref': None,
                        "color": 'yellow'
                        },
            'Horange': {'bool': False, 'val': [],
                        'ref': [['orange_bas', 'orange_haut'], ['orange_low', 'orange_high'],
                                ["hob", "hoh"], ["hol", "hoh"]],
                        'numref': None,
                        "color": 'orange'
                        },
            'Hred': {'bool': False, 'val': [],
                     'ref': [['rouge_bas', 'rouge_haut'], ['red_low', 'red_high'],
                             ["hrb", "hrh"], ["hrl", "hrh"]],
                     'numref': None,
                     "color": "red"
                     },

            'Qyellow': {'bool': False,
                        'val': [],
                        'ref': [['qjaune_bas', 'qjaune_haut'], ['qyellow_low', 'qyellow_high'],
                                ["qyb", "qyh"], ["qyl", "qyh"]],
                        'numref': None,
                        "color": 'yellow'
                        },
            'Qorange': {'bool': False, 'val': [],
                        'ref': [['qorange_bas', 'qorange_haut'], ['qorange_low', 'qorange_high'],
                                ["qob", "qoh"], ["qol", "qoh"]],
                        'numref': None,
                        "color": 'orange'
                        },
            'Qred': {'bool': False, 'val': [],
                     'ref': [['qrouge_bas', 'qrouge_haut'], ['qred_low', 'qred_high'],
                             ["qrb", "qrh"], ["qrl", "qrh"]],
                     'numref': None,
                     "color": "red"
                     },
        }

        if_true = False
        lstyp = []
        for seuil in self.typ_seuil:
            res = [set(sub).issubset(cols) for sub in dict_check[seuil]['ref']]
            dict_check[seuil]['bool'] = any(res)
            if dict_check[seuil]['bool']:
                if_true = True
                idx_r = res.index(True)
                dict_check[seuil]['numref'] = idx_r
                if seuil[0] not in lstyp:
                    lstyp.append(seuil[0])

        return dict_check, if_true, lstyp

    def export_result_vs_obs(self, id_out):
        """
        Export graphs with observation comparison
        Works only for event-based runs
        :param id_out:(int) index of the géométrie
        """
        output_info = self.mdb.select('outputs', where=f"gid={id_out}", list_var=['name', 'code', 'zero', 'abscissa'])
        if not output_info:
            return

        runs = []
        sql = """SELECT run 
                FROM {0}.runs
                WHERE id IN (SELECT DISTINCT ON(run) id
                             FROM {0}.runs
                             WHERE scenario not like '%_init')
                ORDER BY date"""
        rows = self.mdb.run_query(sql.format(self.mdb.SCHEMA), fetch=True)
        for row in rows:
            runs.append(row[0])

        run, ok = QInputDialog.getItem(None,
                                       'Runs',
                                       'Choix du run',
                                       runs, 0, False)
        if not ok or run.strip() == '':
            return

        sql = """SELECT e.name, e.starttime, e.endtime
                        FROM {0}.runs r, {0}.events e
                        WHERE r.scenario NOT LIKE '%init%'
                        AND r.run = '{1}'
                        AND e.name = r.scenario
                        ORDER BY e.starttime"""
        par_event = self.mdb.run_query(sql.format(self.mdb.SCHEMA, run), fetch=True)
        if_event = True
        if not par_event:
            if_event = False
            sql = """SELECT scenario
                       FROM {0}.runs 
                       WHERE scenario NOT LIKE '%init%'
                       AND run = '{1}' """
            par_event = self.mdb.run_query(sql.format(self.mdb.SCHEMA, run), fetch=True)
            par_event = [par[0] for par in par_event]

        dossier = QFileDialog.getExistingDirectory(None, u"Choosing the export folder")
        if not dossier :
            return
        # check if seuil vigilance
        dict_check, all_ch, lstyp = self.check_col_outputs()
        aff_seuil = False
        if all_ch:
            # aff_seuil = self.box.yes_no_q('Voulez-vous afficher vos seuils de vigilance ?',
            #                                   'Voulez-vous afficher vos seuils de vigilance ?')
            aff_seuil = self.box.yes_no_q('Would you like to display your warning thresholds ?',
                                          'Would you like to display your warning thresholds ?')

        if aff_seuil:
            lst_seuil = []
            if 'H' in lstyp:
                lst_seuil.append('H')
            if 'Q' in lstyp:
                lst_seuil.append('Q')
            if 'Q' in lstyp and 'H' in lstyp:
                lst_seuil.append('H and Q')
            tseuil, ok = QInputDialog.getItem(None,
                                              'Alert thresholds',
                                              "Choosing the warning thresholds you want to add :",
                                              lst_seuil, 0, False)
            if not ok:
                aff_seuil = False
            else:
                for seuil in self.typ_seuil:
                    if dict_check[seuil]['bool']:
                        let = seuil[0]
                        if 'Q' == let and 'H' == tseuil:
                            dict_check[seuil]['bool'] = False
                        if 'H' == let and 'Q' == tseuil:
                            dict_check[seuil]['bool'] = False

        if aff_seuil:
            exist_seuil = self.box.yes_no_q('Would you like to use the warning values from the "outputs" table ?',
                                            'Would you like to use the warning values from the "outputs" table ?')
            # exist_seuil = self.box.yes_no_q('Voulez-vous utiliser les valeur de vigilance de la table \"outputs\" ?',
            #                               'Voulez-vous utiliser les valeur de vigilance de la table \"outputs\" ?')

            if not exist_seuil:
                tab = {}
                for seuil in self.typ_seuil:
                    if dict_check[seuil]['bool']:
                        idr = dict_check[seuil]['numref']
                        cols = dict_check[seuil]['ref'][idr]
                        ordre = ['low', 'high']
                        lval = []
                        for idx, col in enumerate(cols):
                            wcond = True
                            val = None
                            while wcond:
                                val, ok = QInputDialog.getDouble(None, f"\"{col}\" threshold value",
                                                                 f"\"{col}\" threshold value "
                                                                 f"({ordre[idx]} "
                                                                 f"end of the transition range)",
                                                                 0.00, -10000, 10000, 2)
                                wcond = False
                                if not ok:
                                    return
                                # Ensures that the high value is greater than the low value
                                if len(lval) > 0:
                                    if lval[0] > val:
                                        msg = f"Warning : The \"{cols[0]}\" value must be less than " \
                                              f"the \"{col}\" value."
                                        self.box.info(msg, title="Warning")
                                        wcond = True
                            tab[col] = val
                            lval.append(val)
                        dict_check[seuil]['val'] = lval
                tabf = {id_out: tab}
                self.mdb.update("outputs", tabf, var="gid")
            else:
                # Get value in output table
                for seuil in self.typ_seuil:
                    if dict_check[seuil]['bool']:
                        idr = dict_check[seuil]['numref']
                        cols = dict_check[seuil]['ref'][idr]
                        val = [None, None]
                        info = self.mdb.select('outputs', where=f"gid={id_out}", list_var=cols)
                        for key, item in info.items():
                            val[cols.index(key)] = item[0]
                        dict_check[seuil]['val'] = val
                        if None in val:
                            dict_check[seuil]['bool'] = False

        if if_event:
            self.obs_graph(dossier, dict_check, run, output_info, aff_seuil, par_event)
        else:
            self.law_graph(dossier, dict_check, run, output_info, aff_seuil, par_event)

    def obs_graph(self, dossier, dict_check, run, output_info, aff_seuil, par_event):
        """
        :param dossier: (str) Folder path
        :param dict_check: (dict) thresholds infortmations
        :param run: (int) Run index
        :param output_info:(dict) outputs parameters
        :param aff_seuil:(bool) if display the thresholds
        :param par_event: (dict) scenario infortmations
        """
        tab = {}
        nom = output_info['name'][0]
        code = output_info['code'][0]
        zero = (0 if output_info['zero'][0] is None else output_info['zero'][0])
        abscisse = output_info['abscissa'][0]
        if_obs = True
        if code is None:
            if_obs = False
        if if_obs:
            path_csv = os.path.join(dossier, '{0}_{1}.csv'.format(run, code))
            path_pdf = os.path.join(dossier, '{0}_{1}.pdf'.format(run, code))
        else:
            path_csv = os.path.join(dossier, '{0}_{1}.csv'.format(run, nom))
            path_pdf = os.path.join(dossier, '{0}_{1}.pdf'.format(run, nom))

        try:
            with open(path_csv, 'w') as fich:
                with PdfPages(path_pdf) as pdf:
                    fich.write('station;type;date;obs;forcast\n')
                    for i, (scenario, debut, fin) in enumerate(par_event):
                        tab[i] = {}

                        sql1 = """SELECT v.var, r."time"*'1 second'::interval+rr.init_date, r.val
                                 FROM {0}.results r, {0}.runs rr, {0}.results_var v
                                 WHERE r.id_runs = rr.id
                                 AND rr.run = '{1}' AND rr.scenario = '{2}'
                                 AND r.pknum = {3}
                                 AND r.var = v.id AND v.var IN ('Z','Q')
                                 ORDER BY date"""

                        sql2 = """SELECT type,  date, valeur FROM (SELECT code,type, UNNEST(date) as date,
                                 UNNEST(valeur) as valeur FROM {0}.observations
                                 WHERE code = '{1}') t
                                 WHERE date>='{2}'
                                 AND date<='{3}'
                                 ORDER BY date"""

                        rows = self.mdb.run_query(sql1.format(self.mdb.SCHEMA, run, scenario, abscisse), fetch=True)
                        for grandeur, date, val in rows:
                            if date not in tab[i].keys():
                                tab[i][date] = {k: None for k in ['Hprev', 'Hobs', 'Qprev', 'Qobs']}

                            if grandeur == 'Z':
                                tab[i][date]['Hprev'] = val - zero
                            else:
                                tab[i][date]['Qprev'] = val
                        if if_obs:
                            rows = self.mdb.run_query(sql2.format(self.mdb.SCHEMA, code, debut, fin), fetch=True)
                            for g, date, valeur in rows:
                                if date not in tab[i].keys():
                                    tab[i][date] = {k: None for k in ['Hprev', 'Hobs', 'Qprev', 'Qobs']}

                                tab[i][date][g + "obs"] = valeur

                        for j, g in enumerate(('H', 'Q')):

                            if i % 5 == 0 and j == 0:
                                plt.rcParams['text.usetex'] = False
                                fig, ax = plt.subplots(5, 2, figsize=(8.27, 11.69))

                            ax[i % 5, j].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
                            ax[i % 5, j].xaxis.set_major_locator(mdates.AutoDateLocator())
                            ax[i % 5, j].xaxis.set_tick_params(labelsize=5)
                            ax[i % 5, j].yaxis.set_tick_params(labelsize=6)
                            ax[i % 5, j].grid(which='both', linestyle=':')
                            # ax[i%5,j].grid(which='minor', alpha=0.5)
                            ax[i % 5, j].grid(which='major', alpha=1)
                            if if_obs:
                                listeobs = sorted(tab[i].keys())
                                ax[i % 5, j].plot(listeobs, [tab[i][d][g + 'obs'] for d in listeobs], color='grey',
                                                  marker='o',
                                                  markersize=2, label='Observation')

                            listeprev = [d for d in sorted(tab[i].keys()) if tab[i][d][g + 'prev'] is not None]
                            ax[i % 5, j].plot(listeprev, [tab[i][d][g + 'prev'] for d in listeprev], color='blue',
                                              label=u'Forecast')
                            ax[i % 5, j].set_xlabel("Date", fontsize=8)
                            if g == 'H':
                                ax[i % 5, j].set_ylabel(u"Scale rating (in m)", fontsize=8)
                                if aff_seuil:
                                    lst_seuil = [typs for typs in self.typ_seuil if typs[0] == 'H']
                                    for seuil in lst_seuil:
                                        if dict_check[seuil]['bool']:
                                            vals = dict_check[seuil]['val']
                                            color = dict_check[seuil]['color']
                                            if vals[0] < vals[1]:
                                                ax[i % 5, j].fill_between(listeprev,
                                                                          vals[0],
                                                                          vals[1],
                                                                          color=f'{color}',
                                                                          alpha=0.7)
                            else:
                                ax[i % 5, j].set_ylabel(u"Flow rate (in m3/s)", fontsize=8)
                                if aff_seuil:
                                    lst_seuil = [typs for typs in self.typ_seuil if typs[0] == 'Q']
                                    for seuil in lst_seuil:
                                        if dict_check[seuil]['bool']:
                                            vals = dict_check[seuil]['val']
                                            color = dict_check[seuil]['color']
                                            if vals[0] < vals[1]:
                                                ax[i % 5, j].fill_between(listeprev,
                                                                          vals[0],
                                                                          vals[1],
                                                                          color=f'{color}',
                                                                          alpha=0.7)
                            if if_obs:
                                ax[i % 5, j].set_title(u"{0} ({1}) - {2}".format(nom, code, scenario), fontsize=10)
                            else:
                                ax[i % 5, j].set_title(u"{0} - {2}".format(nom, code, scenario), fontsize=10)
                            ax[i % 5, j].legend(fontsize=6)
                            plt.tight_layout()
                        if i % 5 == 4:
                            pdf.savefig()
                            plt.close()
                    if i % 5 != 4:
                        pdf.savefig()

                    for g in ('H', 'Q'):
                        for i in sorted(tab.keys()):
                            for date in sorted(tab[i].keys()):
                                if g == 'H':
                                    chaine = '{0};{1};{2};{Hobs};{Hprev}\n'
                                else:
                                    chaine = '{0};{1};{2};{Qobs};{Qprev}\n'

                                if tab[i][date][g + 'obs'] is None and tab[i][date][g + 'prev'] is None:
                                    continue
                                fich.write(chaine.format(code, g, date, **tab[i][date]))
        except PermissionError:
            self.mgis.add_info("********* Failed to create the graphics ***********")
            msg = "Error : " \
                  "An access permission error occurred with the file. " \
                  "Please make sure to close the relevant files."
            self.box.info(msg, title="Error")
            self.mgis.add_info(msg)
        except Exception as err:
            self.mgis.add_info("********* Failed to create the graphics ***********")
            self.mgis.add_info("Error : {}".format(err))

    def law_graph(self, dossier, dict_check, run, output_info, aff_seuil, par_event):
        """
        :param dossier: (str) Folder path
        :param dict_check: (dict) thresholds infortmations
        :param run: (int) Run index
        :param output_info:(dict) outputs parameters
        :param aff_seuil:(bool) if display the thresholds
        :param par_event: (dict) scenario infortmations
        """
        tab = {}
        nom = output_info['name'][0]
        abscisse = output_info['abscissa'][0]
        zero = (0 if output_info['zero'][0] is None else output_info['zero'][0])

        path_csv = os.path.join(dossier, '{0}_{1}.csv'.format(run, nom))
        path_pdf = os.path.join(dossier, '{0}_{1}.pdf'.format(run, nom))

        try:
            with open(path_csv, 'w') as fich:
                with PdfPages(path_pdf) as pdf:
                    fich.write('station;type;time;forecast\n')
                    for i, scenario in enumerate(par_event):
                        tab[i] = {}

                        sql1 = """SELECT v.var, r."time", r.val
                                  FROM {0}.results r, {0}.runs rr, {0}.results_var v
                                  WHERE r.id_runs = rr.id
                                  AND rr.run = '{1}' AND rr.scenario = '{2}'
                                  AND r.pknum = {3}
                                  AND r.var = v.id AND v.var IN ('Z','Q')"""

                        rows = self.mdb.run_query(sql1.format(self.mdb.SCHEMA, run, scenario, abscisse), fetch=True)
                        for grandeur, date, val in rows:
                            if date not in tab[i].keys():
                                tab[i][date] = {k: None for k in ['Hprev', 'Qprev']}

                            if grandeur == 'Z':
                                tab[i][date]['Hprev'] = val - zero
                            else:
                                tab[i][date]['Qprev'] = val

                        for j, g in enumerate(('H', 'Q')):

                            if i % 5 == 0 and j == 0:
                                plt.rcParams['text.usetex'] = False
                                fig, ax = plt.subplots(5, 2, figsize=(8.27, 11.69))

                            ax[i % 5, j].xaxis.set_tick_params(labelsize=5)
                            ax[i % 5, j].yaxis.set_tick_params(labelsize=6)
                            ax[i % 5, j].grid(which='both', linestyle=':')
                            ax[i % 5, j].grid(which='major', alpha=1)

                            listeprev = [d for d in sorted(tab[i].keys()) if tab[i][d][g + 'prev'] is not None]
                            ax[i % 5, j].plot(listeprev, [tab[i][d][g + 'prev'] for d in listeprev], color='blue',
                                              label=u'Forecast')
                            ax[i % 5, j].set_xlabel("Time (s)", fontsize=8)
                            if g == 'H':
                                ax[i % 5, j].set_ylabel(u"Scale rating (in m)", fontsize=8)
                                if aff_seuil:
                                    lst_seuil = [typs for typs in self.typ_seuil if typs[0] == 'H']
                                    for seuil in lst_seuil:
                                        if dict_check[seuil]['bool']:
                                            vals = dict_check[seuil]['val']
                                            color = dict_check[seuil]['color']
                                            if vals[0] < vals[1]:
                                                ax[i % 5, j].fill_between(listeprev,
                                                                          vals[0],
                                                                          vals[1],
                                                                          color=f'{color}',
                                                                          alpha=0.7)
                            else:
                                ax[i % 5, j].set_ylabel(u"Flow rate (in m3/s)", fontsize=8)
                                if aff_seuil:
                                    lst_seuil = [typs for typs in self.typ_seuil if typs[0] == 'Q']
                                    for seuil in lst_seuil:
                                        if dict_check[seuil]['bool']:
                                            vals = dict_check[seuil]['val']
                                            color = dict_check[seuil]['color']
                                            if vals[0] < vals[1]:
                                                ax[i % 5, j].fill_between(listeprev,
                                                                          vals[0],
                                                                          vals[1],
                                                                          color=f'{color}',
                                                                          alpha=0.7)

                            ax[i % 5, j].set_title(u"{0} - {1}".format(nom, scenario), fontsize=10)
                            ax[i % 5, j].legend(fontsize=6)
                            plt.tight_layout()
                        if i % 5 == 4:
                            pdf.savefig()
                            plt.close()
                    if i % 5 != 4:
                        pdf.savefig()

                    for g in ('H', 'Q'):
                        for i in sorted(tab.keys()):
                            for date in sorted(tab[i].keys()):
                                if g == 'H':
                                    chaine = '{0};{1};{2};{Hprev}\n'
                                else:
                                    chaine = '{0};{1};{2};{Qprev}\n'

                                if tab[i][date][g + 'prev'] is None:
                                    continue
                                fich.write(chaine.format(scenario, g, date, **tab[i][date]))
        except PermissionError:
            self.mgis.add_info("********* Failed to create the graphics ***********")
            msg = "Error : " \
                  "An access permission error occurred with the file. " \
                  "Please make sure to close the relevant files."
            self.box.info(msg, title="Error")
            self.mgis.add_info(msg)
        except Exception as err:
            self.mgis.add_info("********* Failed to create the graphics ***********")
            self.mgis.add_info("Error : {}".format(err))
