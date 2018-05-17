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
import psycopg2
import psycopg2.extras

from qgis.core import QgsVectorLayer, NULL,QgsProject
try :   #qgis2
    from qgis.core import QgsMapLayerRegistry,QgsDataSourceURI
except :#qgis3
    from qgis.core import QgsDataSourceUri

from qgis.gui import QgsMessageBar

import os
from . import MasObject as maso
import subprocess



class MasDatabase(object):
    """
    Class for PostgreSQL database and hydrodynamic models handling.
    """

    SCHEMA = 'start'
    SRID = 2180
    OVERWRITE = True
    LOAD_ALL = True
    CHECK_URI = True

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
        self.last_conn=None
        self.last_schema=None
        #liste des tables actuelle
        self.register = {}
        #group d'affichage
        self.group=None
        self.queries = {}
        self.uris = []
        self.refresh_uris()


    def connect_pg(self):
        """
        Method for setting up PostgreSQL connection object as MasDatabase class instance attribute.
        Connection parameters are passed using the dsn.

        Returns:
            str: String message.
        """
        msg = 'None'
        try:
            conn_params = 'dbname={0} host={1} port={2} user={3} password={4}'.format(self.dbname, self.host, self.port, self.user, self.password)
            self.con = psycopg2.connect(conn_params)
            msg = 'Connection established.'
        except psycopg2.OperationalError as e:
            self.mgis.iface.messageBar().pushMessage("Error", 'Can\'t connect to PostGIS database. Check connection details!', level=QgsMessageBar.CRITICAL, duration=10)
            msg = 'Error: Can\'t connect to PostGIS database "{}".'.format(self.dbname)

        finally:
            self.mgis.addInfo(msg)
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
            self.mgis.addInfo('Can not disconnect. There is no opened connection!')

    def execute(self, sql):
        cur = self.con.cursor()
        cur.execute(sql)
        self.con.commit()

    def run_query(self, qry, fetch=False, arraysize=-1, be_quiet=False, namvar=False, many=False,listMany=[]):
        """
        Running PostgreSQL queries

        Args:
            qry (str): Query for database.
            fetch (bool): Flag for returning result from query.
            arraysize (int): Number of items returned from query - default 0 mean using fetchall method.
            be_quiet (bool): Flag for printing exception message.
            namvar (bool): Flag if returning variables name of returning results

        Returns:
            list/generator/None: Returned value depends on the 'fetch' and 'arraysize' parameters.
        """

        result = None
        descr = None
        try:
            if self.con:
                cur = self.con.cursor(cursor_factory=psycopg2.extras.DictCursor)
                if many:
                    cur.executemany(qry, listMany)
                else:
                    cur.execute(qry)
                if fetch is True and arraysize <= 0:
                    result = cur.fetchall()
                    descr = cur.description
                elif fetch is True and arraysize > 0:
                    result = self.result_iter(cur, arraysize)
                    descr = cur.description
                else:
                    descr=[]
                    result = []
                self.con.commit()
            else:
                self.mgis.addInfo('There is no opened connection! Use "connect_pg" method before running query.')
        except Exception as e:
            self.con.rollback()
            if be_quiet is False:
                self.mgis.addInfo(repr(e))
            else:
                pass
        finally:
            #description pb voir ou utilisé
            if namvar:
                return result,descr
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

    def setup_hydro_object(self, hydro_object, schema=None, srid=None, overwrite=None):
        """
        Setting SCHEMA, SRID and OVERWRITE on hydro object.

        Args:
            hydro_object (class): Hydro object class.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
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

    def process_masobject(self, masobject, pg_method, schema=None, srid=None, overwrite=None, **kwargs):
        """
        Creating and processing tables inside PostGIS database.

        Args:
            masobject (class): Mascaret class object.
            pg_method (str): String representation of method that will be called on the masobject class.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
            overwrite (bool): Flag deciding if objects can be overwrite.
            **kwargs (dict): Additional keyword arguments passed to pg_method.

        Returns:
            obj: Instance of Mascaret class object
        """
        self.setup_hydro_object(masobject, schema, srid, overwrite)
        obj = masobject()
        method = getattr(obj, pg_method)
        qry = method(**kwargs)
        result = self.run_query(qry)
        if result is not None:
            self.register_object(obj)
            self.queries[method.__name__] = qry
            return obj
        else:
            self.mgis.addInfo('Process aborted!')
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
                self.mgis.addInfo('{0} already exists inside MasPlug registry.'.format(key))
#

    def register_existing(self, hydro_module, schema=None, srid=None):
        """
        Registering hydrodynamic model objects which already exists inside schema.

        Args:
            hydro_module (module): hydrodynamic model module.
            schema (str): Schema where tables will be created or processed.
            srid (int): A Spatial Reference System Identifier.
        """
        tabs = self.list_tables(schema)
        for tab in tabs:
            if tab in dir(hydro_module):
                hydro_object = getattr(hydro_module, tab)
                self.setup_hydro_object(hydro_object, schema, srid)
                obj = hydro_object()
                self.register_object(obj)
                if self.mgis.DEBUG:
                    self.mgis.addInfo('{0} registered'.format(obj.name))
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
            SCHEMA = self.SCHEMA
        else:
            SCHEMA = schema
        qry = 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'{0}\''.format(SCHEMA)
        tabs = [tab[0] for tab in self.run_query(qry, fetch=True)]
        return tabs
#
    def refresh_uris(self):
        """
        Setting layers uris list from QgsProject.
        """
        try :    # qgis2
            self.uris = [vl.source() for vl in QgsMapLayerRegistry.instance().mapLayers().values()]

        except:  # qgis3
            self.uris = [vl.source() for vl in QgsProject.instance().mapLayers().values()]
        if self.mgis.DEBUG:
            self.mgis.addInfo('Layers sources:\n    {0}'.format('\n    '.join(self.uris)))
#*****************************************************************************

    def make_vlayer(self, obj):
        """
        Making layer from PostGIS table.

        Args:
            obj: Instance of a hydrodynamic model object class.

        Returns:
            QgsVectorLayer: QGIS Vector Layer object.
        """
        vl_schema, vl_name = obj.schema, obj.name
        try:     # qgis2
            uri = QgsDataSourceURI()
        except:  # qgis3
            uri = QgsDataSourceUri()

        uri.setConnection(self.host, self.port, self.dbname, self.user, self.password)
        if obj.geom_type is not None:
            uri.setDataSource(vl_schema, vl_name, 'geom')
        else:
            uri.setDataSource(vl_schema, vl_name, None)
        vlayer = QgsVectorLayer(uri.uri(), vl_name, 'postgres')
        return vlayer
#
    def add_vlayer(self, vlayer):
        """
        Handling adding layer process to QGIS view.

        Args:
            vlayer (QgsVectorLayer): QgsVectorLayer object.
        """
        try:
            style_file = os.path.join(self.mgis.masplugPath,'db', 'styles', '{0}.qml'.format(vlayer.name()))
            if self.group:
                try:     # qgis2
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer, False)
                except:  # qgis3
                    QgsProject.instance().addMapLayer(vlayer, False)
                self.group.addLayer(vlayer)
            else:
                try:     # qgis2
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer)
                except:  # qgis3
                    QgsProject.instance().addMapLayer(vlayer)
            #self.mgis.addInfo('path : {}'.format(style_file))
            # a mettre apres deplacement group pour etre pris en compte
            vlayer.loadNamedStyle(style_file)
        except Exception as e:
            self.mgis.addInfo(repr(e))
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
            self.removeGroup_Layer("Mas_{}".format(self.last_schema))
        self.mgis.addInfo('<br><b>Running Create Layers and Tables...</b>')


        try :
            if self.check_firstModel():
                self.mgis.addInfo(" Shema est {}".format(self.SCHEMA))
                self.create_FirstModel()
            else:
                pass
            chaine = """CREATE SCHEMA {0} AUTHORIZATION postgres;"""
            if self.run_query(chaine.format(self.SCHEMA)) is None:
                return
            else:
                self.mgis.addInfo('<br>Model "{0}" created.'.format(self.SCHEMA))

            #table
            tables = [ maso.scenarios, maso.lateral_inflows, maso.lateral_weirs, maso.extremities,
                      maso.flood_marks, maso.hydraulic_head, maso.outputs,
                      maso.weirs, maso.profiles, maso.topo, maso.branchs,
                      maso.observations, maso.parametres, maso.resultats,maso.runs,maso.laws]

            tables.sort(key=lambda x: x().order)

            for masobj_class in tables:
                try:
                    obj = self.process_masobject(masobj_class, 'pg_create_table')
                    if self.mgis.DEBUG:
                        self.mgis.addInfo('  {0} OK'.format(obj.name))
                except:
                    self.mgis.addInfo('failure!<br>{0}'.format(obj))
            # ajout variable fichier parameter
            # req = """COPY {0}.parametres FROM '{1}' DELIMITER ',' CSV HEADER;"""
            # req = """COPY {0}.parametres FROM '{1}' DELIMITER ',' CSV;"""
            fichparam = os.path.join(dossier, "parametres.csv")
            # self.run_query(req.format(self.SCHEMA, fichparam))
            liste_value = []
            with open(fichparam, 'r') as file:
                for ligne in file:
                    liste_value.append(ligne.split(','))
            listeCol = self.listColumns('parametres')
            var = ",".join(listeCol)
            valeurs = "("
            for k in listeCol:
                valeurs += '%s,'
            valeurs = valeurs[:-1] + ")"

            sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                                'parametres',
                                                                var,
                                                                valeurs)
            self.run_query(sql, many=True, listMany=liste_value)

            #visualization
            self.loadGis_layer()

            self.mgis.addInfo('Model "{0}" completed'.format(self.SCHEMA))

        except Exception as e:
            self.mgis.addInfo("Echec of creation model")
            # self.mgis.addInfo(e)

    def create_FirstModel(self):
        """ 
        To add variable in db for the first model creation
        and to add exemple
        :return: 
        """
        try:
            self.run_query("CREATE EXTENSION postgis;")
            self.disconnect_pg()
            self.connect_pg()

            Listefct=['pg_create_calcul_abscisse',
                      'pg_create_calcul_abscisse_profil',
                    'pg_create_calcul_abscisse_branche']
            for fct in Listefct:
                try:
                    obj = self.process_masobject(maso.calcul_abscisse, fct)
                    if self.mgis.DEBUG:
                        self.mgis.addInfo('  {0} OK'.format(fct))
                    else:
                        pass
                except:
                    if self.mgis.DEBUG:
                        self.mgis.addInfo('failure!<br>{0}'.format(fct))
                    else:
                        pass

        except Exception as e:
            self.disconnect_pg()
            self.mgis.addInfo("Echec of creation First Model")

    def check_firstModel(self):
        """
        Check if first model
        :return: bool
        """
        qry = "SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname != 'information_schema' ORDER BY nspname"
        model= self.run_query(qry, fetch=True)
        if len(model)>1:
            return False
        else:
            return True

    def listeModels(self):
        liste = []
        try :
                sql = """SELECT schema_name FROM information_schema.schemata"""
                rows= self.run_query(sql, fetch=True)
                exclusion = ["pg_toast",
                             "pg_temp_1",
                             "pg_toast_temp_1",
                             "pg_catalog",
                             "public",
                             "information_schema"]
                for row in rows:
                    if row[0] not in exclusion and row[0][:3] != "pg_":
                        liste.append('{}'.format(row[0]))

        except Exception as e:
            self.mgis.addInfo("Problem : to show model list")
            self.mgis.addInfo(repr(e))

        return (liste)

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
            self.mgis.addInfo('<br>Model "{0}" deleted.'.format(model_name))

    def loadGis_layer(self):
        """ layer visualization in qgis"""
        # visualisation

        root = QgsProject.instance().layerTreeRoot()

        self.group = root.findGroup("Mas_{}".format(self.SCHEMA))
        if not self.group:
            self.group = root.addGroup("Mas_{}".format(self.SCHEMA))

        tables = list(self.register.items())
        # tables.sort(key=lambda x: x[1].order, reverse=True)
        tables.sort(key=lambda x: x[1].order)
        for (name, obj) in tables:
            try:
                if obj.order < 12:
                    self.add_to_view(obj)
                    if self.mgis.DEBUG:
                        self.mgis.addInfo(' View {0} : OK'.format(obj.name))
                else:
                    pass
            except:
                self.mgis.addInfo('View failure!<br>{0}'.format(obj))
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

    def loadModel(self):
        """ Load model"""
        self.register.clear()
        if self.last_schema:
            self.removeGroup_Layer("Mas_{}".format(self.last_schema))
        self.mgis.addInfo('Current DB schema is: {0}'.format(self.SCHEMA))
        # crée index spatial si non existant
        self.create_spatial_index()
        self.register_existing(maso)
        reg = [self.register[k].name for k in sorted(self.register.keys())]
        if self.mgis.DEBUG:
            self.mgis.addInfo('Objects registered in the database:<br>  {0}'.format('<br>  '.join(reg)))
            self.mgis.addInfo('You can load them now using  Geometry > Load Mascaret Database Tables Into QGIS')
        else:
            if reg:
                self.mgis.addInfo('There are some objects registered in the database.')
            else:
                self.mgis.addInfo('Mascaret database is empty.<br>Create or import your river network data.')
        #
        self.loadGis_layer()

    def removeGroup_Layer(self, name):
        root = QgsProject.instance().layerTreeRoot()
        group1 = root.findGroup(name)
        if not group1 is None:
            for child in group1.children():
                dump = child.dump()
                id = dump.split("=")[-1].strip()
                try :    # qgis2
                    QgsMapLayerRegistry.instance().removeMapLayer(id)
                except:  # qgis3
                    QgsProject.instance().removeMapLayer(id)
            root.removeChildNode(group1)

    def projection(self, nom, listeX, listeG):
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
                                         ",".join(map(str, listeG))),
                              fetch=True)

        for gid, x in rows:
            if gid in listeG:
                i = listeG.index(gid)
                listeX[i] = x

        return (listeX)

    # PRBOLEM DESRIPTION
    def select(self, table, where="", order=""):
        """ Select variables of table"""
        if where:
            where = " WHERE " + where + " "
        if order:
            order = " ORDER BY " + order

        sql = "SELECT * FROM {0}.{1} {2} {3};"
        (results,namCol) = self.run_query(sql.format(self.SCHEMA, table, where, order), fetch=True,namvar=True)
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
    def selectOne(self, table, where="", order=""):
        """select one variable"""

        if where:
            where = " WHERE " + where + " "
        if order:
            order = " ORDER BY " + order

        sql = "SELECT * FROM {0}.{1} {2} {3};"
        # self.mgis.addInfo(sql.format(self.SCHEMA, table, where, order))
        (results, namCol) = self.run_query(sql.format(self.SCHEMA, table, where, order),
                                           fetch=True,arraysize=1,namvar=True)

        cols = [col[0] for col in namCol]
        results= [col[0] for col in results]

        dico = {}
        # self.mgis.addInfo("{0} {1}".format(results[0],cols))
        for i, val in enumerate(results[0]):
            # self.mgis.addInfo("{0}  {1}".format(cols[i],val))
            dico[cols[i]] = val

        return dico
    #
    def selectDistinct(self, var, table, where=""):
        """select the "where" variable which is multiple"""
        if where:
            where = "WHERE " + where
        sql = "SELECT DISTINCT {0} FROM {1}.{2} {3} ORDER BY {0};"
        (results, namCol) = self.run_query(sql.format(var, self.SCHEMA, table, where), fetch=True,namvar=True)
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
        return(dico)
    #
    def selectMax(self, var, table, where):
        """select the max in the table for the "where" variable"""

        sql = "SELECT MAX({0}) FROM {1}.{2} WHERE {3};"
        results = self.run_query(sql.format(var, self.SCHEMA, table, where), fetch=True,arraysize=1)
        #results obj: generator
        for row in results:
            var=row[0][0]
        return (var)

    def delete(self, table, where=None) :
        """ Delete table information"""
        if where :
            where = "WHERE {0}".format(where)
        sql = "DELETE FROM {0}.{1} {2} ;".format(self.SCHEMA,table,where)
        self.run_query(sql)
        # if self.mgis.DEBUG:
        #     self.mgis.addInfo('function delete end')

    def insert(self, table, tab, colonnes, delim=" "):

        var = ",".join(colonnes)

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
        #     self.mgis.addInfo('function insert end')

    def insert2(self, table, tab):
        """ insert table in tableSQl"""
        colonnes = sorted(tab.keys())
        var = ','.join(colonnes)

        valeurs = ""
        for i in range(len(tab[colonnes[0]])):
            valeurs += "("
            for k in colonnes:
                valeurs += str(tab[k][i]) + ","
            valeurs = valeurs[:-1] + "),"

        valeurs = valeurs[:-1]
        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                            table,
                                                            var,
                                                            valeurs)
        self.run_query(sql)
        # if self.mgis.DEBUG:
        #     self.mgis.addInfo('function insert2 end')

    def insertRes(self, table, liste_value, colonnes):
        var = ",".join(colonnes)
        valeurs = "("
        for k in colonnes:
            valeurs+='%s,'
        valeurs = valeurs[:-1] + ")"


        sql = "INSERT INTO {0}.{1}({2}) VALUES {3};".format(self.SCHEMA,
                                                            table,
                                                            var,
                                                            valeurs)
        self.run_query(sql, many=True, listMany=liste_value)

    def update(self, table, tab, var="nom"):
        """update info"""
        for nom, t in tab.items():
            tabVar = []
            for k, v in tab[nom].items():
                if not v:
                    tabVar.append("{0}=NULL".format(k))
                elif isinstance(v, str):
                    tabVar.append("{0}='{1}'".format(k, v))
                elif isinstance(v, list):
                    tabVar.append("{0}='{1}'".format(k, " ".join(map(str, v))))
                else:
                    tabVar.append("{0}={1}".format(k, v))

            sql = """UPDATE {0}.{1} SET {2}  WHERE {3}='{4}'"""

            self.run_query(sql.format(self.SCHEMA,
                                   table,
                                   ", ".join(tabVar),
                                   var,
                                   nom))
            if self.mgis.DEBUG:
                self.mgis.addInfo('function update end')

    def copy(self, table, var, fichier):
        """Copy file in sql"""
        sql = """COPY {0}.{1}({2}) FROM '{3}' WITH DELIMITER ',';"""
        self.run_query(sql.format(self.SCHEMA, table, ",".join(var), fichier))

    def listColumns(self, table):
        """ List columns"""
        sql = """SELECT column_name FROM information_schema.columns 
                  WHERE table_schema='{0}' AND table_name='{1}';"""
        rows=self.run_query(sql.format(self.SCHEMA, table),fetch=True)
        liste = [row[0] for row in rows]
        return (liste)

    def addColumns(self, table, colonne):
        """ add columns"""
        sql = """ALTER TABLE {0}.{1} ADD COLUMN {2} double precision;"""
        self.run_query(sql.format(self.SCHEMA, table, colonne))

    def exportSchema(self,file):
        "export schema"
        try:
            exe = os.path.join(self.mgis.postgres_path, 'pg_dump')

            if os.path.isfile(exe) or  os.path.isfile(exe+'.exe'):
                commande = '"{0}" -n {1} -U {2} -f"{3}" -d {4} -h {5}'.format(exe, self.SCHEMA, self.user, file,
                                                                  self.dbname, self.host)
                os.putenv("PGPASSWORD","{0}".format(self.password))
                p = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                     , stdin=subprocess.PIPE)
                p.wait()
                return True
            else:
                self.mgis.addInfo('Executable file not found. '
                                  'Please, insert path in "path postgres" in Help / Setting / Options')
                return False

        except:
            return False

    def importSchema(self,Listfile):
        # """import schema"""
        try:
            if self.check_firstModel():
                self.mgis.addInfo(" Shema est {}".format(self.SCHEMA))
                self.create_FirstModel()
            else:
                pass
            exe=os.path.join(self.mgis.postgres_path, 'psql')
            if os.path.isfile(exe) or  os.path.isfile(exe + '.exe'):
                # d = dict(os.environ)
                # d["PGPASSWORD"] = "{0}".format(self.password)
                os.putenv("PGPASSWORD", "{0}".format(self.password))

                for file in Listfile:
                    commande = '"{0}" -U {1} -f "{2}" -d {3} -h {4}'.format(exe,  self.user,
                                                                file,self.dbname, self.host)

                    # p = subprocess.Popen(commande, env=d, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    #                      , stdin=subprocess.PIPE)
                    p = subprocess.Popen(commande, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                         , stdin=subprocess.PIPE)
                    p.wait()
                    if self.mgis.DEBUG:
                        self.mgis.addInfo("Import File :{0}".format(file))
                        self.mgis.addInfo("{0}".format(p.communicate()[0]))
                return True
            else:
                self.mgis.addInfo('Executable file not found. '
                                  'Please, insert path in "path postgres" in Help / Setting / Options')
                return False
        except:
            return False

