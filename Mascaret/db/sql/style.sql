INSERT INTO layer_styles(f_table_catalog, f_table_schema, f_table_name, f_geometry_column,
                         stylename, styleqml, stylesld, useasdefault, description,owner)

(SELECT f_table_catalog, '{0}' as f_table_schema, f_table_name, f_geometry_column,
 stylename, styleqml, stylesld, useasdefault, description,'{1}'
 FROM layer_styles
 WHERE f_table_schema='template')