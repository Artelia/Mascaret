<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.4.4-Madeira" maxScale="-4.65661e-10" readOnly="0" simplifyDrawingHints="0" simplifyMaxScale="1" minScale="200000" hasScaleBasedVisibilityFlag="1" styleCategories="AllStyleCategories" simplifyLocal="1" simplifyDrawingTol="1" simplifyAlgorithm="0" labelsEnabled="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 symbollevels="0" type="singleSymbol" enableorderby="0" forceraster="0">
    <symbols>
      <symbol name="0" alpha="1" force_rhr="0" clip_to_extent="1" type="marker">
        <layer locked="0" pass="0" enabled="1" class="SimpleMarker">
          <prop k="angle" v="0"/>
          <prop k="color" v="51,160,44,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="star"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="4"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory width="15" penWidth="0" backgroundAlpha="255" minimumSize="0" rotationOffset="270" labelPlacementMethod="XHeight" sizeScale="3x:0,0,0,0,0,0" maxScaleDenominator="200000" scaleBasedVisibility="1" height="15" lineSizeType="MM" enabled="0" penAlpha="255" opacity="1" diagramOrientation="Up" sizeType="MM" scaleDependency="Area" penColor="#000000" backgroundColor="#ffffff" minScaleDenominator="-4.65661e-10" lineSizeScale="3x:0,0,0,0,0,0" barWidth="5">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings placement="0" zIndex="0" obstacle="0" showAll="1" priority="0" dist="0" linePlacementFlags="18">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions geometryPrecision="0" removeDuplicateNodes="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="gid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="name">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="code">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="zero">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="branchnum">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="abscissa">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="active">
      <editWidget type="CheckBox">
        <config>
          <Option type="Map">
            <Option value="" name="CheckedState" type="QString"/>
            <Option value="" name="UncheckedState" type="QString"/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="gid"/>
    <alias index="1" name="" field="name"/>
    <alias index="2" name="" field="code"/>
    <alias index="3" name="" field="zero"/>
    <alias index="4" name="" field="branchnum"/>
    <alias index="5" name="" field="abscissa"/>
    <alias index="6" name="" field="active"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="gid"/>
    <default applyOnUpdate="0" expression="" field="name"/>
    <default applyOnUpdate="0" expression="" field="code"/>
    <default applyOnUpdate="0" expression="" field="zero"/>
    <default applyOnUpdate="0" expression="" field="branchnum"/>
    <default applyOnUpdate="0" expression="" field="abscissa"/>
    <default applyOnUpdate="0" expression="" field="active"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" notnull_strength="1" constraints="3" field="gid" unique_strength="1"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" field="name" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" field="code" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" field="zero" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" field="branchnum" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" field="abscissa" unique_strength="0"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" field="active" unique_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" exp="" field="gid"/>
    <constraint desc="" exp="" field="name"/>
    <constraint desc="" exp="" field="code"/>
    <constraint desc="" exp="" field="zero"/>
    <constraint desc="" exp="" field="branchnum"/>
    <constraint desc="" exp="" field="abscissa"/>
    <constraint desc="" exp="" field="active"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column name="gid" type="field" hidden="0" width="-1"/>
      <column name="name" type="field" hidden="0" width="-1"/>
      <column name="code" type="field" hidden="0" width="-1"/>
      <column name="zero" type="field" hidden="0" width="-1"/>
      <column name="branchnum" type="field" hidden="0" width="-1"/>
      <column name="abscissa" type="field" hidden="0" width="-1"/>
      <column name="active" type="field" hidden="0" width="-1"/>
      <column type="actions" hidden="1" width="-1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <editform tolerant="1"></editform>
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
  <editorlayout>tablayout</editorlayout>
  <attributeEditorForm>
    <attributeEditorContainer name="infos" showLabel="1" groupBox="0" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0">
      <attributeEditorField index="1" name="name" showLabel="1"/>
      <attributeEditorField index="2" name="code" showLabel="1"/>
      <attributeEditorField index="3" name="zero" showLabel="1"/>
      <attributeEditorField index="6" name="active" showLabel="1"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field name="abscissa" editable="1"/>
    <field name="active" editable="1"/>
    <field name="branchnum" editable="1"/>
    <field name="code" editable="1"/>
    <field name="gid" editable="1"/>
    <field name="name" editable="1"/>
    <field name="zero" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="abscissa" labelOnTop="0"/>
    <field name="active" labelOnTop="0"/>
    <field name="branchnum" labelOnTop="0"/>
    <field name="code" labelOnTop="0"/>
    <field name="gid" labelOnTop="0"/>
    <field name="name" labelOnTop="0"/>
    <field name="zero" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>name</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
