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
    USER = None

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
        self.user = self.USER

    # def pg_create_table(self, geo_ori=False):
    def pg_create_table(self):
        schema_name = '{0}.{1}'.format(self.schema, self.name)
        attrs = self.pg_geom_attri()
        # if geo_ori:
        #     attrs_ori = self.pg_geom_ori_attri()
        #     attrs += [' '.join(attrs_ori)]
        attrs += [' '.join(field) for field in self.attrs]

        if self.overwrite is True:
            qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {0}(\n\t{1});\n'.format(
                schema_name, ',\n\t'.join(attrs))
        else:
            qry = 'CREATE TABLE  IF NOT EXISTS {0}\n(\n\t{1}\n)\nWITH(\n\t OIDS=FALSE \n);\n'.format(
                schema_name,
                ',\n\t'.join(
                    attrs))
        # if self.spatial_index is True:
        #     qry += 'SELECT "{0}".create_spatial_index(\'{0}\', \'{1}\');'.format(self.schema, self.name)
        # else:
        #     pass
        # qry += 'ALTER TABLE {0}.{1}\n\tOWNER TO {2};\n'.format(self.schema, self.name, self.user)

        return qry

    def pg_geom_attri(self):
        if self.geom_type is not None:
            attrs = [
                'geom geometry({0}, {1})'.format(self.geom_type, self.srid)]
        else:
            attrs = []
        return attrs

    def pg_geom_ori_attri(self):
        if self.geom_type is not None:
            attrs = [
                'geom_ori geometry({0}, {1})'.format(self.geom_type, self.srid)]
        else:
            attrs = []
        return attrs

    def pg_create_index(self):
        qry = 'CREATE INDEX {1}_geom_idx\n  ON {0}.{1} \n  USING gist \n  (geom);\n'.format(
            self.schema, self.name)
        return qry

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema,
                                                                 self.name)
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
        self.order = 99
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
            EXECUTE PROCEDURE public.delete_point_flood();""".format(
            self.schema, self.name)
        return qry

    def pg_calcul_abscisse_flood(self):
        """ create trigger"""
        qry = """
        CREATE TRIGGER {1}_calcul_abscisse_flood
        BEFORE INSERT OR UPDATE 
        ON {0}.{1}
        FOR EACH ROW
        EXECUTE PROCEDURE public.calcul_abscisse_point_flood();
        """.format(self.schema, self.name)
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
                      ('CONSTRAINT tracer_lateral_inflows_pkey',
                       ' PRIMARY KEY (gid)')]

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
                      ('zleftminbed', 'float'),
                      ('zrightminbed', 'float'),
                      ('CONSTRAINT profiles_pkey', 'PRIMARY KEY (gid)'),
                      ('CONSTRAINT profile_unique', 'UNIQUE (name)')]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema,
                                                                 self.name)
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
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema,
                                                                 self.name)
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
                                               '\t   ON UPDATE NO ACTION ON DELETE NO ACTION'.format(
                          self.schema)),
                      ('CONSTRAINT cle_fin', 'FOREIGN KEY (startb)'
                                             '\t   REFERENCES {0}.extremities (name) MATCH SIMPLE \n'
                                             '\t   ON UPDATE NO ACTION ON DELETE NO ACTION'.format(
                          self.schema))]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema,
                                                                 self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_branche();\n'
        return qry

    def pg_updat_actv(self):
        qry = 'CREATE TRIGGER {1}_chstate_active\n' \
              ' AFTER UPDATE OF active \n  ON {0}.{1}\n'.format(self.schema, self.name)
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

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS observations_code_type " \
               "ON {}.observations(code, type);".format(self.schema)
        qry += '\n'
        return qry


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

    def pg_clone_schema(self):
        """
        clone schema in psql
        example : SELECT clone_schema('ouvrage3','ouvrage3_ext','runs,results,results_sect,runs_graph');
        """
        qry = """
-- Function: clone_schema(source text, dest text, include_records boolean default true, show_details boolean default false)

-- DROP FUNCTION clone_schema(text, text,text, boolean, boolean);

CREATE OR REPLACE FUNCTION clone_schema(
  source_schema text,
  dest_schema text,
	list_tab text ,
  include_recs boolean DEFAULT true,
  show_details boolean DEFAULT false)
  RETURNS void AS
$BODY$

