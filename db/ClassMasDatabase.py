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
import numpy as np
import subprocess
import io

import psycopg2
import psycopg2.extras
from qgis.core import QgsVectorLayer, QgsProject

from . import MasObject as Maso
from ..WaterQuality import ClassTableWQ
from ..ui.custom_control import ClassWarningBox
from ..Function import read_version
from .Check_tab import CheckTab

try:  # qgis2
    from qgis.core import QgsMapLayerRegistry, QgsDataSourceURI

    VERSION_QGIS = 2
except:  # qgis3
    from qgis.core import QgsDataSourceUri

    VERSION_QGIS = 3

from qgis.gui import QgsMessageBar


class ClassMasDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """

    SCHEMA = 'start'
    SRID = 2180
    OVERWRITE = True
    LOAD_ALL = True
    CHECK_URI = True
    USER = 'postgres'

    def __init__(self, mgis, dbname, host, port, user, password):
        """
        Constructor for database object

        Args:
            mgis (QgsInterface instance): Instance of QGIS interface.
            dbname (str): Name of the database.
            host (str): Host of the database.
            port (str): Port of the database.
            user (str):User login.
            password (str): Password for user.
        """
        self.mgis = mgis
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.con = None
        self.last_conn = None
        self.last_schema = None
        # liste des tables actuelle
        self.register = {}
        # group d'affichage
        self.group = None
        self.queries = {}
        self.uris = []
        self.refresh_uris()
        self.box = ClassWarningBox()

    def connect_pg(self):
        """
        Method for setting up PostgreSQL connection object as MasDatabase class instance attribute.
        Connection parameters are passed using the dsn.

        Returns:
            str: String message.
        """
        msg = 'None'
        try:
            conn_params = 'dbname={0} host={1} port={2} user={3} password={4}'.format(self.dbname, self.host, self.port,
                                                                                      self.user, self.password)
            self.con = psycopg2.connect(conn_params)
            msg = 'Connection established.'
        except psycopg2.OperationalError as e:
            self.mgis.iface.messageBar().pushMessage("Error",
                                                     'Can\'t connect to PostGIS database. Check connection details!',
                                                     level=QgsMessageBar.CRITICAL, duration=10)
            msg = 'Error: Can\'t connect to PostGIS database "{}".'.format(self.dbname)

        finally:
            self.mgis.add_info(msg)
            return msg

    def disconnect_pg(self):
        """
        Closing connection to database.
        """
        if self.con:
            self.con.close()
            self.con = None
            self.register.clear()
            self.queries.clear()
        else:
            self.mgis.add_info('Can not disconnect. There is no opened connection!')

    def execute(self, sql):
        cur = self.con.cursor()
        cur.execute(sql)
        self.con.commit()

    def run_query(self, qry, fetch=False, arraysize=-1, be_quiet=False, namvar=False, many=False, list_many=None):
        """
        Running PostgreSQL queries

        Args:
            qry (str): Query for database.
            fetch (bool): Flag for returning result from query.
            arraysize (int): Number of items returned from query - default 0 mean using fetchall method.
            be_quiet (bool): Flag for printing exception message.
            namvar (bool): Flag if returning variables name of returning results
            many(bool): True :executemany
            list_many: list value

        Returns:
            list/generator/None: Returned value depends on the 'fetch' and 'arraysize' parameters.
        """

        if list_many is None:
            list_many = []
        result = None
        descr = None
        try:
            if self.con:
                cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                if many:
                    cur.executemany(qry, list_many)
                else:
                    cur.execute(qry)
                if fetch is True and arraysize <= 0:
                    result = cur.fetchall()
                    descr = cur.description
                elif fetch is True and arraysize > 0:
                    result = self.result_iter(cur, arraysize)
                    descr = cur.description
                else:
                    descr = []
                    result = []
                self.con.commit()
            else:
                self.mgis.add_info('There is no opened connection! Use "connect_pg" method before running query.')
        except Exception as e:
            self.con.rollback()
            if be_quiet is False:
                txt = u'{}'.format(repr(e))
                self.mgis.add_info(txt)
            else:
                pass
        finally:
            # description pb voir ou utilisé
            if namvar:
                return result, descr
            else:
                return result

    @staticmethod
    def result_iter(cursor, arraysize):
        """
        Generator for getting partial results from query.

        Args:
            cursor (psycopg2 cursor object): Cursor with query.
            arraysize (int): Number of items returned from query.

        Yields:
            list: Items returned from query which length <= arraysize.
        """
        while True:
            results = cursor.fetchmany(arraysize)
            if not results:
                break
            else:
                pass
            yield results
            #

    def setup_hydro_object(self, hydro_object, schema=None, srid=None, puser= None, overwrite=None):
        """
        Setting SCHEMA, SRID and OVERWRITE on hydro object.

        Args:
            hydro_object (class): Hydro object class.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
            puser(str) : User of postgres
            overwrite (bool): Flag deciding if objects can be overwrite.
        """
        if schema is None:
            hydro_object.SCHEMA = self.SCHEMA
        else:
            hydro_object.SCHEMA = schema
        if srid is None:
            hydro_object.SRID = self.SRID
        else:
            hydro_object.SRID = srid
        if overwrite is None:
            hydro_object.OVERWRITE = self.OVERWRITE
        else:
            hydro_object.OVERWRITE = overwrite
        if overwrite is None:
            hydro_object.USER= self.USER
        else:
            hydro_object.USER = puser

    def process_masobject(self, masobject, pg_method, schema=None, srid=None,  puser= None,overwrite=None, **kwargs):
        """
        Creating and processing tables inside PostGIS database.

        Args:
            masobject (class): Mascaret class object.
            pg_method (str): String representation of method that will be called on the masobject class.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
             puser(str) : User of postgres
            overwrite (bool): Flag deciding if objects can be overwrite.
            **kwargs (dict): Additional keyword arguments passed to pg_method.

        Returns:
            obj: Instance of Mascaret class object
        """
        self.setup_hydro_object(masobject, schema, srid, overwrite,puser)
        print("user", masobject.user)
        obj = masobject()
        method = getattr(obj, pg_method)
        qry = method(**kwargs)
        result = self.run_query(qry)
        if result is not None:
            self.register_object(obj)
            self.queries[method.__name__] = qry
            return obj
        else:
            self.mgis.add_info('Process aborted!')
            #

    def register_object(self, obj):
        """
        Registering object in database as dictionary entry.

        Args:
            obj: Instance of a hydrodynamic schema object class.
        """
        key = obj.name
        if key not in self.register:
            self.register[key] = obj
        else:
            if self.mgis.DEBUG:
                self.mgis.add_info('{0} already exists inside MasPlug registry.'.format(key))
                #

    def register_existing(self, hydro_module, schema=None, srid=None, user= None):
        """
        Registering hydrodynamic model objects which already exists inside schema.

        Args:
            hydro_module (module): hydrodynamic model module.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
        """
        tabs = self.list_tables(schema)
        if tabs:
            for tab in tabs:
                if tab in dir(hydro_module):
                    hydro_object = getattr(hydro_module, tab)
                    self.setup_hydro_object(hydro_object, schema, srid,user=user)
                    obj = hydro_object()
                    self.register_object(obj)
                    if self.mgis.DEBUG:
                        self.mgis.add_info('{0} registered'.format(obj.name))
                else:
                    pass
                    #

    def list_tables(self, schema=None):
        """
        Listing tables in model.

        Args:
            schema (str): Schema where tables will be created or processed.

        Returns:
            list: List of table names in schema.
        """
        if schema is None:
            schema_new = self.SCHEMA
        else:
            schema_new = schema
        qry = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'{0}\''.format(schema_new)
        try:
            tabs = [tab[0] for tab in self.run_query(qry, fetch=True)]
            return tabs
        except TypeError:
            return None

    #
    def refresh_uris(self):
        """
        Setting layers uris list from QgsProject.
        """
        try:  # qgis2
            self.uris = [vl.source() for vl in QgsMapLayerRegistry.instance().mapLayers().values()]

        except:  # qgis3
            self.uris = [vl.source() for vl in QgsProject.instance().mapLayers().values()]
        if self.mgis.DEBUG:
            self.mgis.add_info('Layers sources:\n    {0}'.format('\n    '.join(self.uris)))
            # *****************************************************************************

    def make_vlayer(self, obj):
        """
        Making layer from PostGIS table.

        Args:
            obj: Instance of a hydrodynamic model object class.

        Returns:
            QgsVectorLayer: QGIS Vector Layer object.
        """
        vl_schema, vl_name = obj.schema, obj.name
        try:  # qgis2
            uri = QgsDataSourceURI()
        except:  # qgis3
            uri = QgsDataSourceUri()

        uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        if obj.geom_type is not None:
            uri.setDataSource(vl_schema, vl_name, 'geom')
        else:
            uri.setDataSource(vl_schema, vl_name, None)
        #vlayer = QgsVectorLayer(uri.uri(), vl_name, 'postgres')
        vlayer = QgsVectorLayer(uri.uri(), vl_name, self.user)
        return vlayer

    #
    def add_vlayer(self, vlayer):
        """
        Handling adding layer process to QGIS view.

        Args:
            vlayer (QgsVectorLayer): QgsVectorLayer object.
        """
        try:
            if VERSION_QGIS == 3:  # qgis3
                style_file = os.path.join(self.mgis.masplugPath, 'db', 'styles_qgis3', '{0}.qml'.format(vlayer.name()))
            else:
                style_file = os.path.join(self.mgis.masplugPath, 'db', 'styles_qgis2', '{0}.qml'.format(vlayer.name()))
            if self.group:
                try:  # qgis2
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
                except:  # qgis3
                    QgsProject.instance().addMapLayer(vlayer, False)
                self.group.addLayer(vlayer)

            else:
                try:  # qgis2
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer)
                except:  # qgis3
                    QgsProject.instance().addMapLayer(vlayer)
            # self.mgis.add_info('path : {}'.format(style_file))
            # a mettre apres deplacement group pour etre pris en compte
            vlayer.loadNamedStyle(style_file)
        except Exception as e:
            self.mgis.add_info(repr(e))
            # #

    def add_to_view(self, obj):
        """
        Handling adding layer process to QGIS view.

        Args:
            obj: Instance of a hydrodynamic model object class.
        """
        vlayer = self.make_vlayer(obj)
        src = vlayer.source()
        if self.CHECK_URI is True:
            if src not in self.uris:
                self.add_vlayer(vlayer)
            else:
                pass
        else:
            self.add_vlayer(vlayer)
        return

    def create_model(self, dossier):
        """
        Create empty model inside PostgreSQL database.
        """

        self.register.clear()
        if self.last_schema:
            self.remove_group__layer("Mas_{}".format(self.last_schema))
        self.mgis.add_info('<br><b>Running Create Layers and Tables...</b>')

        try:
            if self.check_extension():
                self.mgis.add_info(" Shema is {}".format(self.SCHEMA))
                self.create_first_model()
            else:
                pass
            chaine = """CREATE SCHEMA {0} ;""" # AUTHORIZATION postgres;"""
            if self.run_query(chaine.format(self.SCHEMA)) is None:
                return
            else:
                self.mgis.add_info('<br>Model "{0}" created.'.format(self.SCHEMA))

            # table
            tables = [Maso.events, Maso.lateral_inflows, Maso.lateral_weirs, Maso.extremities,
                      Maso.flood_marks, Maso.hydraulic_head, Maso.outputs,
                      Maso.weirs, Maso.profiles, Maso.topo, Maso.branchs,
                      Maso.observations, Maso.parametres, Maso.resultats, Maso.runs, Maso.laws,
                      Maso.admin_tab, Maso.visu_flood_marks,
                      # bassin
                      Maso.basins, Maso.links, Maso.resultats_basin, Maso.resultats_links,
                      # qualite d'eau
                      Maso.tracer_lateral_inflows, Maso.tracer_physic, Maso.tracer_name,
                      Maso.tracer_config, Maso.laws_wq,
                      Maso.init_conc_config, Maso.init_conc_wq,
                      # meteo
                      Maso.meteo_config, Maso.laws_meteo,
                      # ouvrage
                      Maso.struct_config, Maso.profil_struct, Maso.struct_param,
                      Maso.struct_elem, Maso.struct_elem_param,
                      Maso.struct_abac, Maso.struct_laws,
                      # ouvrage mobile
                      Maso.struct_fg, Maso.struct_fg_val,
                      Maso.weirs_mob_val,
                      # new results
                      Maso.runs_graph, Maso.results, Maso.results_var,
                      Maso.results_sect
                      ]
            tables.sort(key=lambda x: x().order)
            for masobj_class in tables:
                # try:
                    obj = self.process_masobject(masobj_class, 'pg_create_table')
                    if self.mgis.DEBUG:
                        self.mgis.add_info('  {0} OK'.format(obj.name))
                # except Exception as err:
                #     self.mgis.add_info('failure!<br> {0}'.format(masobj_class))
                #     self.mgis.add_info('Error : {}'.format(err))
                #     # ajout variable fichier parameter
                #     # req = """COPY {0}.parametres FROM '{1}' DELIMITER ',' CSV HEADER;"""
                #     # req = """COPY {0}.parametres FROM '{1}' DELIMITER ',' CSV;"""
            fichparam = os.path.join(dossier, "parametres.csv")
            # self.run_query(req.format(self.SCHEMA, fichparam))
            liste_value = []
            with open(fichparam, 'r') as file:
                for ligne in file:
                    liste_value.append(ligne.replace('\n', '').split(';'))
            liste_col = self.list_columns('parametres')
            var = ",".join(liste_col)
            valeurs = "("
            for k in liste_col:
                valeurs += '%s,'
            valeurs = valeurs[:-1] + ")"

            sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                                'parametres',
                                                                var,
                                                                valeurs)

            self.run_query(sql, many=True, list_many=liste_value)
            # IF WATER QUALITY
            tbwq = ClassTableWQ.ClassTableWQ(self.mgis, self)
            tbwq.default_tab_phy()

            self.insert_abacus_table(self.mgis.dossier_struct)
            self.insert_var_to_result_var(dossier)

            # admin_tab
            chkt = CheckTab(self.mgis, self)
            chkt.all_version(self.list_tables(self.SCHEMA),
                             read_version(self.mgis.masplugPath))

            # add fct
            cl = Maso.class_fct_psql()
            cl.user = self.user
            lfct = [cl.pg_abscisse_profil(),
                    cl.pg_all_profil(),
                    cl.pg_abscisse_point(),
                    cl.pg_all_point(),
                    ]
            for sql in lfct:
                self.run_query(sql)

            # visualization
            self.load_gis_layer()

            self.mgis.add_info('Model "{0}" completed'.format(self.SCHEMA))

        except Exception as e:
            self.mgis.add_info("Echec of creation model")
            self.mgis.add_info(str(e))

    def add_table_basins(self, dossier):
        """
        Add table  for water Quality model
        """

        tables = [Maso.basins, Maso.links,
                  Maso.resultats_basin, Maso.resultats_links]
        tables.sort(key=lambda x: x().order)

        for masobj_class in tables:
            try:
                masobj_class.user=self.user
                obj = self.process_masobject(masobj_class, 'pg_create_table')
                if self.mgis.DEBUG:
                    self.mgis.add_info('  {0} OK'.format(obj.name))
            except Exception as err:

                self.mgis.add_info('failure!<br> {0}'.format(masobj_class))
                self.mgis.add_info('Error : {}'.format(err))

        fichparam = os.path.join(dossier, "parametres.csv")
        # self.run_query(req.format(self.SCHEMA, fichparam))
        liste_value = []
        with open(fichparam, 'r') as file:
            for ligne in file:
                list_val = ligne.replace('\n', '').split(';')
                if list_val[-1] == 'basins':
                    liste_value.append(list_val)

        sql = "DELETE FROM {}.parametres;".format(self.SCHEMA)
        self.run_query(sql)

        liste_value = []
        with open(fichparam, 'r') as file:
            for ligne in file:
                liste_value.append(ligne.replace('\n', '').split(';'))
        liste_col = self.list_columns('parametres')
        var = ",".join(liste_col)
        valeurs = "("
        for k in liste_col:
            valeurs += '%s,'
        valeurs = valeurs[:-1] + ")"

        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                            'parametres',
                                                            var,
                                                            valeurs)

        self.run_query(sql, many=True, list_many=liste_value)

    def add_table_wq(self, dossier):
        """
        Add table  for water Quality model
        """
        tables = [Maso.tracer_lateral_inflows, Maso.tracer_physic, Maso.tracer_name,
                  Maso.tracer_config, Maso.laws_wq, Maso.init_conc_config,
                  Maso.init_conc_wq, Maso.meteo_config, Maso.laws_meteo]
        tables.sort(key=lambda x: x().order)

        for masobj_class in tables:
            try:
                masobj_class.overwrite = True
                masobj_class.user =self.user
                obj = self.process_masobject(masobj_class, 'pg_create_table')
                if self.mgis.DEBUG:
                    self.mgis.add_info('  {0} OK'.format(obj.name))
            except Exception as err:
                self.mgis.add_info('failure!<br> {0}'.format(masobj_class))
                self.mgis.add_info('Error : {}'.format(err))

        sql = """ALTER TABLE {}.runs ADD COLUMN IF NOT EXISTS wq text;"""
        self.run_query(sql.format(self.SCHEMA))
        sql = """ALTER TABLE {}.extremities ADD COLUMN IF NOT EXISTS tracer_boundary_condition_type integer NULL ;"""
        self.run_query(sql.format(self.SCHEMA))
        sql = """ALTER TABLE {}.extremities ADD COLUMN IF NOT EXISTS law_wq text;"""
        self.run_query(sql.format(self.SCHEMA))
        # add parameters
        sql = """ALTER TABLE {}.parametres ADD COLUMN IF NOT EXISTS gui_type text DEFAULT 'parameters';"""
        self.run_query(sql.format(self.SCHEMA))
        fichparam = os.path.join(dossier, "parametres.csv")
        # self.run_query(req.format(self.SCHEMA, fichparam))
        liste_value = []
        with open(fichparam, 'r') as file:
            for ligne in file:
                list_val = ligne.replace('\n', '').split(';')
                if list_val[-1] == 'tracers':
                    liste_value.append(list_val)

        # liste_col = self.list_columns('parametres')
        # var = ",".join(liste_col)
        # valeurs = "("
        # for k in liste_col:
        #     valeurs += '%s,'
        # valeurs = valeurs[:-1] + ")"
        #
        # sql = "INSERT INTO {0}.{1}({2}) VALUES {3} ON CONFLICT DO NOTHING;".format(self.SCHEMA,
        #                                                                            'parametres',
        #                                                                            var,
        #                                                                            valeurs)
        #
        # self.run_query(sql, many=True, list_many=liste_value)

        # phy parameters
        tbwq = ClassTableWQ.ClassTableWQ(self.mgis, self)
        tbwq.default_tab_phy()

    def add_table_struct(self, dossier):
        """
        Add table  for water Quality model
        """

        tables = [
            Maso.struct_config, Maso.profil_struct, Maso.struct_param,
            Maso.struct_elem, Maso.struct_elem_param,
            Maso.struct_abac, Maso.struct_laws
        ]
        tables.sort(key=lambda x: x().order)

        for masobj_class in tables:
            try:
                masobj_class.overwrite = True
                masobj_class.user = self.user
                obj = self.process_masobject(masobj_class, 'pg_create_table')
                if self.mgis.DEBUG:
                    self.mgis.add_info('  {0} OK'.format(obj.name))
            except Exception as err:
                self.mgis.add_info('failure!<br> {0}'.format(masobj_class))
                self.mgis.add_info('Error : {}'.format(err))
        self.insert_abacus_table(dossier)

        list_col = self.list_columns('profiles')
        sql = ''
        if 'struct' in list_col:
            sql = "ALTER TABLE {0}.profiles DROP COLUMN IF EXISTS  struct;\n"
        sql += "ALTER TABLE {0}.profiles ADD COLUMN struct integer DEFAULT 0;"
        self.run_query(sql.format(self.SCHEMA))

    def create_first_model(self):
        """ 
        To add variable in db for the first model creation
        and to add exemple
        :return: 
        """
        try:
            self.run_query("CREATE EXTENSION postgis;")
            self.run_query("CREATE EXTENSION postgis_topology;")

            self.disconnect_pg()
            self.connect_pg()

            listefct = ['pg_create_calcul_abscisse',
                        'pg_create_calcul_abscisse_profil',
                        'pg_create_calcul_abscisse_branche',
                        'pg_chstate_branch',
                        'pg_chstate_basin',
                        # visu
                        'pg_delete_visu_flood_marks',
                        'pg_create_calcul_abscisse_point_flood',
                        ]
            for fct in listefct:
                try:
                    obj = self.process_masobject(Maso.class_fct_psql, fct)
                    if self.mgis.DEBUG:
                        self.mgis.add_info('  {0} OK'.format(fct))
                    else:
                        pass
                except Exception as err:
                    if self.mgis.DEBUG:
                        self.mgis.add_info('{0}\n'.format(fct))
                        self.mgis.add_info('failure!<br> {0}'.format(fct))
                        self.mgis.add_info('Error {}: '.format(err))
                    else:
                        pass

        except Exception as e:
            self.disconnect_pg()
            self.mgis.add_info("Echec of creation First Model")

    def check_fct(self, fct_name):
        cond = True
        if isinstance(fct_name, list):

            for name in fct_name:
                sql = " select exists(select * from pg_proc where proname = '{}');".format(name)
                rows = self.run_query(sql, fetch=True)[0][0]
                if not rows:
                    cond = False
            return cond
        else:
            sql = " select exists(select * from pg_proc where proname = '{}');".format(fct_name)
            rows = self.run_query(sql, fetch=True)[0][0]
            if not rows:
                cond = False
            return cond

    def add_fct_for_update_pk(self):
        """add fct psql to compute abscissa"""
        cl = Maso.class_fct_psql()
        lfct = [cl.pg_abscisse_profil(), cl.pg_all_profil(),
                cl.pg_abscisse_point(), cl.pg_all_point(),
                cl.pg_abscisse_branch(), cl.pg_all_branch(),
                ]
        qry = ''
        for sql in lfct:
            qry += sql
            qry += '\n'
        self.run_query(qry)

    def add_fct_for_visu(self):
        """ add fct psql for the visualisation"""
        cl = Maso.class_fct_psql()
        lfct = [cl.pg_delete_visu_flood_marks(),
                cl.pg_create_calcul_abscisse_point_flood()]
        qry = ''
        for sql in lfct:
            qry += sql
            qry += '\n'

        self.run_query(qry)

    def check_first_model(self):
        """
        Check if first model
        :return: bool
        """
        qry = "SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' " \
              "AND nspname != 'information_schema' ORDER BY nspname"
        model = self.run_query(qry, fetch=True)
        if len(model) > 1:
            return False
        else:
            return True

    def check_extension(self):
        """check postgis extension """
        sql = "SELECT extname FROM pg_extension"
        extension = self.run_query(sql, fetch=True)
        cond = True
        if extension is None:
            return cond
        for ext in extension:
            if ext[0] == 'postgis':
                cond = False
        return cond

    def liste_models(self):
        liste = []
        try:
            sql = """SELECT schema_name FROM information_schema.schemata"""
            rows = self.run_query(sql, fetch=True)
            exclusion = ["pg_toast",
                         "pg_temp_1",
                         "pg_toast_temp_1",
                         "pg_catalog",
                         "public",
                         "topology",
                         "information_schema"]
            for row in rows:
                if row[0] not in exclusion and row[0][:3] != "pg_":
                    liste.append('{}'.format(row[0]))

        except Exception as e:
            self.mgis.add_info("Problem : to show model list")
            self.mgis.add_info(repr(e))

        return liste

    def drop_model(self, model_name, cascade=False):
        """
        Delete model inside PostgreSQL database.

        Args:
            model_name (str): Name of the schema which will be deleted.
            cascade (bool): Flag forcing cascade delete.
        """
        qry = '''DROP SCHEMA "{0}" CASCADE;''' if cascade is True else '''DROP SCHEMA "{0}";'''
        qry = qry.format(model_name)
        if self.run_query(qry) is None:
            return
        else:
            self.mgis.add_info('<br>Model "{0}" deleted.'.format(model_name))

    def drop_table(self, table_name):
        """
        Delete tables inside PostgreSQL database.

        Args:
            table_name (str): Name of the table which will be deleted.
        """
        qry = 'DROP TABLE IF EXISTS {0}.{1} ;'
        qry = qry.format(self.SCHEMA, table_name)
        if self.run_query(qry) is None:
            return False
        else:
            self.mgis.add_info('<br>Table "{0}" deleted.'.format(table_name))
            return True

    def load_gis_layer(self):
        """ layer visualization in qgis"""
        # visualisation

        root = QgsProject.instance().layerTreeRoot()

        self.group = root.findGroup("Mas_{}".format(self.SCHEMA))
        if not self.group:
            self.group = root.addGroup("Mas_{}".format(self.SCHEMA))
        lst_only_visu = ['visu_flood_marks']
        dict_only_visu = {}
        tables = list(self.register.items())

        # tables.sort(key=lambda x: x[1].order, reverse=True)
        tables.sort(key=lambda x: x[1].order)
        for (name, obj) in tables:
            try:
                # TODO modif if new geometric table
                if obj.order < 16:
                    if name in lst_only_visu:
                        dict_only_visu[name] = obj
                    else:
                        self.add_to_view(obj)

                        if self.mgis.DEBUG:
                            self.mgis.add_info(' View {0} : OK'.format(obj.name))
                else:
                    pass
            except Exception as err:

                self.mgis.add_info('View failure!<br> {0}'.format(obj.name))
                self.mgis.add_info('Error : {}'.format(err))

        # add visualistation layer
        group_main = self.group
        self.group = group_main.findGroup("Visualisation".format(self.SCHEMA))
        if not self.group:
            self.group = group_main.addGroup("Visualisation".format(self.SCHEMA))

        for name, obj in dict_only_visu.items():
            try:
                self.add_to_view(obj)
                if self.mgis.DEBUG:
                    self.mgis.add_info(' View {0} : OK'.format(obj.name))
            except Exception as err:
                self.mgis.add_info('View failure!<br>{0}'.format(obj.name))
                self.mgis.add_info('Error : {}'.format(err))

        self.mgis.iface.mapCanvas().refresh()

    #
    def create_spatial_index(self):
        """
        Create PostgreSQL function create_st_index_if_not_exists(schema, table).
        The function checks if a spatial index exists for the table - if not, it is created.
        """
        qry = '''
CREATE OR REPLACE FUNCTION "{0}".create_spatial_index(schema text, t_name text)
    RETURNS VOID AS
$BODY$
DECLARE
    full_index_name text;
BEGIN
    full_index_name = schema || '_' || t_name || '_' || 'geom_idx';
    IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = full_index_name AND n.nspname = schema
        )
    THEN
        EXECUTE 'CREATE INDEX "' || full_index_name || '" ON "' || schema || '"."' || t_name || '" USING GIST (geom)';
    END IF;
END;
$BODY$
    LANGUAGE plpgsql;
'''
        qry = qry.format(self.SCHEMA)
        self.run_query(qry)

    def load_model(self):
        """ Load model"""
        self.register.clear()
        if self.last_schema:
            self.remove_group__layer("Mas_{}".format(self.last_schema))
        self.mgis.add_info('Current DB schema is: {0}'.format(self.SCHEMA))
        # crée index spatial si non existant
        self.create_spatial_index()
        self.register_existing(Maso, self.user)
        reg = [self.register[k].name for k in sorted(self.register.keys())]
        if self.mgis.DEBUG:
            self.mgis.add_info('Objects registered in the database:<br>  {0}'.format('<br>  '.join(reg)))
            self.mgis.add_info('You can load them now using  Geometry > Load Mascaret Database Tables Into QGIS')
        else:
            if reg:
                self.mgis.add_info('There are some objects registered in the database.')
            else:
                self.mgis.add_info('Mascaret database is empty.<br>Create or import your river network data.')
        #
        self.load_gis_layer()

    def remove_group__layer(self, name):
        root = QgsProject.instance().layerTreeRoot()
        group1 = root.findGroup(name)
        if group1 is not None:
            for child in group1.children():
                dump = child.dump()
                id = dump.split("=")[-1].strip()
                try:  # qgis2
                    QgsMapLayerRegistry.instance().removeMapLayer(id)
                except:  # qgis3
                    QgsProject.instance().removeMapLayer(id)
            root.removeChildNode(group1)

    def projection(self, nom, liste_x, liste_g):
        """ fonction de projection de la bathymétrie le long du profil """

        sql = """SELECT t.gid, 
                       ST_Length(p.geom)*ST_LineLocatePoint(ST_LineMerge(p.geom), t.geom) as x 
                FROM {0}.profiles as p, {0}.topo as t 
                WHERE p.name='{1}'
                AND t.profile ='{1}'
                AND t.x IS NULL
                AND t.gid IN ({2})"""

        rows = self.run_query(sql.format(self.SCHEMA,
                                         nom,
                                         ",".join(map(str, liste_g))),
                              fetch=True)

        for gid, x in rows:
            if gid in liste_g:
                i = liste_g.index(gid)
                liste_x[i] = x

        return liste_x

    def select(self, table, where="", order="", list_var=None):
        """ Select variables of table"""
        if where:
            where = " WHERE " + where + " "
        if order:
            order = " ORDER BY " + order
        if list_var is not None:
            lvar = ','.join([str(v) for v in list_var])
        else:
            lvar = '*'

        sql = "SELECT {4} FROM {0}.{1} {2} {3};"
        # print(sql.format(self.SCHEMA, table, where, order, lvar))
        (results, namCol) = self.run_query(sql.format(self.SCHEMA, table, where, order, lvar), fetch=True, namvar=True)
        if results is None or namCol is None:
            print("error : ", sql.format(self.SCHEMA, table, where, order, lvar))
            return None
        cols = [col[0] for col in namCol]
        dico = {}
        for col in cols:
            dico[col] = []

        for row in results:
            for i, val in enumerate(row):
                try:
                    dico[cols[i]].append(val.strip())
                except:
                    dico[cols[i]].append(val)
        return dico

    #
    def select_one(self, table, where="", order=""):
        """select one variable"""

        if where:
            where = " WHERE " + where + " "
        if order:
            order = " ORDER BY " + order

        sql = "SELECT * FROM {0}.{1} {2} {3};"
        # self.mgis.add_info(sql.format(self.SCHEMA, table, where, order))
        (results, namCol) = self.run_query(sql.format(self.SCHEMA, table, where, order),
                                           fetch=True, arraysize=1, namvar=True)

        if results is None or namCol is None:
            print("error : ", sql.format(self.SCHEMA, table, where, order))
            return None
        cols = [col[0] for col in namCol]
        results = [col[0] for col in results]

        dico = {}
        # self.mgis.add_info("{0} {1}".format(results[0],cols))
        for i, val in enumerate(results[0]):
            # self.mgis.add_info("{0}  {1}".format(cols[i],val))
            dico[cols[i]] = val

        return dico

    #
    def select_distinct(self, var, table, where="", ordre=None):
        """select the "where" variable which is multiple"""
        if ordre is None:
            ordre = var
        if where:
            where = "WHERE " + where
        sql = "SELECT DISTINCT {0} FROM {1}.{2} {3} ORDER BY {4};"
        (results, namCol) = self.run_query(sql.format(var, self.SCHEMA, table, where, ordre), fetch=True, namvar=True)
        if namCol and results:
            cols = [col[0] for col in namCol]
            dico = {}
            for row in results:
                for i, val in enumerate(row):
                    if cols[i] not in dico.keys():
                        dico[cols[i]] = []
                    try:
                        dico[cols[i]].append(eval(val))
                    except:
                        dico[cols[i]].append(val)

            return dico
        # print('warning', sql.format(var, self.SCHEMA, table, where, ordre))
        return None

    #
    def select_max(self, var, table, where=None):
        """select the max in the table for the "where" variable"""
        if where:
            sql = "SELECT MAX({0}) FROM {1}.{2} WHERE {3};".format(var, self.SCHEMA, table, where)
        else:
            sql = "SELECT MAX({0}) FROM {1}.{2};".format(var, self.SCHEMA, table)
        results = self.run_query(sql, fetch=True, arraysize=1)
        # results obj: generator
        if results:
            for row in results:
                var = row[0][0]
            return var
        else:
            print("error : ", sql.format(self.SCHEMA, table, where, order, lvar))
            return None

    def select_min(self, var, table, where=None):
        """select the max in the table for the "where" variable"""
        if where:
            sql = "SELECT MIN({0}) FROM {1}.{2} WHERE {3};".format(var, self.SCHEMA, table, where)
        else:
            sql = "SELECT MIN({0}) FROM {1}.{2};".format(var, self.SCHEMA, table)
        results = self.run_query(sql, fetch=True, arraysize=1)
        # results obj: generator
        for row in results:
            var = row[0][0]
        return var

    def delete(self, table, where=None):
        """ Delete table information"""
        if where:
            where = "WHERE {0}".format(where)
        sql = "DELETE FROM {0}.{1} {2} ;".format(self.SCHEMA, table, where)
        self.run_query(sql)
        # if self.mgis.DEBUG:
        #     self.mgis.add_info('function delete end')

    def insert(self, table, tab, colonnes, delim=" "):
        tmp = [colonnes[0]]
        tmp += sorted(colonnes[1:])
        var = ",".join(tmp)
        valeurs = ""
        for id in tab.keys():

            if isinstance(id, basestring):
                valeurs += "('" + str(id) + "',"
            else:
                valeurs += "(" + str(id) + ","
            for k in sorted(tab[id].keys()):
                if isinstance(tab[id][k], basestring):
                    valeurs += "'" + tab[id][k] + "',"
                elif isinstance(tab[id][k], list):
                    valeurs += "'" + delim.join(tab[id][k]) + "',"
                else:
                    valeurs += str(tab[id][k]) + ","
            valeurs = valeurs[:-1] + "),"

        valeurs = valeurs[:-1]

        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                            table,
                                                            var,
                                                            valeurs)

        self.run_query(sql)
        # if self.mgis.DEBUG:
        #     self.mgis.add_info('function insert end')

    def insert2(self, table, tab):
        """ insert table in tableSQl"""
        colonnes = sorted(tab.keys())
        var = ','.join(colonnes)

        valeurs = []
        for i in range(len(tab[colonnes[0]])):
            temp = []
            for k in colonnes:
                temp.append(str(tab[k][i]))
            valeurs.append("({})".format(",".join(temp)))
        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                            table,
                                                            var,
                                                            ",".join(valeurs))
        self.run_query(sql)

    def insert_res(self, table, liste_value, colonnes):
        var = ",".join(colonnes)
        temp = []
        for k in colonnes:
            temp.append('%s')
        valeurs = "({})".format(",".join(temp))

        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                            table,
                                                            var,
                                                            valeurs)
        self.run_query(sql, many=True, list_many=liste_value)

    def new_insert_res(self, table, values, col_tab, be_quiet=False):
        try:
            if self.con:
                file = self.buff_file(values)
                cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.copy_from(file, '{0}.{1}'.format(self.SCHEMA, table), columns=col_tab)
                del file

        except Exception as e:
            self.con.rollback()
            if be_quiet is False:
                txt = u'{}'.format(repr(e))
                self.mgis.add_info(txt)
            else:
                pass

    def buff_file(self, liste):
        txt = ''

        leng = len(liste[0])

        for x in liste:
            for i in range(leng):
                if i == 0:
                    txt += "{}".format(x[i])
                else:
                    txt += "\t{}".format(x[i])
            txt += '\n'

        f = io.StringIO(txt)
        return f

    def update_res(self, table, liste_value, colonnes):

        sql = ''
        for value in liste_value:
            condition = """run='{0}' AND scenario='{1}' """.format(value[colonnes.index('run')],
                                                                   value[colonnes.index('scenario')])
            condition += """AND branche='{}' """.format(value[colonnes.index('branche')])
            condition += """AND t='{}' """.format(value[colonnes.index('t')])
            condition += """AND section='{}' """.format(value[colonnes.index('section')])
            condition += """AND pk='{}' """.format(value[colonnes.index('pk')])
            if "date" in colonnes:
                condition += """AND date='{:%Y-%m-%d %H:%M:%S}' """.format(value[colonnes.index("date")])
            list_exclu = ['run', 'scenario', 'date', 't', 'branche', 'section', 'pk']
            values = ''
            for i, col in enumerate(colonnes):
                if col not in list_exclu:
                    values += "{}='{}' ,".format(col, value[i])
            values = values[:-1]
            sql += "UPDATE  {0}.{1} SET {2} WHERE {3};\n".format(self.SCHEMA, table, values, condition)

        self.run_query(sql)

    def update(self, table, tab, var="nom"):
        """update info"""
        for nom, t in tab.items():
            tab_var = []
            for k, v in tab[nom].items():
                if not v and not isinstance(v, float) and not isinstance(v, int):
                    tab_var.append("{0}=NULL".format(k))
                elif isinstance(v, str):
                    tab_var.append("{0}='{1}'".format(k, v))
                elif isinstance(v, list):
                    tab_var.append("{0}='{1}'".format(k, " ".join(map(str, v))))
                else:
                    tab_var.append("{0}={1}".format(k, v))

            sql = """UPDATE {0}.{1} SET {2}  WHERE {3}='{4}'"""
            self.run_query(sql.format(self.SCHEMA,
                                      table,
                                      ", ".join(tab_var),
                                      var,
                                      nom))
            if self.mgis.DEBUG:
                self.mgis.add_info('function update end')

    def copy(self, table, var, fichier):
        """Copy file in sql"""
        sql = """COPY {0}.{1}({2}) FROM '{3}' WITH DELIMITER ',';"""
        self.run_query(sql.format(self.SCHEMA, table, ",".join(var), fichier))

    def list_columns(self, table):
        """ List columns"""
        sql = """SELECT column_name FROM information_schema.columns 
                  WHERE table_schema='{0}' AND table_name='{1}';"""
        rows = self.run_query(sql.format(self.SCHEMA, table), fetch=True)
        liste = [row[0] for row in rows]
        return liste

    def add_columns(self, table, colonne):
        """ add columns"""
        sql = """ALTER TABLE {0}.{1} ADD COLUMN {2} double precision;"""
        self.run_query(sql.format(self.SCHEMA, table, colonne))

    def export_schema(self, file):
        """export schema"""
        try:
            exe = os.path.join(self.mgis.postgres_path, 'pg_dump')

            if os.path.isfile(exe) or os.path.isfile(exe + '.exe'):
                commande = '"{0}" -p {6} -n {1} -U {2} -f"{3}" -d {4} -h {5}'.format(exe, self.SCHEMA, self.user, file,
                                                                                     self.dbname, self.host, self.port)
                os.putenv("PGPASSWORD", "{0}".format(self.password))

                p = subprocess.Popen(commande, shell=True)
                p.wait()
                return True
            else:
                self.mgis.add_info('Executable file not found. '
                                   'Please, insert path in "path postgres" in Help / Setting / Options')
                return False

        except:
            return False

    def import_schema(self, file):
        """import schema"""
        try:
            exe = os.path.join(self.mgis.postgres_path, 'psql')
            # exe = os.path.join(self.mgis.postgres_path, 'pg_restore')
            if os.path.isfile(exe) or os.path.isfile(exe + '.exe'):
                # d = dict(os.environ)
                # d["PGPASSWORD"] = "{0}".format(self.password)
                os.putenv("PGPASSWORD", "{0}".format(self.password))
                # for file in Listfile:

                commande = '"{0}" -U {1} -p {2} -f "{3}" -d {4} -h {5}'.format(exe, self.user, self.port,
                                                                               file, self.dbname, self.host)

                # p = subprocess.Popen(commande, env=d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                #                      , stdin=subprocess.PIPE)
                p = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                     , stdin=subprocess.PIPE)
                outs, err = p.communicate()
                if self.mgis.DEBUG:
                    self.mgis.add_info("Import File :{0}".format(file))
                    if VERSION_QGIS == 3:
                        self.mgis.add_info("{0}".format(outs.decode('utf-8')))
                    else:
                        self.mgis.add_info("{0}".format(outs))
                p.wait()

                return True
            else:
                self.mgis.add_info('Executable file not found. '
                                   'Please, insert path in "path postgres" in Help / Setting / Options')
                return False
        except:
            return False

    def list_schema(self):
        sql = "SELECT nspname from pg_catalog.pg_namespace;"
        info = self.run_query(sql, fetch=True)
        listf = []
        if info is not None:
            for row in info:
                listf.append(row[0])
        return listf

    def checkschema_import(self, file):
        namesh = None
        with open(file, 'r') as infile:
            for line in infile:
                if line.find('CREATE SCHEMA') > -1:
                    line = line.replace(';', '').replace('\n', '')
                    liste = line.split()
                    namesh = liste[2]
                    break

        return namesh

    def insert_abacus_table(self, dossier):
        list_fich = os.listdir(dossier)
        for fich in list_fich:
            fichabac = os.path.join(dossier, fich)
            liste_value = []
            with open(fichabac, 'r') as file:
                for ligne in file:
                    liste_value.append(ligne.replace('\n', '').split(';'))
            mehtod = liste_value[0][1]
            name_abc = liste_value[1][1]
            list_var = liste_value[2]
            if not self.checkabac(mehtod, name_abc):
                liste_value = np.array(liste_value[3:])
                list_insert = []
                for i, var in enumerate(list_var):
                    for order, val in enumerate(liste_value[:, i]):
                        if val != '':
                            list_insert.append([mehtod, name_abc, var, order, val])
                liste_col = self.list_columns('struct_abac')

                var = ",".join(liste_col)
                valeurs = "("
                for k in liste_col:
                    valeurs += '%s,'
                valeurs = valeurs[:-1] + ")"

                sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                                    'struct_abac',
                                                                    var,
                                                                    valeurs)

                self.run_query(sql, many=True, list_many=list_insert)

    def checkabac(self, method, abc):
        """check if abacus doesn't exist"""
        where = "WHERE nam_method='{}' AND nam_abac ='{}'".format(method, abc)
        sql = "SELECT * FROM {0}.{1} {2};"

        results = self.run_query(sql.format(self.SCHEMA, 'struct_abac', where),
                                 fetch=True, arraysize=1)
        for row in results:
            if row[0][0] is not None:
                return True
        return False

    def check_id_var(self, dico):
        """
        return varibale id  and  add variable if not exist
        :param dico: example : {'var': 'ZSTR',
                    'type_res': 'weirs',
                    'name': 'Valve movement',
                    'type_var': 'float'}
        :return: id_var ; var identifiant number
        """
        id_var = None
        info = self.select('results_var', where="var = '{var}' AND type_res = '{type_res}'".format(**dico),
                           list_var=['id'])
        if info['id']:
            id_var = info['id'][0]
        else:
            if len(dico) > 2:
                dico['schema'] = self.SCHEMA
                id_var = self.select_max('id', 'results_var') + 1
                dico['id'] = id_var
                self.run_query("INSERT INTO {schema}.results_var (id,type_res, var, name,type_var) "
                               "VALUES ( {id}, '{type_res}', '{var}', '{name}','{type_var}')".format(**dico))

        return id_var

    def insert_var_to_result_var(self, dossier):
        try:

            fichparam = os.path.join(dossier, "var.csv")
            liste_value = []
            with open(fichparam, 'r') as file:
                cpt = 0
                for ligne in file:
                    if cpt > 0:
                        liste = ligne.replace('\n', '').split(';')
                        liste_value.append([int(liste[0])] + liste[1:])
                    cpt += 1
            liste_col = self.list_columns('results_var')

            var = ",".join(liste_col)
            valeurs = "("
            for k in liste_col:
                valeurs += '%s,'
            valeurs = valeurs[:-1] + ")"

            sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                                'results_var',
                                                                var,
                                                                valeurs)
            self.run_query(sql, many=True, list_many=liste_value)

            # add tracer variable
            info = self.select('tracer_name', where="type='TRANSPORT_PUR'", list_var=['type', 'text', 'sigle'])
            nbv = len(info['type'])
            if nbv > 0:
                dico = {'var': info['sigle'][0],
                        'type_res': 'tracer_{}'.format('TRANSPORT_PUR'),
                        'name': info['text'][0],
                        'type_var': 'float'}
                self.check_id_var(dico)
            return True
        except Exception as e:
            self.mgis.add_info("Error create_var_result: {}".format(str(e)))
            return False
