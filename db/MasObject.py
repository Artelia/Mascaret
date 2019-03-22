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

    def pg_create_table(self):
        schema_name = '{0}.{1}'.format(self.schema, self.name)
        attrs=self.pg_geom_attri()
        attrs += [' '.join(field) for field in self.attrs]
        if self.overwrite is True:
            qry = 'DROP TABLE IF EXISTS {0};\nCREATE TABLE {0}(\n\t{1});\n'.format(schema_name, ',\n\t'.join(attrs))
        else:
            qry = 'CREATE TABLE {0}\n(\n\t{1}\n)\nWITH(\n\t OIDS=FALSE \n);\n'.format(schema_name, ',\n\t'.join(attrs))
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

    def pg_create_index(self):
        qry='CREATE INDEX {1}_geom_idx\n  ON {0}.{1} \n  USING gist \n  (geom);\n'.format(self.schema, self.name)
        return qry

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
        '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry+='   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_point();\n'
        return qry



#*****************************************
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
            ('CONSTRAINT cle_laws', 'PRIMARY KEY (id)')]
#*****************************************
class scenarios(MasObject):
    def __init__(self):
        super(scenarios, self).__init__()
        self.order = 1
        self.geom_type = None
        self.attrs = [ ('name', 'character varying(30) NOT NULL'),
                       ('starttime', 'timestamp without time zone'),
                       ('endtime', 'timestamp without time zone'),
                       ('run', 'boolean'),
                       ('CONSTRAINT cle_scenarios', 'PRIMARY KEY (name)')]
#*****************************************
class lateral_inflows(MasObject):
    def __init__(self):
        super(lateral_inflows, self).__init__()
        self.order = 2
        self.geom_type = 'Point'
        self.attrs = [ ('gid', ' serial NOT NULL'),
                       ('name', ' character varying(30)'),
                       ('branchnum', ' integer'),
                       ('abscissa', ' float'),
                       ('length', ' float'),
                       ('firstvalue', ' float'),
                       ('method', ' text'),
                       ('active', ' boolean'),
                       ('CONSTRAINT lateral_inflows_pkey', ' PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class lateral_weirs(MasObject):
    def __init__(self):
        super(lateral_weirs, self).__init__()
        self.order = 3
        self.geom_type = 'Point'
        self.attrs = [  ('gid serial', 'NOT NULL'),
                        ('name character', 'varying(30)'),
                        ('type', 'integer'),
                        ('branchnum', 'integer'),
                        ('abscissa', 'float'),
                        ('length', 'float'),
                        ('z_crest', 'float'),
                        ('flowratecoef', 'float'),
                        ('active', 'boolean'),
                        ('CONSTRAINT lateral_weir_pkey', 'PRIMARY KEY (gid)')]
    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class extremities(MasObject):
    def __init__(self):
        super(extremities, self).__init__()
        self.order = 4
        self.geom_type = 'Point'
        self.attrs = [  ('gid serial', 'NOT NULL'),
                        ('name character', 'varying(30)'),
                        ('type', 'integer'),
                        ('method', 'text'),
                        ('firstvalue', 'float'),
                        ('abscissa', 'text'),
                        ('ordinates', 'text'),
                        ('angles', 'text'),
                        ('active',' boolean'),
                        ('CONSTRAINT cle_extremities', ' PRIMARY KEY (gid)'),
                        ('CONSTRAINT extremities_nom_key', ' UNIQUE (name)')]

#*****************************************
class flood_marks(MasObject):
    def __init__(self):
        super(flood_marks, self).__init__()
        self.order = 5
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
            ('township', 'character varying(30)'),
            ('CONSTRAINT flood_marks_pkey', 'PRIMARY KEY(gid)')]

    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class hydraulic_head(MasObject):
    def __init__(self):
        super(hydraulic_head, self).__init__()
        self.order = 6
        self.geom_type = 'Point'
        self.attrs = [  ('gid', 'serial NOT NULL'),
                        ('name', 'character varying(30)'),
                        ('branchnum', 'integer'),
                        ('abscissa', 'float'),
                        ('coeff', 'float'),
                        ('active', 'boolean'),
                        ('CONSTRAINT hydraulic_head_pkey', 'PRIMARY KEY (gid)')]
    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class outputs(MasObject):
    def __init__(self):
        super(outputs, self).__init__()
        self.order = 7
        self.geom_type = 'Point'
        self.attrs = [ ('gid', 'serial NOT NULL'),
                       ('name', 'character varying(30)'),
                       ('code', 'character varying(30)'),
                       ('zero', 'float'),
                       ('branchnum', 'integer'),
                       ('abscissa', 'float'),
                       ('CONSTRAINT outputs_pkey', 'PRIMARY KEY (gid)')]

    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class weirs(MasObject):
    def __init__(self):
        super(weirs, self).__init__()
        self.order = 8
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
            ('active', ' boolean'),
            ('CONSTRAINT weirs_pkey', ' PRIMARY KEY(gid)') ]
    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class profiles(MasObject):
    def __init__(self):
        super(profiles, self).__init__()
        self.order = 9
        self.geom_type = 'MultiLineString'
        self.attrs = [  ('gid', 'serial NOT NULL'),
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
                        ('active', 'boolean'),
                        ('CONSTRAINT profiles_pkey','PRIMARY KEY (gid)'),
                        ('CONSTRAINT profile_unique', 'UNIQUE (name)')]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_profil();\n'
        return qry

    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry
