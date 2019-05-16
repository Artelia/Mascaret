<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.4.0-Madeira" maxScale="-4.65661e-10" hasScaleBasedVisibilityFlag="0" minScale="1e+08" styleCategories="AllStyleCategories" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>id</value>
    </property>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="id">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="name">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option name="IsMultiline" type="bool" value="false"/>
            <Option name="UseHtml" type="bool" value="false"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="starttime">
      <editWidget type="DateTime">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="endtime">
      <editWidget type="DateTime">
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
    <field name="type">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option name="map" type="List">
              <Option type="Map">
                <Option name="Hydrograph Q(t)" type="QString" value="1"/>
              </Option>
              <Option type="Map">
                <Option name="limnigraph Z(t)" type="QString" value="2"/>
              </Option>
              <Option type="Map">
                <Option name="Limnihydrograph Z,Q(t)" type="QString" value="3"/>
              </Option>
              <Option type="Map">
                <Option name="Rating curve Z=f(Q)" type="QString" value="4"/>
              </Option>
              <Option type="Map">
                <Option name="Rating curve Q=f(Z)" type="QString" value="5"/>
              </Option>
              <Option type="Map">
                <Option name="Weir Zam=f(Q,Zav)" type="QString" value="6"/>
              </Option>
              <Option type="Map">
                <Option name="Floodgate Zinf,Zsup=f(t)" type="QString" value="7"/>
              </Option>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="flowrate">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="time">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="z_upstream">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="z_downstream">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="z_lower">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="z_up">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" name="" field="id"/>
    <alias index="1" name="" field="name"/>
    <alias index="2" name="" field="starttime"/>
    <alias index="3" name="" field="endtime"/>
    <alias index="4" name="" field="z"/>
    <alias index="5" name="" field="type"/>
    <alias index="6" name="" field="flowrate"/>
    <alias index="7" name="" field="time"/>
    <alias index="8" name="" field="z_upstream"/>
    <alias index="9" name="" field="z_downstream"/>
    <alias index="10" name="" field="z_lower"/>
    <alias index="11" name="" field="z_up"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default field="id" expression="" applyOnUpdate="0"/>
    <default field="name" expression="" applyOnUpdate="0"/>
    <default field="starttime" expression="" applyOnUpdate="0"/>
    <default field="endtime" expression="" applyOnUpdate="0"/>
    <default field="z" expression="" applyOnUpdate="0"/>
    <default field="type" expression="1" applyOnUpdate="0"/>
    <default field="flowrate" expression="" applyOnUpdate="0"/>
    <default field="time" expression="" applyOnUpdate="0"/>
    <default field="z_upstream" expression="" applyOnUpdate="0"/>
    <default field="z_downstream" expression="" applyOnUpdate="0"/>
    <default field="z_lower" expression="" applyOnUpdate="0"/>
    <default field="z_up" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="id" exp_strength="0" unique_strength="1" notnull_strength="1"/>
    <constraint constraints="0" field="name" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="starttime" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="endtime" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="z" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="4" field="type" exp_strength="2" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="flowrate" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="time" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="z_upstream" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="z_downstream" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="z_lower" exp_strength="0" unique_strength="0" notnull_strength="0"/>
    <constraint constraints="0" field="z_up" exp_strength="0" unique_strength="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="id" exp=""/>
    <constraint desc="" field="name" exp=""/>
    <constraint desc="" field="starttime" exp=""/>
    <constraint desc="" field="endtime" exp=""/>
    <constraint desc="" field="z" exp=""/>
    <constraint desc="" field="type" exp="&quot;type&quot;"/>
    <constraint desc="" field="flowrate" exp=""/>
    <constraint desc="" field="time" exp=""/>
    <constraint desc="" field="z_upstream" exp=""/>
    <constraint desc="" field="z_downstream" exp=""/>
    <constraint desc="" field="z_lower" exp=""/>
    <constraint desc="" field="z_up" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column name="id" type="field" width="-1" hidden="0"/>
      <column name="name" type="field" width="-1" hidden="0"/>
      <column name="starttime" type="field" width="-1" hidden="0"/>
      <column name="endtime" type="field" width="-1" hidden="0"/>
      <column name="z" type="field" width="-1" hidden="0"/>
      <column name="type" type="field" width="-1" hidden="0"/>
      <column name="flowrate" type="field" width="-1" hidden="0"/>
      <column name="time" type="field" width="-1" hidden="0"/>
      <column name="z_upstream" type="field" width="-1" hidden="0"/>
      <column name="z_downstream" type="field" width="-1" hidden="0"/>
      <column name="z_lower" type="field" width="-1" hidden="0"/>
      <column name="z_up" type="field" width="-1" hidden="0"/>
      <column type="actions" width="-1" hidden="1"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
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
  <editorlayout>tablayout</editorlayout>
  <attributeEditorForm>
    <attributeEditorContainer showLabel="1" name="infos" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="1" name="name"/>
      <attributeEditorField showLabel="1" index="2" name="starttime"/>
      <attributeEditorField showLabel="1" index="3" name="endtime"/>
      <attributeEditorField showLabel="1" index="5" name="type"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" name="Tarage" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="4" name="z"/>
      <attributeEditorField showLabel="1" index="6" name="flowrate"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" name="Limnigraph" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="7" name="time"/>
      <attributeEditorField showLabel="1" index="4" name="z"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" name="Hydrograph" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="7" name="time"/>
      <attributeEditorField showLabel="1" index="6" name="flowrate"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" name="Limnihydrograph" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="7" name="time"/>
      <attributeEditorField showLabel="1" index="4" name="z"/>
      <attributeEditorField showLabel="1" index="6" name="flowrate"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" name="Weir law" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="9" name="z_downstream"/>
      <attributeEditorField showLabel="1" index="6" name="flowrate"/>
      <attributeEditorField showLabel="1" index="8" name="z_upstream"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" name="Floodgate law" groupBox="0" visibilityExpressionEnabled="0" columnCount="0" visibilityExpression="">
      <attributeEditorField showLabel="1" index="7" name="time"/>
      <attributeEditorField showLabel="1" index="10" name="z_lower"/>
      <attributeEditorField showLabel="1" index="11" name="z_up"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field name="endtime" editable="1"/>
    <field name="flowrate" editable="1"/>
    <field name="id" editable="1"/>
    <field name="name" editable="1"/>
    <field name="starttime" editable="1"/>
    <field name="time" editable="1"/>
    <field name="type" editable="1"/>
    <field name="z" editable="1"/>
    <field name="z_downstream" editable="1"/>
    <field name="z_lower" editable="1"/>
    <field name="z_up" editable="1"/>
    <field name="z_upstream" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="endtime" labelOnTop="0"/>
    <field name="flowrate" labelOnTop="0"/>
    <field name="id" labelOnTop="0"/>
    <field name="name" labelOnTop="0"/>
    <field name="starttime" labelOnTop="0"/>
    <field name="time" labelOnTop="0"/>
    <field name="type" labelOnTop="0"/>
    <field name="z" labelOnTop="0"/>
    <field name="z_downstream" labelOnTop="0"/>
    <field name="z_lower" labelOnTop="0"/>
    <field name="z_up" labelOnTop="0"/>
    <field name="z_upstream" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>id</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>4</layerGeometryType>
</qgis>
