<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="-4.65661e-10" minScale="200000" labelsEnabled="0" simplifyAlgorithm="0" readOnly="0" simplifyMaxScale="1" styleCategories="AllStyleCategories" hasScaleBasedVisibilityFlag="1" version="3.10.8-A Coruña" simplifyLocal="1" simplifyDrawingHints="0" simplifyDrawingTol="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 forceraster="0" enableorderby="0" type="singleSymbol" symbollevels="0">
    <symbols>
      <symbol alpha="1" force_rhr="0" type="marker" name="0" clip_to_extent="1">
        <layer pass="0" locked="0" enabled="1" class="SimpleMarker">
          <prop v="0" k="angle"/>
          <prop v="51,160,44,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="cross" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="51,160,44,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.5" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="2.5" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
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
      <value>"name"</value>
    </property>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <LinearlyInterpolatedDiagramRenderer diagramType="Histogram" upperHeight="50" lowerWidth="0" lowerHeight="0" lowerValue="0" attributeLegend="1" upperValue="0" classificationField="gid" upperWidth="50">
    <DiagramCategory backgroundAlpha="255" scaleDependency="Area" minimumSize="0" rotationOffset="270" minScaleDenominator="100000" sizeScale="3x:0,0,0,0,0,0" maxScaleDenominator="200000" opacity="1" sizeType="MM" labelPlacementMethod="XHeight" penWidth="0" penColor="#000000" barWidth="5" backgroundColor="#ffffff" height="15" width="15" penAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" diagramOrientation="Up" lineSizeType="MM" scaleBasedVisibility="1" enabled="1">
      <fontProperties description=",8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" color="#000000" field=""/>
    </DiagramCategory>
  </LinearlyInterpolatedDiagramRenderer>
  <DiagramLayerSettings obstacle="0" priority="0" linePlacementFlags="0" zIndex="0" placement="0" dist="0" showAll="0">
    <properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
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
    <field name="event">
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
    <field name="date">
      <editWidget type="DateTime">
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
    <field name="z">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="validate">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="comment">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="weir">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="adress">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="township">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="geom_ori">
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
            <Option type="QString" name="CheckedState" value=""/>
            <Option type="QString" name="UncheckedState" value=""/>
          </Option>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="gid"/>
    <alias index="1" name="" field="name"/>
    <alias index="2" name="" field="event"/>
    <alias index="3" name="" field="branchnum"/>
    <alias index="4" name="" field="date"/>
    <alias index="5" name="" field="abscissa"/>
    <alias index="6" name="" field="z"/>
    <alias index="7" name="" field="validate"/>
    <alias index="8" name="" field="comment"/>
    <alias index="9" name="" field="weir"/>
    <alias index="10" name="" field="adress"/>
    <alias index="11" name="" field="township"/>
    <alias index="12" name="" field="geom_ori"/>
    <alias index="13" name="" field="active"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default expression="" field="gid" applyOnUpdate="0"/>
    <default expression="" field="name" applyOnUpdate="0"/>
    <default expression="" field="event" applyOnUpdate="0"/>
    <default expression="" field="branchnum" applyOnUpdate="0"/>
    <default expression="" field="date" applyOnUpdate="0"/>
    <default expression="" field="abscissa" applyOnUpdate="0"/>
    <default expression="" field="z" applyOnUpdate="0"/>
    <default expression="" field="validate" applyOnUpdate="0"/>
    <default expression="" field="comment" applyOnUpdate="0"/>
    <default expression="" field="weir" applyOnUpdate="0"/>
    <default expression="" field="adress" applyOnUpdate="0"/>
    <default expression="" field="township" applyOnUpdate="0"/>
    <default expression="" field="geom_ori" applyOnUpdate="0"/>
    <default expression="" field="active" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" unique_strength="1" exp_strength="0" notnull_strength="1" field="gid"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="name"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="event"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="branchnum"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="date"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="abscissa"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="z"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="validate"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="comment"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="weir"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="adress"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="township"/>
    <constraint constraints="0" unique_strength="0" exp_strength="0" notnull_strength="0" field="geom_ori"/>
    <constraint constraints="1" unique_strength="0" exp_strength="0" notnull_strength="2" field="active"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="gid" desc=""/>
    <constraint exp="" field="name" desc=""/>
    <constraint exp="" field="event" desc=""/>
    <constraint exp="" field="branchnum" desc=""/>
    <constraint exp="" field="date" desc=""/>
    <constraint exp="" field="abscissa" desc=""/>
    <constraint exp="" field="z" desc=""/>
    <constraint exp="" field="validate" desc=""/>
    <constraint exp="" field="comment" desc=""/>
    <constraint exp="" field="weir" desc=""/>
    <constraint exp="" field="adress" desc=""/>
    <constraint exp="" field="township" desc=""/>
    <constraint exp="" field="geom_ori" desc=""/>
    <constraint exp="" field="active" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="1" sortExpression="&quot;active&quot;">
    <columns>
      <column type="field" name="gid" width="-1" hidden="0"/>
      <column type="field" name="name" width="-1" hidden="0"/>
      <column type="field" name="event" width="-1" hidden="0"/>
      <column type="field" name="branchnum" width="-1" hidden="0"/>
      <column type="field" name="date" width="-1" hidden="0"/>
      <column type="field" name="abscissa" width="-1" hidden="0"/>
      <column type="field" name="z" width="-1" hidden="0"/>
      <column type="field" name="validate" width="-1" hidden="0"/>
      <column type="field" name="comment" width="-1" hidden="0"/>
      <column type="field" name="weir" width="-1" hidden="0"/>
      <column type="field" name="adress" width="-1" hidden="0"/>
      <column type="field" name="township" width="-1" hidden="0"/>
      <column type="field" name="geom_ori" width="-1" hidden="0"/>
      <column type="field" name="active" width="-1" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
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
    <attributeEditorContainer groupBox="0" visibilityExpression="" visibilityExpressionEnabled="0" name="infos" showLabel="1" columnCount="0">
      <attributeEditorField index="1" name="name" showLabel="1"/>
      <attributeEditorField index="3" name="branchnum" showLabel="1"/>
      <attributeEditorField index="2" name="event" showLabel="1"/>
      <attributeEditorField index="6" name="z" showLabel="1"/>
      <attributeEditorField index="13" name="active" showLabel="1"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field editable="1" name="abscissa"/>
    <field editable="1" name="active"/>
    <field editable="1" name="adress"/>
    <field editable="1" name="branchnum"/>
    <field editable="1" name="comment"/>
    <field editable="1" name="date"/>
    <field editable="1" name="event"/>
    <field editable="1" name="geom_ori"/>
    <field editable="1" name="gid"/>
    <field editable="1" name="name"/>
    <field editable="1" name="township"/>
    <field editable="1" name="validate"/>
    <field editable="1" name="weir"/>
    <field editable="1" name="z"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abscissa"/>
    <field labelOnTop="0" name="active"/>
    <field labelOnTop="0" name="adress"/>
    <field labelOnTop="0" name="branchnum"/>
    <field labelOnTop="0" name="comment"/>
    <field labelOnTop="0" name="date"/>
    <field labelOnTop="0" name="event"/>
    <field labelOnTop="0" name="geom_ori"/>
    <field labelOnTop="0" name="gid"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="township"/>
    <field labelOnTop="0" name="validate"/>
    <field labelOnTop="0" name="weir"/>
    <field labelOnTop="0" name="z"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>name</previewExpression>
  <mapTip>field_1</mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