--  This function will clone all sequences, tables, data, views & functions from any existing schema to a new one
-- SAMPLE CALL:
-- SELECT clone_schema('public', 'new_schema', 'list_tab_ignor');
-- SELECT clone_schema('public', 'new_schema', 'list_tab_ignor', TRUE);
-- SELECT clone_schema('public', 'new_schema', 'list_tab_ignor', TRUE, TRUE);

DECLARE
  src_oid          oid;
  tbl_oid          oid;
  func_oid         oid;
  object           text;
  buffer           text;
  srctbl           text;
  default_         text;
  column_          text;
  qry              text;
  xrec             record;
  dest_qry         text;
  v_def            text;
  seqval           bigint;
  sq_last_value    bigint;
  sq_max_value     bigint;
  sq_start_value   bigint;
  sq_increment_by  bigint;
  sq_min_value     bigint;
  sq_cache_value   bigint;
  sq_log_cnt       bigint;
  sq_is_called     boolean;
  sq_is_cycled     boolean;
  sq_cycled        char(10);
  rec              record;
  source_schema_dot text = source_schema || '.';
  dest_schema_dot text = dest_schema || '.';

BEGIN

  -- Check that source_schema exists
  SELECT oid INTO src_oid
  FROM pg_namespace
  WHERE nspname = quote_ident(source_schema);
  IF NOT FOUND
  THEN
    RAISE NOTICE 'source schema % does not exist!', source_schema;
    RETURN ;
  END IF;

  -- Check that dest_schema does not yet exist
  PERFORM nspname
  FROM pg_namespace
  WHERE nspname = quote_ident(dest_schema);
  IF FOUND
  THEN
    RAISE NOTICE 'dest schema % already exists!', dest_schema;
    RETURN ;
  END IF;

  EXECUTE 'CREATE SCHEMA ' || quote_ident(dest_schema) ;

  -- Defaults search_path to destination schema
  PERFORM set_config('search_path', dest_schema, true);

  -- Create sequences
  -- TODO: Find a way to make this sequence's owner is the correct table.
  FOR object IN
  SELECT sequence_name::text
  FROM information_schema.sequences
  WHERE sequence_schema = quote_ident(source_schema)
  LOOP
    EXECUTE 'CREATE SEQUENCE ' || quote_ident(dest_schema) || '.' || quote_ident(object);
    srctbl := quote_ident(source_schema) || '.' || quote_ident(object);

    EXECUTE 'SELECT last_value ,log_cnt, is_called
              FROM ' || quote_ident(source_schema) || '.' || quote_ident(object) || ';'
              INTO sq_last_value, sq_log_cnt, sq_is_called ;
	sq_start_value =  1;

    buffer := quote_ident(dest_schema) || '.' || quote_ident(object);
    IF include_recs
    THEN
      EXECUTE 'SELECT setval( ''' || buffer || ''', ' || sq_last_value || ', ' || sq_is_called || ');' ;
    ELSE
      EXECUTE 'SELECT setval( ''' || buffer || ''', ' || sq_start_value || ', ' || sq_is_called || ');' ;
    END IF;
    IF show_details THEN RAISE NOTICE 'Sequence created: %', object; END IF;
  END LOOP;

  -- Create tables
  FOR object IN
  SELECT TABLE_NAME::text
  FROM information_schema.tables
  WHERE table_schema = quote_ident(source_schema)
        AND table_type = 'BASE TABLE'

  LOOP
    buffer := dest_schema || '.' || quote_ident(object);
    EXECUTE 'CREATE TABLE ' || buffer || ' (LIKE ' || quote_ident(source_schema) || '.' || quote_ident(object)
            || ' INCLUDING ALL)';

    IF include_recs AND not (object IN (SELECT regexp_split_to_table(list_tab,'[,]')))
    THEN
      -- Insert records from source table
      EXECUTE 'INSERT INTO ' || buffer || ' SELECT * FROM ' || quote_ident(source_schema) || '.' || quote_ident(object) || ';';
    END IF;

    FOR column_, default_ IN
    SELECT column_name::text,
      REPLACE(column_default::text, source_schema, dest_schema)
    FROM information_schema.COLUMNS
    WHERE table_schema = dest_schema
          AND TABLE_NAME = object
          AND column_default LIKE 'nextval(%' || quote_ident(source_schema) || '%::regclass)'
    LOOP
      EXECUTE 'ALTER TABLE ' || buffer || ' ALTER COLUMN ' || column_ || ' SET DEFAULT ' || default_;
    END LOOP;

    IF show_details THEN RAISE NOTICE 'base table created: %', object; END IF;

  END LOOP;

  --  add FK constraint
  FOR xrec IN
  SELECT ct.conname as fk_name, rn.relname as tb_name,  'ALTER TABLE ' || quote_ident(dest_schema) || '.' || quote_ident(rn.relname)
         || ' ADD CONSTRAINT ' || quote_ident(ct.conname) || ' ' || replace(pg_get_constraintdef(ct.oid), source_schema_dot, '') || ';' as qry
  FROM pg_constraint ct
    JOIN pg_class rn ON rn.oid = ct.conrelid
  WHERE connamespace = src_oid
        AND rn.relkind = 'r'
        AND ct.contype = 'f'

  LOOP
    IF show_details THEN RAISE NOTICE 'Creating FK constraint %.%...', xrec.tb_name, xrec.fk_name; END IF;
    --RAISE NOTICE 'DEF: %', xrec.qry;
    EXECUTE xrec.qry;
  END LOOP;

  -- Create functions
  FOR xrec IN
  SELECT proname as func_name, oid as func_oid
  FROM pg_proc
  WHERE pronamespace = src_oid

  LOOP
    IF show_details THEN RAISE NOTICE 'Creating function %...', xrec.func_name; END IF;
    SELECT pg_get_functiondef(xrec.func_oid) INTO qry;
    SELECT replace(qry, source_schema_dot, '') INTO dest_qry;
    EXECUTE dest_qry;
  END LOOP;

  -- add Table Triggers
  FOR rec IN
  SELECT
    trg.tgname AS trigger_name,
    tbl.relname AS trigger_table,

    CASE
    WHEN trg.tgenabled='O' THEN 'ENABLED'
    ELSE 'DISABLED'
    END AS status,
    CASE trg.tgtype::integer & 1
    WHEN 1 THEN 'ROW'::text
    ELSE 'STATEMENT'::text
    END AS trigger_level,
    CASE trg.tgtype::integer & 66
    WHEN 2 THEN 'BEFORE'
    WHEN 64 THEN 'INSTEAD OF'
    ELSE 'AFTER'
    END AS action_timing,
    CASE trg.tgtype::integer & cast(60 AS int2)
    WHEN 16 THEN 'UPDATE'
    WHEN 8 THEN 'DELETE'
    WHEN 4 THEN 'INSERT'
    WHEN 20 THEN 'INSERT OR UPDATE'
    WHEN 28 THEN 'INSERT OR UPDATE OR DELETE'
    WHEN 24 THEN 'UPDATE OR DELETE'
    WHEN 12 THEN 'INSERT OR DELETE'
    WHEN 32 THEN 'TRUNCATE'
    END AS trigger_event,
    'EXECUTE PROCEDURE ' ||  (SELECT nspname FROM pg_namespace where oid = pc.pronamespace )
    || '.' || proname || '('
    || regexp_replace(replace(trim(trailing '0' from encode(tgargs,'escape')), '0',','),'{(.+)}','''{}''','g')
    || ')' as action_statement

  FROM pg_trigger trg
    JOIN pg_class tbl on trg.tgrelid = tbl.oid
    JOIN pg_proc pc ON pc.oid = trg.tgfoid
  WHERE trg.tgname not like 'RI_ConstraintTrigger%'
        AND trg.tgname not like 'pg_sync_pg%'
        AND tbl.relnamespace = (SELECT oid FROM pg_namespace where nspname = quote_ident(source_schema) )

  LOOP
    buffer := dest_schema || '.' || quote_ident(rec.trigger_table);
    IF show_details THEN RAISE NOTICE 'Creating trigger % % % ON %...', rec.trigger_name, rec.action_timing, rec.trigger_event, rec.trigger_table; END IF;
    EXECUTE 'CREATE TRIGGER ' || rec.trigger_name || ' ' || rec.action_timing
            || ' ' || rec.trigger_event || ' ON ' || buffer || ' FOR EACH '
            || rec.trigger_level || ' ' || replace(rec.action_statement, source_schema_dot, '');

  END LOOP;

  -- Create views
  FOR object IN
  SELECT table_name::text,
    view_definition
  FROM information_schema.views
  WHERE table_schema = quote_ident(source_schema)

  LOOP
    buffer := dest_schema || '.' || quote_ident(object);
    SELECT replace(view_definition, source_schema_dot, '') INTO v_def
    FROM information_schema.views
    WHERE table_schema = quote_ident(source_schema)
          AND table_name = quote_ident(object);
    IF show_details THEN RAISE NOTICE 'Creating view % AS %', object, regexp_replace(v_def, '[\n\r]+', ' ', 'g'); END IF;
    EXECUTE 'CREATE OR REPLACE VIEW ' || buffer || ' AS ' || v_def || ';' ;

  END LOOP;

  RETURN;

END;

$BODY$
LANGUAGE plpgsql VOLATILE
COST 100;
"""
        #         qry = """
        # CREATE OR REPLACE FUNCTION public.clone_schema(source_schema text, dest_schema text, list_tab text ) RETURNS void AS
        # $BODY$
        # DECLARE
        #   objeto text;
        #   buffer text;
        # BEGIN
        #     EXECUTE 'CREATE SCHEMA ' || dest_schema ;
        #
        #     FOR objeto IN
        #         SELECT table_name::text FROM information_schema.tables WHERE table_schema = source_schema
        #     LOOP
        #         buffer := dest_schema || '.' || objeto;
        #
        #         EXECUTE 'CREATE TABLE ' || buffer || ' (LIKE ' || source_schema || '.' || objeto || ' INCLUDING CONSTRAINTS INCLUDING INDEXES INCLUDING DEFAULTS)';
        # 		IF not (objeto IN (SELECT regexp_split_to_table(list_tab,'[,]'))) THEN
        # 			EXECUTE 'INSERT INTO ' || buffer || '(SELECT * FROM ' || source_schema || '.' || objeto ||  ')';
        # 		ELSE
        # 			RAISE NOTICE '%', objeto;
        # 		END IF;
        # 	END LOOP;
        #
        # END;
        # $BODY$
        # LANGUAGE plpgsql VOLATILE;
        # """
        return qry

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
              COST 100; """

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
                  COST 100;"""
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
         EXECUTE 'UPDATE ' || TG_TABLE_SCHEMA || '.links SET active = $2 WHERE (branchnum = $1)' USING NEW.branch,NEW.active;
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
        RETURNS TABLE(abscissa double precision, branch integer)
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
         BEGIN
            EXECUTE 'SELECT geom FROM  ' || _tbl || ' WHERE gid = $1' USING id_prof INTO geom_p;
            EXECUTE 'SELECT branch, zonenum, geom, ST_Distance(geom, $1) FROM ' || _tbl_branchs || ' ORDER BY 4 LIMIT 1' USING geom_p INTO b,z,g,d  ;
            EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM  ' || _tbl_branchs || ' WHERE (branch<$1) OR (branch=$1 AND zonenum<$2))' USING b,z INTO long1;
            p = (SELECT (ST_DUMP(ST_Intersection(geom_p, g))).geom LIMIT 1);
            long2 = (SELECT (ST_Length(g)*ST_LineLocatePoint(ST_LineMerge(g),p)));
            IF long1 IS NULL THEN
                  long1 = 0;
            END IF;
            abscissa := ROUND((long1+long2)::numeric,2);
            branch := b;

            RETURN NEXT;
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
        b1  integer;   
     BEGIN
       FOR my_row IN  EXECUTE 'SELECT gid FROM ' ||_tbl
       LOOP
          SELECT abscissa, branch FROM public.abscisse_profil( _tbl ,_tbl_branchs, my_row ) INTO abs1,b1;
          EXECUTE 'UPDATE  '||_tbl || ' SET  branchnum = $3, abscissa = $1 WHERE gid = $2' USING abs1, my_row,b1;
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
    RETURNS TABLE(abscissa double precision, branch integer)
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
         abscissa :=     ROUND((long1+long2)::numeric,2);        
         branch := b;          
        RETURN NEXT;
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
            b1  integer;     
         BEGIN
          FOR my_row IN  EXECUTE 'SELECT gid FROM ' ||_tbl
           LOOP
             SELECT abscissa, branch FROM  public.abscisse_point( _tbl ,_tbl_branchs, my_row ) INTO abs1,b1;
             EXECUTE 'UPDATE  '||_tbl || ' SET  branchnum = $3, abscissa = $1 WHERE gid = $2' USING abs1, my_row,b1;
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
        qry = """
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
        EXECUTE 'SELECT geom,zonenum,branch FROM  ' || _tbl_branchs || ' WHERE gid = $1' USING id_branch INTO geom_b,zonenum, branch;
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
          EXECUTE 'UPDATE  '||_tbl_branchs || ' SET zoneabsstart = $1, zoneabsend = $2 WHERE gid = $3' 
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
    VOLATILE NOT LEAKPROOF 
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
                val  double precision;
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
                     
                    IF TG_OP='INSERT' OR NEW.abscissa IS NULL OR NOT ST_Equals(NEW.geom,OLD.geom) THEN
                     	NEW.branchnum= b ;
                        /* projection compute*/
                       EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2) )' USING b,z INTO long1;
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
                         NEW.branchnum= b ;
                         
                        IF NOT  OLD.abscissa=  NEW.abscissa THEN
                         RAISE NOTICE 'entre 1 ';
                            EXECUTE '(SELECT ST_Length(ST_UNION(geom)) FROM ' || TG_TABLE_SCHEMA || '.branchs WHERE (branch<$1) OR (branch=$1 AND zonenum<$2) )' USING b,z INTO long1;
                            IF long1 IS NULL THEN
                               long1 = 0;
                            END IF;
                            /* check if new abscissa is in zone*/
                            val = (NEW.abscissa-long1)/ST_Length(g);
                            IF val>1 OR  val<0 THEN
                            	RAISE NOTICE 'Branch : %, Zone : %',b,z;
                            	RAISE NOTICE 'The new abscissa (%) is not between % and % ;', NEW.abscissa, long1, long1+ST_Length(g);
                            END IF ;    

                            geom_final_p = (SELECT ST_LineInterpolatePoint(ST_LineMerge(g),val));                            
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
            (
                'CONSTRAINT cle_laws_wq',
                'PRIMARY KEY (id_config, id_trac, time)')]


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
            (
                'CONSTRAINT cle_laws_met',
                'PRIMARY KEY (id_config, id_var, time)')]


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
            ('CONSTRAINT cle_init_conc_wq',
             'PRIMARY KEY (id_config, id_trac, bief,abscissa)')]


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
                      ('CONSTRAINT profil_struct_pkey',
                       'PRIMARY KEY (id_order,id_config)')]


class struct_param(MasObject):
    def __init__(self):
        super(struct_param, self).__init__()
        self.order = 28
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('var', 'text'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_param',
                       'PRIMARY KEY (id_config,var)')]


class struct_elem_param(MasObject):
    def __init__(self):
        super(struct_elem_param, self).__init__()
        self.order = 29
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_elem', 'integer'),
                      ('var', 'text'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_elem_param',
                       'PRIMARY KEY (id_config,id_elem,var)')]


class struct_elem(MasObject):
    def __init__(self):
        super(struct_elem, self).__init__()
        self.order = 30
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_elem', 'integer'),
                      ('type', 'integer'),
                      ('polygon', 'GEOMETRY'),
                      ('CONSTRAINT cle_struct_elem',
                       'PRIMARY KEY (id_config,id_elem)')]


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
                      ('CONSTRAINT cle_struct_abac',
                       'PRIMARY KEY (id_order,nam_method,nam_abac,var)')]


class struct_laws(MasObject):
    def __init__(self):
        super(struct_laws, self).__init__()
        self.order = 32
        self.geom_type = None
        self.attrs = [('id_config', 'integer'),
                      ('id_var', 'integer'),
                      ('id_order', 'integer'),
                      ('value', 'float'),
                      ('CONSTRAINT cle_struct_laws',
                       'PRIMARY KEY (id_config, id_var, id_order)')]


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
                      ('CONSTRAINT cle_struct_fg',
                       'PRIMARY KEY (id_config,id_scen)')]


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
                      ('CONSTRAINT cle_struct_fg_val',
                       'PRIMARY KEY (id_config,id_scen,id_order,name_var)')]


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
                      ('CONSTRAINT cle_weirs_mob_val',
                       'PRIMARY KEY (id_weirs,id_order,name_var)')]


class admin_tab(MasObject):
    # valeur des variable float
    def __init__(self):
        super(admin_tab, self).__init__()
        self.order = 36
        self.geom_type = None
        self.attrs = [('id_', 'serial NOT NULL'),
                      ('table_', 'text'),
                      ('version_', 'text'),
                      ('CONSTRAINT cle_admin_tab',
                       'PRIMARY KEY (id_,table_, version_)')]


# new results table
class results_old(MasObject):
    def __init__(self):
        super(results_old, self).__init__()
        self.order = 37
        self.geom_type = None
        self.attrs = [('id_runs', 'integer NOT NULL'),
                      ('time', 'float'),
                      ('pknum', 'float'),
                      ('var', 'integer'),
                      ('val', 'float'),
                      ('CONSTRAINT results_old_pkey',
                       ' PRIMARY KEY (id_runs, time, pknum, var)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS results_old_id_runs_pknum " \
               "ON {}.results(id_runs, pknum);".format(self.schema)
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS results_old_id_runs_time " \
               "ON {}.results(id_runs, time);".format(self.schema)
        qry += '\n'
        return qry


class results_val(MasObject):
    def __init__(self):
        super(results_val, self).__init__()
        self.order = 45
        self.geom_type = None
        self.attrs = [('idRunTPk', 'integer  NOT NULL'),
                      ('var', 'integer'),
                      ('val', 'float'),
                      ('CONSTRAINT results_val_pkey',
                       ' PRIMARY KEY (idRunTPk, var)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS results_val_idRunTPk " \
               "ON {}.results_val(idRunTPk, var);".format(self.schema)
        qry += '\n'
        return qry


class results_idx(MasObject):
    def __init__(self):
        super(results_idx, self).__init__()
        self.order = 44
        self.geom_type = None
        self.attrs = [('idRunTPk', 'serial NOT NULL'),
                      ('id_runs', 'integer NOT NULL'),
                      ('time', 'float'),
                      ('pknum', 'float'),
                      ('CONSTRAINT results_idx_pkey',
                       ' PRIMARY KEY (id_runs, time, pknum)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS results_idx_id_runs_pknum " \
               "ON {}.results_idx(id_runs, pknum);".format(self.schema)
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS results_idx_id_runs_time " \
               "ON {}.results_idx(id_runs, time);".format(self.schema)
        qry += '\n'
        return qry




class results_sect(MasObject):
    def __init__(self):
        super(results_sect, self).__init__()
        self.order = 38
        self.geom_type = None
        self.attrs = [('id_runs', 'integer NOT NULL'),
                      ('pk', 'float'),
                      ('branch', 'integer'),
                      ('section', 'integer'),
                      ('CONSTRAINT results_sect_pkey',
                       ' PRIMARY KEY (id_runs, pk, branch)')]

    def pg_create_table(self):
        qry = super(self.__class__, self).pg_create_table()
        qry += '\n'
        qry += "CREATE INDEX IF NOT EXISTS results_sect_id_runs_pknum " \
               "ON {}.results_sect(id_runs, pk);".format(self.schema)
        qry += '\n'
        return qry


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
                      ('CONSTRAINT results_var_pkey',
                       ' PRIMARY KEY (type_res, var)')]


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
                      ('CONSTRAINT runs_graph_pkey',
                       ' PRIMARY KEY (id_runs,type_res,var)')]


class runs_plani(MasObject):
    def __init__(self):
        super(runs_plani, self).__init__()
        self.order = 41
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('id_runs', 'integer'),
                      ('pknum', 'float'),
                      ('id_type', 'integer'),
                      ('id_order', 'integer'),
                      ('line', 'GEOMETRY'),
                      ('CONSTRAINT runs_plani_pkey',
                       ' PRIMARY KEY (id_runs,pknum,id_type,id_order)')]


class law_config(MasObject):
    def __init__(self):
        super(law_config, self).__init__()
        self.order = 42
        self.geom_type = None
        self.attrs = [('id', 'serial NOT NULL'),
                      ('name', 'text'),
                      ('geom_obj', 'text'),
                      ('starttime', 'timestamp without time zone'),
                      ('endtime', 'timestamp without time zone'),
                      ('id_law_type', 'integer'),
                      ('active', ' boolean NOT NULL DEFAULT FALSE'),
                      ('comment', 'text'),
                      ('CONSTRAINT law_config_pkey', 'PRIMARY KEY (id)')]


class law_values(MasObject):
    def __init__(self):
        super(law_values, self).__init__()
        self.order = 43
        self.geom_type = None
        self.attrs = [('id_law', 'integer'),
                      ('id_var', 'integer'),
                      ('id_order', 'integer'),
                      ('value', 'float'),
                      ('CONSTRAINT law_values_pkey',
                       'PRIMARY KEY (id_law, id_var, id_order)')]

# ****************************************************************************
