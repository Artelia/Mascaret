<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis readOnly="0" simplifyDrawingHints="0" version="3.16.7-Hannover" simplifyMaxScale="1" simplifyDrawingTol="1" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" maxScale="0" minScale="100000000" labelsEnabled="0" simplifyLocal="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal accumulate="0" startField="" mode="0" durationUnit="min" startExpression="" enabled="0" endField="" durationField="" fixedDuration="0" endExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 enableorderby="0" symbollevels="0" forceraster="0" type="singleSymbol">
    <symbols>
      <symbol clip_to_extent="1" force_rhr="0" name="0" type="marker" alpha="1">
        <layer class="SimpleMarker" enabled="1" locked="0" pass="0">
          <prop k="angle" v="0"/>
          <prop k="color" v="253,191,111,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="circle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="2"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>"gid"</value>
      <value>gid</value>
      <value>"gid"</value>
    </property>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory height="15" sizeType="MM" minScaleDenominator="0" showAxis="0" scaleBasedVisibility="0" spacingUnitScale="3x:0,0,0,0,0,0" enabled="0" penWidth="0" backgroundColor="#ffffff" rotationOffset="270" diagramOrientation="Up" backgroundAlpha="255" penAlpha="255" sizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" spacingUnit="MM" spacing="0" maxScaleDenominator="1e+08" direction="1" barWidth="5" width="15" opacity="1" lineSizeType="MM" minimumSize="0" lineSizeScale="3x:0,0,0,0,0,0" scaleDependency="Area" penColor="#000000">
      <fontProperties style="" description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0"/>
      <attribute label="" color="#000000" field=""/>
      <axisSymbol>
        <symbol clip_to_extent="1" force_rhr="0" name="" type="line" alpha="1">
          <layer class="SimpleLine" enabled="1" locked="0" pass="0">
            <prop k="align_dash_pattern" v="0"/>
            <prop k="capstyle" v="square"/>
            <prop k="customdash" v="5;2"/>
            <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="customdash_unit" v="MM"/>
            <prop k="dash_pattern_offset" v="0"/>
            <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="dash_pattern_offset_unit" v="MM"/>
            <prop k="draw_inside_polygon" v="0"/>
            <prop k="joinstyle" v="bevel"/>
            <prop k="line_color" v="35,35,35,255"/>
            <prop k="line_style" v="solid"/>
            <prop k="line_width" v="0.26"/>
            <prop k="line_width_unit" v="MM"/>
            <prop k="offset" v="0"/>
            <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="offset_unit" v="MM"/>
            <prop k="ring_filter" v="0"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option name="name" type="QString" value=""/>
                <Option name="properties"/>
                <Option name="type" type="QString" value="collection"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" obstacle="0" priority="0" placement="0" dist="0" zIndex="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field name="gid" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="name" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="profile" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="order_" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option type="Map">
            <Option name="AllowNull" type="bool" value="true"/>
            <Option name="Max" type="int" value="2147483647"/>
            <Option name="Min" type="int" value="-2147483648"/>
            <Option name="Precision" type="int" value="0"/>
            <Option name="Step" type="int" value="1"/>
            <Option name="Style" type="QString" value="SpinBox"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="x" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="z" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="gid"/>
    <alias index="1" name="" field="name"/>
    <alias index="2" name="" field="profile"/>
    <alias index="3" name="order" field="order_"/>
    <alias index="4" name="" field="x"/>
    <alias index="5" name="" field="z"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="gid" expression=""/>
    <default applyOnUpdate="0" field="name" expression=""/>
    <default applyOnUpdate="0" field="profile" expression=""/>
    <default applyOnUpdate="0" field="order_" expression=""/>
    <default applyOnUpdate="0" field="x" expression=""/>
    <default applyOnUpdate="0" field="z" expression=""/>
  </defaults>
  <constraints>
    <constraint unique_strength="1" constraints="3" exp_strength="0" field="gid" notnull_strength="1"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" field="name" notnull_strength="0"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" field="profile" notnull_strength="0"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" field="order_" notnull_strength="0"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" field="x" notnull_strength="0"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" field="z" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="gid"/>
    <constraint exp="" desc="" field="name"/>
    <constraint exp="" desc="" field="profile"/>
    <constraint exp="" desc="" field="order_"/>
    <constraint exp="" desc="" field="x"/>
    <constraint exp="" desc="" field="z"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="">
    <columns>
      <column hidden="0" name="gid" type="field" width="-1"/>
      <column hidden="0" name="name" type="field" width="-1"/>
      <column hidden="0" name="profile" type="field" width="-1"/>
      <column hidden="0" name="order_" type="field" width="-1"/>
      <column hidden="0" name="x" type="field" width="-1"/>
      <column hidden="0" name="z" type="field" width="-1"/>
      <column hidden="1" type="actions" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1">.</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
Les formulaires QGIS peuvent avoir une fonction Python qui sera appelée à l'ouverture du formulaire.

Utilisez cette fonction pour ajouter plus de fonctionnalités à vos formulaires.

Entrez le nom de la fonction dans le champ "Fonction d'initialisation Python".
Voici un exemple à suivre:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
    geom = feature.geometry()
    control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field editable="1" name="gid"/>
    <field editable="1" name="name"/>
    <field editable="1" name="order_"/>
    <field editable="1" name="profile"/>
    <field editable="1" name="x"/>
    <field editable="1" name="z"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="gid"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="order_"/>
    <field labelOnTop="0" name="profile"/>
    <field labelOnTop="0" name="x"/>
    <field labelOnTop="0" name="z"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"gid"</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