#*****************************************
class topo(MasObject):
    def __init__(self):
        super(topo, self).__init__()
        self.order = 10
        self.geom_type = 'Point'
        self.attrs = [  ('gid','serial NOT NULL'),
                        ('name','character varying(30)'),
                        ('profile','character varying(30)'),
                        ('order_','integer'),
                        ('x','float'),
                        ('z','float'),
                        ('CONSTRAINT topo_pkey','PRIMARY KEY (gid)')]
    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        return qry

    # def pg_geom_attri(self):
    #     if self.geom_type is not None:
    #         attrs = ['geom geometry({0})'.format(self.geom_type)]
    #     else:
    #         attrs = []
    #     return attrs
#*****************************************
class branchs(MasObject):
    def __init__(self):
        super(branchs, self).__init__()
        self.order = 11
        self.geom_type = 'MultiLineString'
        self.attrs = [  ('gid','serial NOT NULL'),
                        ('branch','integer'),
                        ('startb','character varying(30)'),
                        ('endb','character varying(30)'),
                        ('zonenum','integer'),
                        ('zoneabsstart','float'),
                        ('zoneabsend','float'),
                        ('minbedcoef','float'),
                        ('majbedcoef','float'),
                        ('mesh','float'),
                        ('planim','float'),
                        ('active','boolean'),
                        ('CONSTRAINT branchs_pkey','PRIMARY KEY (gid)'),
                        ('CONSTRAINT cle_debut','FOREIGN KEY (startb)\n'
                                                '\t   REFERENCES {0}.extremities (name) MATCH SIMPLE \n'
                                                '\t   ON UPDATE NO ACTION ON DELETE NO ACTION'.format(self.schema)),
                        ('CONSTRAINT cle_fin','FOREIGN KEY (startb)'
                                                '\t   REFERENCES {0}.extremities (name) MATCH SIMPLE \n'
                                                '\t   ON UPDATE NO ACTION ON DELETE NO ACTION'.format(self.schema))]
    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_branche();\n'
        return qry
    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry

# *****************************************
class resultats(MasObject):
    def __init__(self):
        super(resultats, self).__init__()
        self.order = 12
        self.geom_type = None
        self.attrs = [ ('id',' serial NOT NULL'),
                       ('run',' character varying(30)'),
                       ('scenario',' character varying(30)'),
                       ('date',' timestamp without time zone'),
                       ('t',' float'),
                       ('branche',' integer'),
                       ('section',' integer'),
                       ('pk',' float'),
                       ('zref',' float'),
                       ('z',' float'),
                       ('qmin',' float'),
                       ('qmaj',' float'),
                       ('kmin',' float'),
                       ('kmaj',' float'),
                       ('fr',' float'),
                       ('y',' float'),
                       ('zmax',' float'),
                       ('qmax',' float'),
                       ('q',' float'),
                       ('bnum',' integer'),
                       ('bz',' float'),
                       ('barea',' float'),
                       ('bvol',' float'),
                       ('lnum',' integer'),
                       ('lq',' float'),
                       ('lvel',' float'),
                       ('CONSTRAINT projet_pkey',' PRIMARY KEY (id)')]
