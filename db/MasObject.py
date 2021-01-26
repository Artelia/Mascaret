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


class MasObject(object):
    """
    Class for Mascaret geometry objects processing.
    """
    SCHEMA = None
    SRID = None
    OVERWRITE = None

    def __init__(self):
        self.order = 0
        # self.main = True
        # self.visible = True
        # self.spatial_index = True
        self.schema = self.SCHEMA
        self.srid = self.SRID
        self.overwrite = self.OVERWRITE
        self.name = self.__class__.__name__
        self.geom_type = None
        self.attrs = None

    # def pg_create_table(self, geo_ori=False):
    def pg_create_table(self):
        schema_name = '{0}.{1}'.format(self.schema, self.name)
        attrs = self.pg_geom_attri()
        # if geo_ori:
        #     attrs_ori = self.pg_geom_ori_attri()
        #     attrs += [' '.join(attrs_ori)]
        attrs += [' '.join(field) for field in self.attrs]

        if self.overwrite is True:
            qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {0}(\n\t{1});\n'.format(schema_name, ',\n\t'.join(attrs))
        else:
            qry = 'CREATE TABLE  IF NOT EXISTS {0}\n(\n\t{1}\n)\nWITH(\n\t OIDS=FALSE \n);\n'.format(schema_name,
                                                                                                     ',\n\t'.join(
                                                                                                         attrs))
        # if self.spatial_index is True:
        #     qry += 'SELECT "{0}".create_spatial_index(\'{0}\', \'{1}\');'.format(self.schema, self.name)
        # else:
        #     pass
        qry += 'ALTER TABLE {0}.{1}\n\tOWNER TO postgres;\n'.format(self.schema, self.name)
        return qry

    def pg_geom_attri(self):
        if self.geom_type is not None:
            attrs = ['geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        else:
            attrs = []
        return attrs

    def pg_geom_ori_attri(self):
        if self.geom_type is not None:
            attrs = ['geom_ori geometry({0}, {1})'.format(self.geom_type, self.srid)]
        else:
            attrs = []
        return attrs

    def pg_create_index(self):
        qry = 'CREATE INDEX {1}_geom_idx\n  ON {0}.{1} \n  USING gist \n  (geom);\n'.format(self.schema, self.name)
        return qry

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_point();\n'
        return qry

    def pg_abscisse_profil(self):
        qry = """
    CREATE OR REPLACE FUNCTION {}.abscisse_profil(id_profil integer )
        RETURNS double precision
        LANGUAGE 'plpgsql'
        COST 100.0
        IMMUTABLE NOT LEAKPROOF 
    AS $BODY$
         DECLARE
            long1	double precision;
            long2	double precision;
            g	geometry;
            p	geometry;
            b	integer;
            z	integer;
            d	double precision;
            geom_p geometry;
            abscissa  double precision;
         BEGIN
            EXECUTE 'SELECT geom FROM {0}.profiles WHERE gid = $1' USING id_profil INTO geom_p;
            EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom,$1) FROM  {0}.branchs ORDER BY 4 LIMIT 1' USING geom_p INTO b,z,g,d;
            EXECUTE 'SELECT ST_Length(ST_UNION(geom)) FROM {0}.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2)' USING b,z INTO long1;
            p = (SELECT (ST_DUMP(ST_Intersection(geom_p, g))).geom LIMIT 1);
            long2 = (SELECT (ST_Length(g)*ST_LineLocatePoint(ST_LineMerge(g),p)));
            IF long1 IS NULL THEN
                  long1 = 0;
            END IF;
            abscissa = ROUND((long1+long2)::numeric,2);

            RETURN abscissa;
         END;
    $BODY$; """

        return qry


# *****************************************
class laws(MasObject):
    def __init__(self):
        super(laws, self).__init__()
        self.order = 0
        self.geom_type = None
        self.attrs = [
            ('id', 'serial NOT NULL'),
            ('name', 'character varying(30)'),
            ('starttime', 'timestamp without time zone'),
            ('endtime', 'timestamp without time zone'),
            ('z', 'text'),
            ('type', 'integer'),
            ('flowrate', 'text'),
            ('time', 'text'),
            ('z_upstream', 'text'),
            ('z_downstream', 'text'),
            ('z_lower', 'text'),
            ('z_up', 'text'),
            ('active', ' boolean NOT NULL DEFAULT TRUE'),
            ('CONSTRAINT cle_laws', 'PRIMARY KEY (id)')]


# *****************************************
class events(MasObject):
    def __init__(self):
        super(events, self).__init__()
        self.order = 1
        self.geom_type = None
        self.attrs = [('name', 'character varying(30) NOT NULL'),
                      ('starttime', 'timestamp without time zone'),
                      ('endtime', 'timestamp without time zone'),
                      ('run', 'boolean'),
                      ('CONSTRAINT cle_events', 'PRIMARY KEY (name)')]



# *****************************************
class extremities(MasObject):
    def __init__(self):
        super(extremities, self).__init__()
        self.order = 2
        self.geom_type = 'Point'
        self.attrs = [('gid serial', 'NOT NULL'),
                      ('name character', 'varying(30)'),
                      ('type', 'integer'),
                      ('method', 'text'),
                      ('firstvalue', 'float'),
                      ('abscissa', 'text'),
                      ('ordinates', 'text'),
                      ('angles', 'text'),
                      ('active', ' boolean NOT NULL DEFAULT TRUE'),
                      ('tracer_boundary_condition_type', 'integer'),
                      ('law_wq', 'text'),
                      ('CONSTRAINT cle_extremities', ' PRIMARY KEY (gid)'),
                      ('CONSTRAINT extremities_nom_key', ' UNIQUE (name)')]
        # TODO plante
        # def pg_create_table(self):
        #     qry = super(self.__class__, self).pg_create_table()
        #     qry += '\n'
        #     qry += self.pg_create_index()
        #     qry += '\n'
        #     qry += self.pg_create_calcul_abscisse()
        #     return qry


# *****************************************
class flood_marks(MasObject):
    def __init__(self):
        super(flood_marks, self).__init__()
        self.order = 3
        self.geom_type = 'Point'
        self.attrs = [
            ('gid', 'serial NOT NULL'),
            ('name', 'character varying(30)'),
            ('event', 'character varying(30)'),
            ('branchnum', 'integer'),
            ('date', 'date'),
            ('abscissa', 'float'),
            ('z', 'float'),
            ('validate', 'integer'),
            ('comment', 'text'),
            ('weir', 'float'),
            ('adress', 'text'),
            ('active', ' boolean NOT NULL DEFAULT TRUE'),
            ('township', 'character varying(30)'),
            ('CONSTRAINT flood_marks_pkey', 'PRIMARY KEY(gid)')]

    def pg_clear_tab(self):
        """ create trigger"""
        qry = """
            CREATE TRIGGER flood_marks_delete_point_flood
            AFTER DELETE
            ON {}.{}
            FOR EACH ROW
            EXECUTE PROCEDURE public.delete_point_flood();""".format(self.schema,self.name)
        return qry

    def pg_calcul_abscisse_flood(self):
        """ create trigger"""
        qry = """
        CREATE TRIGGER {1}_calcul_abscisse_flood
        BEFORE INSERT OR UPDATE 
        ON {0}.{1}
        FOR EACH ROW
        EXECUTE PROCEDURE public.calcul_abscisse_point_flood();
        """.format(self.schema,self.name)
        return qry

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_calcul_abscisse_flood()
        qry += '\n'
        qry += self.pg_clear_tab()
        return qry


# *****************************************
class weirs(MasObject):
    def __init__(self):
        super(weirs, self).__init__()
        self.order = 4
        self.geom_type = 'Point'
        self.attrs = [
            ('gid', ' serial NOT NULL'),
            ('name', ' character varying(30)'),
            ('type', ' integer'),
            ('branchnum', ' integer'),
            ('abscissa', ' float'),
            ('z_crest', ' float'),
            ('z_average_crest', ' float'),
            ('z_break', ' float DEFAULT 10000'),
            ('flowratecoeff', ' float'),
            ('thickness', ' integer'),
            ('wide_floodgate', ' float'),
            ('lawfile', ' text'),
            ('active', ' boolean NOT NULL DEFAULT TRUE'),
            ('active_mob', 'boolean NOT NULL DEFAULT FALSE'),
            ('method_mob', 'text'),
            ('CONSTRAINT weirs_pkey', ' PRIMARY KEY(gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class hydraulic_head(MasObject):
    def __init__(self):
        super(hydraulic_head, self).__init__()
        self.order = 5
        self.geom_type = 'Point'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('branchnum', 'integer'),
                      ('abscissa', 'float'),
                      ('coeff', 'float'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT hydraulic_head_pkey', 'PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class lateral_inflows(MasObject):
    def __init__(self):
        super(lateral_inflows, self).__init__()
        self.order = 6
        self.geom_type = 'Point'
        self.attrs = [('gid', ' serial NOT NULL'),
                      ('name', ' character varying(30)'),
                      ('branchnum', ' integer'),
                      ('abscissa', ' float'),
                      ('length', ' float'),
                      ('firstvalue', ' float'),
                      ('method', ' text'),
                      ('active', ' boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT lateral_inflows_pkey', ' PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class lateral_weirs(MasObject):
    def __init__(self):
        super(lateral_weirs, self).__init__()
        self.order = 7
        self.geom_type = 'Point'
        self.attrs = [('gid serial', 'NOT NULL'),
                      ('name character', 'varying(30)'),
                      ('type', 'integer'),
                      ('branchnum', 'integer'),
                      ('abscissa', 'float'),
                      ('length', 'float'),
                      ('z_crest', 'float'),
                      ('flowratecoef', 'float'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT lateral_weir_pkey', 'PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *********** Water quality ***************
class tracer_lateral_inflows(MasObject):
    def __init__(self):
        super(tracer_lateral_inflows, self).__init__()
        self.order = 8
        self.geom_type = 'Point'
        self.attrs = [('gid', ' serial NOT NULL'),
                      ('name', ' character varying(30)'),
                      ('branchnum', ' integer'),
                      ('abscissa', ' float'),
                      ('length', ' float'),
                      ('law_wq', ' text'),
                      ('typeSources', ' integer'),
                      ('active', ' boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT tracer_lateral_inflows_pkey', ' PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class outputs(MasObject):
    def __init__(self):
        super(outputs, self).__init__()
        self.order = 9
        self.geom_type = 'Point'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('code', 'character varying(30)'),
                      ('zero', 'float'),
                      ('branchnum', 'integer'),
                      ('abscissa', 'float'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT outputs_pkey', 'PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class topo(MasObject):
    def __init__(self):
        super(topo, self).__init__()
        self.order = 10
        self.geom_type = 'Point'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('profile', 'character varying(30)'),
                      ('order_', 'integer'),
                      ('x', 'float'),
                      ('z', 'float'),
                      ('CONSTRAINT topo_pkey', 'PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        return qry

        # def pg_geom_attri(self):
        #     if self.geom_type is not None:
        #         attrs = ['geom geometry({0})'.format(self.geom_type)]
        #     else:
        #         attrs = []
        #     return attrs


# *****************************************
class profiles(MasObject):
    def __init__(self):
        super(profiles, self).__init__()
        self.order = 11
        self.geom_type = 'MultiLineString'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('branchnum', 'integer'),
                      ('abscissa', 'float'),
                      ('x', 'text'),
                      ('z', 'text'),
                      ('leftminbed', 'float'),
                      ('rightminbed', 'float'),
                      ('leftstock', 'float'),
                      ('rightstock', 'float'),
                      ('xmnt', 'text'),
                      ('zmnt', 'text'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('struct', 'integer DEFAULT 0'),
                      ('CONSTRAINT profiles_pkey', 'PRIMARY KEY (gid)'),
                      ('CONSTRAINT profile_unique', 'UNIQUE (name)')]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_profil();\n'
        return qry

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class links(MasObject):
    def __init__(self):
        super(links, self).__init__()
        self.order = 12
        self.geom_type = 'MultiLineString'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('linknum', 'serial NOT NULL'),
                      ('type', 'integer'),
                      ('nature', 'integer'),
                      ('level', 'float'),
                      ('length', 'float'),
                      ('width', 'float'),
                      ('roughness', 'float'),
                      ('crosssection', 'float'),
                      ('headlosscoef', 'float'),
                      ('weirdischargecoef', 'float'),
                      ('activationcoef', 'float'),
                      ('pipedischargecoef', 'float'),
                      ('culverttype', 'integer'),
                      ('basinstart', 'integer'),
                      ('basinend', 'integer'),
                      ('branchnum', 'integer'),
                      ('abscissa', 'float'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT links_pkey', 'PRIMARY KEY (gid)'),
                      ('CONSTRAINT link_name_unique', 'UNIQUE (name)'),
                      ('CONSTRAINT link_num_unique', 'UNIQUE (linknum)')]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_profil();\n'
        return qry

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        return qry


# *****************************************
class branchs(MasObject):
    def __init__(self):
        super(branchs, self).__init__()
        self.order = 13
        self.geom_type = 'MultiLineString'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('branch', 'serial NOT NULL'),
                      ('startb', 'character varying(30)'),
                      ('endb', 'character varying(30)'),
                      ('zonenum', 'serial NOT NULL'),
                      ('zoneabsstart', 'float'),
                      ('zoneabsend', 'float'),
                      ('minbedcoef', 'float'),
                      ('majbedcoef', 'float'),
                      ('mesh', 'float'),
                      ('planim', 'float'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT branchs_pkey', 'PRIMARY KEY (gid)'),
                      ('CONSTRAINT cle_debut', 'FOREIGN KEY (startb)\n'
                                               '\t   REFERENCES {0}.extremities (name) MATCH SIMPLE \n'
                                               '\t   ON UPDATE NO ACTION ON DELETE NO ACTION'.format(self.schema)),
                      ('CONSTRAINT cle_fin', 'FOREIGN KEY (startb)'
                                             '\t   REFERENCES {0}.extremities (name) MATCH SIMPLE \n'
                                             '\t   ON UPDATE NO ACTION ON DELETE NO ACTION'.format(self.schema))]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_branche();\n'
        return qry

    def pg_updat_actv(self):
        qry = 'CREATE TRIGGER {1}_chstate_active\n' \
              ' AFTER UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += ' FOR EACH ROW\n' \
               'WHEN (OLD.active IS DISTINCT FROM NEW.active)\n' \
               'EXECUTE PROCEDURE chstate_branch();\n'
        return qry

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_create_calcul_abscisse()
        qry += '\n'
        qry += self.pg_updat_actv()
        return qry


# **************** Basins *************************
class basins(MasObject):
    def __init__(self):
        super(basins, self).__init__()
        self.order = 14
        self.geom_type = 'MultiPolygon'
        self.attrs = [('gid', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('basinnum', 'serial NOT NULL'),
                      ('initlevel', 'float'),
                      ('level', 'text'),
                      ('area', 'text'),
                      ('volume', 'text'),
                      ('active', 'boolean NOT NULL DEFAULT TRUE'),
                      ('CONSTRAINT basins_pkey', 'PRIMARY KEY (gid)'),
                      ('CONSTRAINT basin_name_unique', 'UNIQUE (name)'),
                      ('CONSTRAINT basin_num_unique', 'UNIQUE (basinnum)')]

    def pg_updat_actv(self):
        qry = 'CREATE TRIGGER {1}_chstate_active\n' \
              ' AFTER UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += ' FOR EACH ROW\n' \
               'WHEN (OLD.active IS DISTINCT FROM NEW.active)\n' \
               'EXECUTE PROCEDURE chstate_basin();\n'
        return qry

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        qry += self.pg_updat_actv()
        return qry

class visu_flood_marks(MasObject):
    def __init__(self):
        super(visu_flood_marks, self).__init__()
        self.order = 15
        self.geom_type = 'LineString'
        self.attrs = [
            ('gid', 'serial NOT NULL'),
            ('id_marks', 'integer'),
            ('CONSTRAINT visu_flood_marks_pkey', 'PRIMARY KEY(gid,id_marks)')]


    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += self.pg_create_index()
        qry += '\n'
        return qry

# *******************************************
# ******************************************
# *****************************************
class observations(MasObject):
    def __init__(self):
        super(observations, self).__init__()
        self.order = 16
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('code', 'character(10)'),
                      ('type', 'character(1)'),
                      ('comment', 'character varying(50)'),
                      ('valeur', 'float'),
                      ('date', 'timestamp without time zone'),
                      ('CONSTRAINT cle_obs ', 'PRIMARY KEY (id)')]




class resultats(MasObject):
    def __init__(self):
        super(resultats, self).__init__()
        self.order = 17
        self.geom_type = None
        self.attrs = [('id', ' serial NOT NULL'),
                      ('run', ' character varying(30)'),
                      ('scenario', ' character varying(30)'),
                      ('date', ' timestamp without time zone'),
                      ('t', ' float'),
                      ('branche', ' integer'),
                      ('section', ' integer'),
                      ('pk', ' float'),
                      ('zref', ' float'),
                      ('z', ' float'),
                      ('qmin', ' float'),
                      ('qmaj', ' float'),
                      ('kmin', ' float'),
                      ('kmaj', ' float'),
                      ('fr', ' float'),
                      ('y', ' float'),
                      ('zmax', ' float'),
                      ('qmax', ' float'),
                      ('q', ' float'),
                      ('bnum', ' integer'),
                      ('zcas', ' float'),
                      ('surcas', ' float'),
                      ('volcas', ' float'),
                      ('lnum', ' integer'),
                      ('qech', ' float'),
                      ('vech', ' float'),
                      ('CONSTRAINT projet_pkey', ' PRIMARY KEY (id)')]


class resultats_basin(MasObject):
    def __init__(self):
        super(resultats_basin, self).__init__()
        self.order = 18
        self.geom_type = None
        self.attrs = [('id', ' serial NOT NULL'),
                      ('run', ' character varying(30)'),
                      ('scenario', ' character varying(30)'),
                      ('date', ' timestamp without time zone'),
                      ('t', ' float'),
                      ('bnum', ' integer'),
                      ('zcas', ' float'),
                      ('surcas', ' float'),
                      ('volcas', ' float'),
                      ('CONSTRAINT res_basinkey', ' PRIMARY KEY (id)')]


class resultats_links(MasObject):
    def __init__(self):
        super(resultats_links, self).__init__()
        self.order = 19
        self.geom_type = None
        self.attrs = [('id', ' serial NOT NULL'),
                      ('run', ' character varying(30)'),
                      ('scenario', ' character varying(30)'),
                      ('date', ' timestamp without time zone'),
                      ('t', ' float'),
                      ('lnum', ' integer'),
                      ('qech', ' float'),
                      ('vech', ' float'),
                      ('CONSTRAINT res_linkkey', ' PRIMARY KEY (id)')]


# *****************************************
class runs(MasObject):
    def __init__(self):
        super(runs, self).__init__()
        self.order = 20
        self.geom_type = None
        self.attrs = [('id serial', 'NOT NULL'),
                      ('run', 'character varying(30)'),
                      ('scenario', 'character varying(30)'),
                      ('date', ' timestamp without time zone'),
                      ('init_date', 'timestamp without time zone'),
                      ('t', ' text'),
                      ('pk', ' text'),
                      ('comments', 'text'),
                      ('wq', 'text'),
                      ('CONSTRAINT cle_runs', 'PRIMARY KEY (id)')]


# *****************************************
class parametres(MasObject):
    def __init__(self):
        super(parametres, self).__init__()
        self.order = 21
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('parametre', 'text'),
                      ('steady', 'text'),
                      ('unsteady', 'text'),
                      ('transcritical', 'text'),
                      ('libelle', 'text'),
                      ('balise1', 'text'),
                      ('balise2', 'text'),
                      ('gui', 'text'),
                      ('gui_type', 'text'),
                      ('CONSTRAINT cle_param', 'PRIMARY KEY (id)')]


# *****************************************
class class_fct_psql(MasObject):
    def __init__(self):
        super(class_fct_psql, self).__init__()
        self.order = 22

    def pg_create_calcul_abscisse(self):
        qry = """CREATE OR REPLACE FUNCTION {0}()  
            RETURNS trigger AS  
            $BODY$ 
            DECLARE  
                long1	double precision; 
                long2	double precision;  
                g	geometry; 
                b	integer; 
                z	integer; 
                d	double precision; 
                f	double precision;
                val	boolean;           
             
                BEGIN 
                IF NEW.geom IS NULL AND NEW.abscissa IS NOT NULL AND NEW.branchnum IS NOT NULL THEN
                    EXECUTE '(SELECT ST_UNION(geom) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch=$1))' USING NEW.branchnum INTO g;
                    NEW.geom = (SELECT ST_LineInterpolatePoint(ST_LineMerge(g),NEW.abscissa/ST_Length(g)));
                ELSE
                    EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom, $1) FROM ' || TG_TABLE_SCHEMA || '.branchs ORDER BY 4 LIMIT 1' USING NEW.geom INTO b,z,g,d  ;

                    IF TG_OP='INSERT' OR NEW.branchnum IS NULL OR NOT ST_Equals(NEW.geom,OLD.geom) THEN
                        NEW.branchnum= b ;
                    END IF;

                        
                    IF TG_OP='INSERT' OR NEW.abscissa IS NULL OR NOT ST_Equals(NEW.geom,OLD.geom) THEN
                       EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2))' USING b,z INTO long1;
                       f = (SELECT ST_LineLocatePoint(ST_LineMerge(g),NEW.geom));
                       NEW.geom = (SELECT ST_LineInterpolatePoint(ST_LineMerge(g),f));
                       long2 = (SELECT (ST_Length(g)*f));
                        
                       IF long1 IS NULL THEN
                           long1 = 0;
                       END IF;
                        
                       NEW.abscissa = ROUND((long1+long2)::numeric,2);

                    END IF;

                    
                END IF;                   
                        
                RETURN NEW;
            END; 
             
            $BODY$ 
              LANGUAGE plpgsql IMMUTABLE 
              COST 100; 
            ALTER FUNCTION {0}() 
              OWNER TO postgres;"""

        return qry.format('calcul_abscisse_point')

    def pg_create_calcul_abscisse_profil(self):
        qry = """CREATE OR REPLACE FUNCTION {0}()
                  RETURNS trigger AS
                $BODY$
                DECLARE
                    long1	double precision;
                    long2	double precision;
                    g	geometry;
                    p	geometry;
                    b	integer;
                    z	integer;
                    d	double precision;
                    BEGIN
                    
                    EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom,$1) FROM ' || TG_TABLE_SCHEMA ||'.branchs ORDER BY 4 LIMIT 1' USING NEW.geom INTO b,z,g,d;

                    IF TG_OP='INSERT' OR NEW.branchnum IS NULL OR NOT ST_Equals(NEW.geom,OLD.geom) THEN
                    NEW.branchnum=b;
                    END IF;

                    
                    IF TG_OP='INSERT' OR NEW.abscissa IS NULL OR NOT ST_Equals(NEW.geom,OLD.geom) THEN
                        EXECUTE 'SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA ||'.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2)' USING b,z INTO long1;
                        p = (SELECT (ST_DUMP(ST_Intersection(NEW.geom, g))).geom LIMIT 1);
                        long2 = (SELECT (ST_Length(g)*ST_LineLocatePoint(ST_LineMerge(g),p)));
                        
                        IF long1 IS NULL THEN
                            long1 = 0;
                        END IF;
                        
                        NEW.abscissa = ROUND((long1+long2)::numeric,2);

                    END IF;
                        
                        RETURN NEW;
                    END;

                $BODY$
                  LANGUAGE plpgsql IMMUTABLE
                  COST 100;
                ALTER FUNCTION {0}()
                  OWNER TO postgres;"""
        return qry.format('calcul_abscisse_profil')

    def pg_create_calcul_abscisse_branche(self):
        qry = '''CREATE OR REPLACE FUNCTION calcul_abscisse_branche()
              RETURNS trigger AS
            $BODY$
            DECLARE
                long1	float; 
                long2	float; 
            BEGIN 
         
                EXECUTE 'SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2)' USING NEW.branch,NEW.zonenum INTO long1; 
                long2 = (SELECT ST_Length(NEW.geom)); 
             
                IF long1 IS NULL THEN 
                    long1 = 0; 
                END IF; 
            
                NEW.zoneabsstart = ROUND(long1::numeric,1);
                NEW.zoneabsend = ROUND((long1+long2)::numeric,1);
            
                RETURN NEW;
            END;
            
            $BODY$
              LANGUAGE plpgsql IMMUTABLE
              COST 100;
            ALTER FUNCTION calcul_abscisse_branche()
              OWNER TO postgres;
'''
        return qry

    def pg_chstate_branch(self):
        qry = """
CREATE  OR REPLACE FUNCTION public.chstate_branch() RETURNS TRIGGER AS $$
    DECLARE
         my_row  integer; 
    BEGIN 
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.profiles SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.flood_marks SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.weirs SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.hydraulic_head SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.lateral_inflows SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.lateral_weirs SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.tracer_lateral_inflows SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.outputs SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.branchs SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
         FOR my_row IN EXECUTE 'SELECT gid FROM ' || TG_TABLE_SCHEMA || '.branchs  WHERE branch = $1 AND gid !=$2 AND active != $3 ' USING NEW.branch,NEW.gid,NEW.active
         LOOP 
            EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.branchs SET active = $2 WHERE (gid = $1)' USING my_row,NEW.active;
         END LOOP;
         RETURN NEW;
    END;
$$ LANGUAGE plpgsql;"""
        return qry

        # DROP TRIGGER IF EXISTS branch_chstate_active ON ouvrage3.branchs

    def pg_chstate_basin(self):
        qry = """
CREATE  OR REPLACE FUNCTION public.chstate_basin() RETURNS TRIGGER AS $$
    BEGIN 
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.links SET active = $2 WHERE (basinstart = $1 OR basinend = $1)' USING NEW.basinnum,NEW.active;
         RETURN NEW;
    END;
$$ LANGUAGE plpgsql;"""
        return qry

    def pg_abscisse_profil(self):
        """
        SQL function which computes the profiles abscissa
        :return:
        """
        qry = """
    CREATE OR REPLACE FUNCTION public.abscisse_profil(_tbl regclass, _tbl_branchs regclass, id_prof integer)
        RETURNS double precision
        LANGUAGE 'plpgsql'
    AS $BODY$
         DECLARE
            long1	double precision;
            long2	double precision;
            g	geometry;
            p	geometry;
            b	integer;
            z	integer;
            d	double precision;
            geom_p geometry;
            abscissa  double precision;
         BEGIN
            EXECUTE 'SELECT geom FROM  ' || _tbl || ' WHERE gid = $1' USING id_prof INTO geom_p;
            EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom, $1) FROM ' || _tbl_branchs || ' ORDER BY 4 LIMIT 1' USING geom_p INTO b,z,g,d  ;
            EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM  ' || _tbl_branchs || ' WHERE (branch<$1) OR (branch=$1 AND zonenum<$2))' USING b,z INTO long1;
            p = (SELECT (ST_DUMP(ST_Intersection(geom_p, g))).geom LIMIT 1);
            long2 = (SELECT (ST_Length(g)*ST_LineLocatePoint(ST_LineMerge(g),p)));
            IF long1 IS NULL THEN
                  long1 = 0;
            END IF;
            abscissa = ROUND((long1+long2)::numeric,2);

            RETURN abscissa;
         END;
    $BODY$; """

        return qry

    def pg_all_profil(self):
        """ SQL function which updates abscissa of all profiles of one table"""
        qry = """
CREATE OR REPLACE FUNCTION public.update_abscisse_profil(_tbl regclass, _tbl_branchs regclass)
    RETURNS  VOID 
    LANGUAGE 'plpgsql'
AS $BODY$
     DECLARE
        my_row  integer;     
        abs1 double precision;
     BEGIN
       FOR my_row IN  EXECUTE 'SELECT gid FROM ' ||_tbl
       LOOP
          SELECT public.abscisse_profil( _tbl ,_tbl_branchs, my_row ) INTO abs1;
          EXECUTE 'UPDATE  '||_tbl || ' SET abscissa = $1 WHERE gid = $2' USING abs1, my_row;
        END LOOP;
        RETURN  ;
     END;
$BODY$;"""
        return qry

    def pg_abscisse_point(self):
        """
         SQL function which computes the points abscissa
        :return:
        """
        qry = """
    CREATE OR REPLACE FUNCTION public.abscisse_point(_tbl regclass, _tbl_branchs regclass, id_point integer)
    RETURNS double precision
    LANGUAGE 'plpgsql'
AS $BODY$
 
     DECLARE  
        long1	double precision; 
        long2	double precision;  
        g	geometry; 
        b	integer; 
        z	integer; 
        d	double precision; 
        f	double precision;
        abscissa double precision;          
        geom_p  geometry;    

     BEGIN
         EXECUTE 'SELECT geom FROM  ' || _tbl || ' WHERE gid = $1' USING id_point INTO geom_p;
         EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom, $1) FROM ' || _tbl_branchs || ' ORDER BY 4 LIMIT 1' USING geom_p INTO b,z,g,d  ;
         EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM  ' || _tbl_branchs || ' WHERE (branch<$1) OR (branch=$1 AND zonenum<$2))' USING b,z INTO long1;
         f = (SELECT ST_LineLocatePoint(ST_LineMerge(g),geom_p));
         long2 = (SELECT (ST_Length(g)*f));
         IF long1 IS NULL THEN
             long1 = 0;
         END IF;
         abscissa =     ROUND((long1+long2)::numeric,2);        
                   
        RETURN abscissa;
     END;      
$BODY$;"""
        return qry

    def pg_all_point(self):
        """
         SQL function which updates abscissa of all point of one table
        :return:
        """
        qry = """
    CREATE OR REPLACE FUNCTION  public.update_abscisse_point(_tbl regclass, _tbl_branchs regclass)
        RETURNS  VOID 
        LANGUAGE 'plpgsql'
    AS $BODY$
         DECLARE
            my_row  integer;     
            abs1 double precision;
         BEGIN
          FOR my_row IN  EXECUTE 'SELECT gid FROM ' ||_tbl
           LOOP
             SELECT public.abscisse_point( _tbl ,_tbl_branchs, my_row ) INTO abs1;
             EXECUTE 'UPDATE  '||_tbl || ' SET abscissa = $1 WHERE gid = $2' USING abs1, my_row;
            END LOOP;
            RETURN  ;
         END;
    $BODY$;"""
        return qry

    def pg_abscisse_branch(self):
        """
          SQL function which computes the branch abscissa
        :return:
        """
        qry="""
CREATE OR REPLACE FUNCTION public.abscisse_branch(
	_tbl_branchs regclass,
	id_branch integer)
    RETURNS TABLE (zoneabsstart float, zoneabsend float) 
    LANGUAGE 'plpgsql'
AS $BODY$

    DECLARE
        long1	float; 
        long2	float; 
        geom_b  geometry;
        branch integer;
        zonenum integer;      
    BEGIN 
        EXECUTE 'SELECT geom,zonenum,branch FROM  ' || _tbl_branchs || ' WHERE gid = $1' USING id_branch INTO geom_b, branch,zonenum;
        EXECUTE 'SELECT ST_Length(ST_UNION(geom)) FROM ' || _tbl_branchs || ' WHERE (branch<$1) OR (branch=$1 AND zonenum<$2)' USING branch,zonenum INTO long1; 
        long2 = (SELECT ST_Length(geom_b)); 
        IF long1 IS NULL THEN 
            long1 = 0; 
        END IF; 
        zoneabsstart := ROUND(long1::numeric,1);
        zoneabsend := ROUND((long1+long2)::numeric,1);     
      	RETURN NEXT ;
    END;
                  
$BODY$;"""
        return qry

    def pg_all_branch(self):
        """
         SQL function which updates abscissa of all branchs of one table
        :return:
        """
        qry = """
CREATE OR REPLACE FUNCTION public.update_abscisse_branch(
	_tbl_branchs regclass)
    RETURNS void
    LANGUAGE 'plpgsql'
AS $BODY$

     DECLARE
        my_row  integer;     
        abs1 float;
        abs2 float;
     BEGIN
       FOR my_row IN  EXECUTE 'SELECT gid FROM '||_tbl_branchs
       LOOP
          SELECT * FROM public.abscisse_branch( _tbl_branchs, my_row ) into abs1,abs2;        
          EXECUTE 'UPDATE  '||_tbl_branchs || ' SET zoneabsstart = $1, zoneabsend = $2 WHERE gid = $2' 
          USING  abs1, abs2,my_row;
        END LOOP;
        RETURN  ;
     END;

$BODY$;"""
        return qry

    def pg_delete_visu_flood_marks(self):
        """
         SQL function which delete visu_flood_marks
        :return:
        """
        qry = """
        
        CREATE OR REPLACE FUNCTION public.delete_point_flood()
            RETURNS trigger
            LANGUAGE 'plpgsql'
            COST 100.0
        
        AS $BODY$
         DECLARE 
         test boolean;
         BEGIN 
        
          EXECUTE 'SELECT EXISTS(SELECT 1 from ' || TG_TABLE_SCHEMA || '.visu_flood_marks where  id_marks =$1 )' USING OLD.gid into test ;     			
          IF (test) THEN
            EXECUTE 'DELETE FROM ' || TG_TABLE_SCHEMA || '.visu_flood_marks WHERE id_marks = $1' USING OLD.gid;
          END IF;
          RETURN NEW;
        
        
         END
        $BODY$;
        """
        return qry

    def pg_create_calcul_abscisse_point_flood(self):
        qry = """
        CREATE OR REPLACE FUNCTION public.calcul_abscisse_point_flood()
        RETURNS trigger
        
        LANGUAGE 'plpgsql'
        COST 100.0
        
        AS $BODY$
 
            DECLARE  
                long1	double precision; 
                long2	double precision;  
                g	geometry; 
                b	integer; 
                z	integer; 
                d	double precision; 
                f	double precision;
                test	boolean;       
                new_line  geometry;
                geom_final_p geometry;
                srid integer;
                
             
                BEGIN 
              
                IF NEW.geom IS NULL AND NEW.abscissa IS NOT NULL AND NEW.branchnum IS NOT NULL THEN
         
                    EXECUTE 'SELECT ST_UNION(geom) FROM  ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch = $1)' USING NEW.branchnum INTO g;
                    geom_final_p = (SELECT ST_LineInterpolatePoint(ST_LineMerge(g),NEW.abscissa/ST_Length(g)));
                    NEW.geom = geom_final_p;
                    SELECT ST_SRID(g) INTO srid;                     
                                       
					EXECUTE 'SELECT ST_AsText( ST_MakeLine($1, $2))' USING geom_final_p,NEW.geom INTO new_line;
                    EXECUTE 'SELECT EXISTS(SELECT 1 from ' || TG_TABLE_SCHEMA || '.visu_flood_marks where  id_marks =$1 )' USING NEW.gid into test ;
          			
  				    IF (test) THEN
                   		EXECUTE 'UPDATE  ' || TG_TABLE_SCHEMA || '.visu_flood_marks  SET geom=ST_SetSRID($1,$2) WHERE id_marks = $3' USING new_line, srid,NEW.gid;
                    ELSE
                    	EXECUTE 'INSERT INTO ' || TG_TABLE_SCHEMA || '.visu_flood_marks (geom,gid, id_marks) VALUES( ST_SetSRID($1,$2),DEFAULT,$3)' USING new_line, srid,NEW.gid ;
        			END IF;
                   	
                ELSE
                    EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom, $1) FROM ' || TG_TABLE_SCHEMA || '.branchs ORDER BY 4 LIMIT 1' USING NEW.geom INTO b,z,g,d  ;

                    IF TG_OP='INSERT' OR NEW.branchnum IS NULL OR NOT ST_Equals(geom_final_p,OLD.geom) THEN
                        NEW.branchnum= b ;
                    END IF;

                        
                    IF TG_OP='INSERT' OR NEW.abscissa IS NULL OR NOT ST_Equals(NEW.geom,OLD.geom) THEN
                        /* projection compute*/
                       EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2))' USING b,z INTO long1;
                       f = (SELECT ST_LineLocatePoint(ST_LineMerge(g),NEW.geom));
                       geom_final_p = (SELECT ST_LineInterpolatePoint(ST_LineMerge(g),f));
                        /* get srid value*/
                       SELECT ST_SRID(g) INTO srid; 
                        /* create line*/
                       EXECUTE 'SELECT ST_AsText( ST_MakeLine($1, $2))' USING geom_final_p,NEW.geom INTO new_line;
                        /* change visu_flood_marks*/
                       EXECUTE 'SELECT EXISTS(SELECT 1 from ' || TG_TABLE_SCHEMA || '.visu_flood_marks where  id_marks =$1 )' USING NEW.gid into test ;
                       IF  test THEN
                           EXECUTE 'UPDATE  ' || TG_TABLE_SCHEMA || '.visu_flood_marks  SET geom=ST_SetSRID($1,$2) WHERE id_marks = $3' USING new_line, srid,NEW.gid ;
                       ELSE
                    	   EXECUTE 'INSERT INTO ' || TG_TABLE_SCHEMA || '.visu_flood_marks (geom,gid, id_marks) VALUES( ST_SetSRID($1,$2),DEFAULT,$3)' USING new_line, srid,NEW.gid ;
        			   END IF;
                       
                       long2 = (SELECT (ST_Length(g)*f));
                        
                       IF long1 IS NULL THEN
                           long1 = 0;
                       END IF;
                        
                       NEW.abscissa = ROUND((long1+long2)::numeric,2);
                    ELSE
                        IF NOT OLD.branchnum = NEW.branchnum THEN
                            NEW.branchnum= b ;
                        END IF;
                         
                        IF NOT  OLD.abscissa=  NEW.abscissa THEN
                            EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2))' USING b,z INTO long1;
                            IF (NEW.abscissa-long1)/ST_Length(g)>1THEN
                            	RAISE NOTICE 'Branch : %, Zone : %',b,z;
                            	RAISE NOTICE 'The new abscissa (%) is not between % and % ;', NEW.abscissa, long1, long1+ST_Length(g);
                            END IF ;    
                           
                            geom_final_p = (SELECT ST_LineInterpolatePoint(ST_LineMerge(g),(NEW.abscissa-long1)/ST_Length(g)));
                            
                            SELECT ST_SRID(g) INTO srid;                     
                            EXECUTE 'SELECT ST_AsText( ST_MakeLine($1, $2))' USING geom_final_p,NEW.geom INTO new_line;
                            EXECUTE 'SELECT EXISTS(SELECT 1 from ' || TG_TABLE_SCHEMA || '.visu_flood_marks where  id_marks =$1 )' USING NEW.gid into test ;
                            IF (test) THEN
                                EXECUTE 'UPDATE  ' || TG_TABLE_SCHEMA || '.visu_flood_marks  SET geom=ST_SetSRID($1,$2) WHERE id_marks = $3' USING new_line, srid,NEW.gid;
                            ELSE
                                EXECUTE 'INSERT INTO ' || TG_TABLE_SCHEMA || '.visu_flood_marks (geom,gid, id_marks) VALUES( ST_SetSRID($1,$2),DEFAULT,$3)' USING new_line, srid,NEW.gid ;
                            END IF;
                        END IF;
                        
                    END IF;

                END IF;                  
                        
               RETURN NEW;

            END;   
        $BODY$;
              """
        return qry

# *****************************************
class laws_wq(MasObject):
    def __init__(self):
        super(laws_wq, self).__init__()
        self.order = 23
        self.geom_type = None
        self.attrs = [
            ('id_config', 'integer'),
            ('id_trac', 'integer'),
            ('time', 'float'),
            ('value', 'float'),
            ('active', 'boolean'),
            ('CONSTRAINT cle_laws_wq', 'PRIMARY KEY (id_config, id_trac, time)')]


# *****************************************

class tracer_physic(MasObject):
    def __init__(self):
        super(tracer_physic, self).__init__()
        self.order = 24
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('type', 'text'),
                      ('sigle', 'text'),
                      ('value', 'text'),
                      ('text', 'text'),
                      ('textfr', 'text'),
                      ('CONSTRAINT cle_tr_phy', 'PRIMARY KEY (id)')]


class tracer_name(MasObject):
    def __init__(self):
        super(tracer_name, self).__init__()
        self.order = 25
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('type', 'text'),
                      ('sigle', 'text'),
                      ('text', 'text'),
                      ('textfr', 'text'),
                      ('convec', 'boolean'),
                      ('diffu', 'boolean'),
                      ('CONSTRAINT cle_tr_name', 'PRIMARY KEY (id)')]


class tracer_config(MasObject):
    def __init__(self):
        super(tracer_config, self).__init__()
        self.order = 26
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('type', 'integer'),
                      ('CONSTRAINT cle_tr_conf', 'PRIMARY KEY (id)')]


class meteo_config(MasObject):
    def __init__(self):
        super(meteo_config, self).__init__()
        self.order = 27
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('starttime', 'timestamp without time zone'),
                      ('active', 'boolean'),
                      ('CONSTRAINT cle_met_conf', 'PRIMARY KEY (id)')]


class laws_meteo(MasObject):
    def __init__(self):
        super(laws_meteo, self).__init__()
        self.order = 28
        self.geom_type = None
        self.attrs = [
            ('id_config', 'integer'),
            ('id_var', 'integer'),
            ('time', 'float'),
            ('value', 'float'),
            ('CONSTRAINT cle_laws_met', 'PRIMARY KEY (id_config, id_var, time)')]


class init_conc_config(MasObject):
    def __init__(self):
        super(init_conc_config, self).__init__()
        self.order = 29
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('type', 'integer'),
                      ('active', ' boolean'),
                      ('CONSTRAINT cle_init_conc_conf', 'PRIMARY KEY (id)')]


class init_conc_wq(MasObject):
    def __init__(self):
        super(init_conc_wq, self).__init__()
        self.order = 30
        self.geom_type = None
        self.attrs = [
            ('id_config', 'integer'),
            ('id_trac', 'integer'),
            ('bief', ' integer'),
            ('abscissa', ' float'),
            ('value', 'float'),
            ('CONSTRAINT cle_init_conc_wq', 'PRIMARY KEY (id_config, id_trac, bief,abscissa)')]


# *****************************************
# Hydraulic structur
# ******************************************
class struct_config(MasObject):
    def __init__(self):
        super(struct_config, self).__init__()
        self.order = 26
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('name', 'character varying(30)'),
                      ('type', 'text'),
                      ('method', 'integer'),
                      ('active', 'boolean'),
                      ('abscissa', 'float'),
                      ('branchnum', 'integer'),
                      ('id_prof_ori', 'integer'),
                      ('comment', 'text'),
                      ('CONSTRAINT cle_struct_conf', 'PRIMARY KEY (id)')]


class profil_struct(MasObject):
    def __init__(self):
        super(profil_struct, self).__init__()
        self.order = 27
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_order', 'integer'),
                      ('x', 'float'),
                      ('z', 'float'),
                      ('CONSTRAINT profil_struct_pkey', 'PRIMARY KEY (id_order,id_config)')]


class struct_param(MasObject):
    def __init__(self):
        super(struct_param, self).__init__()
        self.order = 28
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('var', 'text'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_param', 'PRIMARY KEY (id_config,var)')]


class struct_elem_param(MasObject):
    def __init__(self):
        super(struct_elem_param, self).__init__()
        self.order = 29
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_elem', 'integer'),
                      ('var', 'text'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_elem_param', 'PRIMARY KEY (id_config,id_elem,var)')]


class struct_elem(MasObject):
    def __init__(self):
        super(struct_elem, self).__init__()
        self.order = 30
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_elem', 'integer'),
                      ('type', 'integer'),
                      ('polygon', 'GEOMETRY'),
                      ('CONSTRAINT cle_struct_elem', 'PRIMARY KEY (id_config,id_elem)')]


class struct_abac(MasObject):
    def __init__(self):
        super(struct_abac, self).__init__()
        self.order = 31
        self.geom_type = None
        self.attrs = [('nam_method', 'text'),
                      ('nam_abac', 'text'),
                      ('var', 'text'),
                      ('id_order', 'integer'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_abac', 'PRIMARY KEY (id_order,nam_method,nam_abac,var)')]


class struct_laws(MasObject):
    def __init__(self):
        super(struct_laws, self).__init__()
        self.order = 32
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_var', 'integer'),
                      ('id_order', 'integer'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_laws', 'PRIMARY KEY (id_config, id_var, id_order)')]


# ************************************************************************************

class struct_fg(MasObject):
    # parameter vanne
    def __init__(self):
        super(struct_fg, self).__init__()
        self.order = 33
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_scen', 'integer'),
                      ('active', 'boolean'),
                      ('type_fg', 'text'),
                      ('xpos', 'text'),
                      ('var_reg', 'text'),
                      ('CONSTRAINT cle_struct_fg', 'PRIMARY KEY (id_config,id_scen)')]


class struct_fg_val(MasObject):
    # valeur des variable float
    def __init__(self):
        super(struct_fg_val, self).__init__()
        self.order = 34
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_scen', 'integer'),
                      ('id_order', 'integer'),
                      ('name_var', 'text'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_fg_val', 'PRIMARY KEY (id_config,id_scen,id_order,name_var)')]


class weirs_mob_val(MasObject):
    # valeur des variable float
    def __init__(self):
        super(weirs_mob_val, self).__init__()
        self.order = 35
        self.geom_type = None
        self.attrs = [('id_weirs', 'integer'),
                      ('id_order', 'integer'),
                      ('name_var', 'text'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_weirs_mob_val', 'PRIMARY KEY (id_weirs,id_order,name_var)')]


class admin_tab(MasObject):
    # valeur des variable float
    def __init__(self):
        super(admin_tab, self).__init__()
        self.order = 36
        self.geom_type = None
        self.attrs = [('id_', 'serial NOT NULL'),
                      ('table_', 'text'),
                      ('version_', 'text'),
                      ('CONSTRAINT cle_admin_tab', 'PRIMARY KEY (id_,table_, version_)')]


# new results table
class results(MasObject):
    def __init__(self):
        super(results, self).__init__()
        self.order = 37
        self.geom_type = None
        self.attrs = [('id_runs', 'integer NOT NULL'),
                      ('time', 'float'),
                      ('pknum', 'float'),
                      ('var', 'integer'),
                      ('val', 'float'),
                      ('CONSTRAINT results_pkey', ' PRIMARY KEY (id_runs, time, pknum, var)')]

        # def pg_create_table(self):
        #     qry = super(self.__class__, self).pg_create_table()
        #     qry += '\n'
        #     qry += "CREATE INDEX IF NOT EXISTS idx_res_var ON {0}.results(id_runs);\n".format(self.schema)
        #     return qry


class results_sect(MasObject):
    def __init__(self):
        super(results_sect, self).__init__()
        self.order = 38
        self.geom_type = None
        self.attrs = [('id_runs', 'integer NOT NULL'),
                      ('pk', 'float'),
                      ('branch', 'integer'),
                      ('section', 'integer'),
                      ('CONSTRAINT results_sect_pkey', ' PRIMARY KEY (id_runs, pk, branch)')]


class results_var(MasObject):
    def __init__(self):
        super(results_var, self).__init__()
        self.order = 39
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('type_res', 'text'),
                      ('var', 'text'),
                      ('name', 'text'),
                      ('type_var', 'text'),
                      ('CONSTRAINT results_var_pkey', ' PRIMARY KEY (type_res, var)')]


class runs_graph(MasObject):
    def __init__(self):
        super(runs_graph, self).__init__()
        self.order = 40
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('id_runs', 'integer'),
                      ('type_res', 'text'),
                      ('var', 'text'),
                      ('val', 'json'),
                      ('CONSTRAINT runs_graph_pkey', ' PRIMARY KEY (id_runs,type_res,var)')]

# ****************************************************************************