# *****************************************
class runs(MasObject):
    def __init__(self):
        super(runs, self).__init__()
        self.order = 13
        self.geom_type = None
        self.attrs = [('id serial','NOT NULL'),
                      ('run','character varying(30)'),
                      ('scenario','character varying(30)'),
                      ('date',' timestamp without time zone'),
                      ('t',' text'),
                      ('pk',' text'),
                      ('comments', 'text'),
                      ('CONSTRAINT cle_runs','PRIMARY KEY (id)')]
#*****************************************
class observations(MasObject):
    def __init__(self):
        super(observations, self).__init__()
        self.order = 14
        self.geom_type = None
        self.attrs = [('id','serial NOT NULL'),
                      ('code','character(10)'),
                      ('type','character(1)'),
                      ('comment', 'character varying(50)'),
                      ('valeur','float'),
                      ('date','timestamp without time zone'),
                      ('CONSTRAINT cle_obs ','PRIMARY KEY (id)')]
#*****************************************
class parametres(MasObject):
    def __init__(self):
        super(parametres, self).__init__()
        self.order = 15
        self.geom_type = None
        self.attrs = [  ('id','serial NOT NULL'),
                        ('parametre','text'),
                        ('steady','text'),
                        ('unsteady','text'),
                        ('transcritical','text'),
                        ('libelle','text'),
                        ('balise1','text'),
                        ('balise2','text'),
                        ('gui','text'),
                        ('CONSTRAINT cle_param','PRIMARY KEY (id)')]
#*****************************************
class basins(MasObject):
    def __init__(self):
        super(basins, self).__init__()
        self.order = 17
        self.geom_type = 'MultiPolygon'
        self.attrs = [  ('gid', 'serial NOT NULL'),
                        ('name', 'character varying(30)'),
                        ('basinnum', 'integer'),
                        ('initlevel', 'float'),
                        ('level', 'text'),
                        ('area', 'text'),
                        ('volume', 'text'),
                        ('active', 'boolean'),
                        ('CONSTRAINT basins_pkey','PRIMARY KEY (gid)'),
                        ('CONSTRAINT basin_name_unique', 'UNIQUE (name)'),
                        ('CONSTRAINT basin_num_unique', 'UNIQUE (basinnum)')]

    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        return qry
#*****************************************
class links(MasObject):
    def __init__(self):
        super(links, self).__init__()
        self.order = 18
        self.geom_type = 'MultiLineString'
        self.attrs = [  ('gid', 'serial NOT NULL'),
                        ('name', 'character varying(30)'),
                        ('linknum', 'integer'),
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
                        ('active', 'boolean'),
                        ('CONSTRAINT links_pkey','PRIMARY KEY (gid)'),
                        ('CONSTRAINT link_name_unique', 'UNIQUE (name)'),
                        ('CONSTRAINT link_num_unique', 'UNIQUE (linknum)')]

    def pg_create_calcul_abscisse(self):
        qry = 'CREATE TRIGGER {1}_calcul_abscisse\n' \
              '  BEFORE INSERT OR UPDATE\n  ON {0}.{1}\n'.format(self.schema, self.name)
        qry += '   FOR EACH ROW\nEXECUTE PROCEDURE calcul_abscisse_profil();\n'
        return qry

    def pg_create_table(self):
        qry= super(self.__class__,self).pg_create_table()
        qry +='\n'
        qry +=self.pg_create_index()
        qry += '\n'
        qry +=self.pg_create_calcul_abscisse()
        return qry

#*****************************************


class calcul_abscisse(MasObject):
    def __init__(self):
        super(calcul_abscisse, self).__init__()
        self.order = 16

    def pg_create_calcul_abscisse (self):
        qry="""CREATE OR REPLACE FUNCTION {0}()  
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
        qry="""CREATE OR REPLACE FUNCTION {0}()
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
                        p = (SELECT (ST_ClosestPoint(g,NEW.geom)) LIMIT 1);
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
        return qry.format('calcul_abscisse_profil' )
    def pg_create_calcul_abscisse_branche(self):
        qry ='''CREATE OR REPLACE FUNCTION calcul_abscisse_branche()
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




if __name__ == '__main__':
    var= topo()
    var.schema = 'toto'
    var.srid= 9999
    # print(var.pg_create_calcul_abscisse_profil())
    with open("toto.sql",'w') as f:
        f.write(var.pg_create_table())
