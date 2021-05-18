<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyAlgorithm="0" hasScaleBasedVisibilityFlag="1" maxScale="0" styleCategories="AllStyleCategories" readOnly="0" simplifyDrawingTol="1" labelsEnabled="0" simplifyMaxScale="1" simplifyDrawingHints="0" simplifyLocal="1" version="3.4.5-Madeira" minScale="200000">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 type="categorizedSymbol" symbollevels="0" enableorderby="0" forceraster="0" attr="CASE WHEN  &quot;active&quot; = 'true'  THEN type ELSE 0 END">
    <categories>
      <category label="Rating curve weir (Abacuses Zam/Zav/Q)" value="1" render="true" symbol="0"/>
      <category label="Rating curve weir (Abacuses Zam=f(Q))" value="2" render="true" symbol="1"/>
      <category label="Geometric weir (Crest profile)" value="3" render="true" symbol="2"/>
      <category label="Weir law" value="4" render="true" symbol="3"/>
      <category label="Limni upstream weir (Abacuses (Zam, t))" value="5" render="true" symbol="4"/>
      <category label="Upstream rating weir(Abacuses Q=f(Zam))" value="6" render="true" symbol="5"/>
      <category label="Downstream rating curve weir(Abacuses (Q, Zav))" value="7" render="true" symbol="6"/>
      <category label="Floodgate" value="8" render="true" symbol="7"/>
      <category label="inactive" value="0" render="true" symbol="8"/>
    </categories>
    <symbols>
      <symbol name="0" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="26,105,201,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="1" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="240,240,240,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="2" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="111,171,69,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="3" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="255,127,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="4" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="101,189,0,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="5" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="113,232,253,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="6" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="255,146,210,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="7" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="219,169,225,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol name="8" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="159,159,159,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
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
    <source-symbol>
      <symbol name="0" alpha="1" clip_to_extent="1" type="marker" force_rhr="0">
        <layer enabled="1" class="SimpleMarker" locked="0" pass="0">
          <prop v="0" k="angle"/>
          <prop v="251,154,153,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="triangle" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,0,0,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="3" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="dualview/previewExpressions">
      <value>"gid"</value>
    </property>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <LinearlyInterpolatedDiagramRenderer classificationAttributeExpression="" lowerValue="0" lowerWidth="0" diagramType="Text" upperValue="0" lowerHeight="0" upperHeight="50" attributeLegend="1" upperWidth="50">
    <DiagramCategory penWidth="0" opacity="1" sizeScale="3x:0,0,0,0,0,0" enabled="1" scaleBasedVisibility="1" penAlpha="255" penColor="#000000" rotationOffset="270" backgroundColor="#ffffff" minimumSize="0" labelPlacementMethod="XHeight" height="15" width="15" lineSizeType="MM" diagramOrientation="Up" minScaleDenominator="100000" barWidth="5" lineSizeScale="3x:0,0,0,0,0,0" backgroundAlpha="255" maxScaleDenominator="200000" sizeType="MM" scaleDependency="Area">
      <fontProperties description=",8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="&quot;abscissa&quot;" color="#04a3d0" field="&quot;abscissa&quot;"/>
      <attribute label="&quot;branchnum&quot;" color="#254877" field="&quot;branchnum&quot;"/>
    </DiagramCategory>
  </LinearlyInterpolatedDiagramRenderer>
  <DiagramLayerSettings dist="0" obstacle="0" showAll="0" linePlacementFlags="0" placement="0" priority="0" zIndex="0">
    <properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties" type="Map">
          <Option name="show" type="Map">
            <Option name="active" type="bool" value="true"/>
            <Option name="field" type="QString" value="gid"/>
            <Option name="type" type="int" value="2"/>
          </Option>
        </Option>
        <Option name="type" type="QString" value="collection"/>
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
    <field name="type">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option name="map" type="List">
              <Option type="Map">
                <Option name="Downstream rating curve weir(Abacuses (Q, Zav))" type="QString" value="7"/>
              </Option>
              <Option type="Map">
                <Option name="Floodgate" type="QString" value="8"/>
              </Option>
              <Option type="Map">
                <Option name="Geometric weir (Crest profile)" type="QString" value="3"/>
              </Option>
              <Option type="Map">
                <Option name="Limni upstream weir (Abacuses (Zam, t))" type="QString" value="5"/>
              </Option>
              <Option type="Map">
                <Option name="Rating curve weir (Abacuses Zam/Zav/Q)" type="QString" value="1"/>
              </Option>
              <Option type="Map">
                <Option name="Rating curve weir (Abacuses Zam=f(Q))" type="QString" value="2"/>
              </Option>
              <Option type="Map">
                <Option name="Upstream rating weir( (Abacuses Q=f(Zam))" type="QString" value="6"/>
              </Option>
              <Option type="Map">
                <Option name="Weir law" type="QString" value="4"/>
              </Option>
            </Option>
          </Option>
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
    <field name="z_crest">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="z_average_crest">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="z_break">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="flowratecoeff">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="thickness">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="wide_floodgate">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="lawfile">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="active">
      <editWidget type="CheckBox">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="active_mob">
      <editWidget type="CheckBox">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="method_mob">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="gid"/>
    <alias name="" index="1" field="name"/>
    <alias name="" index="2" field="type"/>
    <alias name="" index="3" field="branchnum"/>
    <alias name="" index="4" field="abscissa"/>
    <alias name="" index="5" field="z_crest"/>
    <alias name="" index="6" field="z_average_crest"/>
    <alias name="" index="7" field="z_break"/>
    <alias name="" index="8" field="flowratecoeff"/>
    <alias name="" index="9" field="thickness"/>
    <alias name="" index="10" field="wide_floodgate"/>
    <alias name="" index="11" field="lawfile"/>
    <alias name="" index="12" field="active"/>
    <alias name="" index="13" field="active_mob"/>
    <alias name="" index="14" field="method_mob"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="gid"/>
    <default applyOnUpdate="0" expression="" field="name"/>
    <default applyOnUpdate="0" expression="" field="type"/>
    <default applyOnUpdate="0" expression="" field="branchnum"/>
    <default applyOnUpdate="0" expression="" field="abscissa"/>
    <default applyOnUpdate="0" expression="" field="z_crest"/>
    <default applyOnUpdate="0" expression="" field="z_average_crest"/>
    <default applyOnUpdate="0" expression="" field="z_break"/>
    <default applyOnUpdate="0" expression="" field="flowratecoeff"/>
    <default applyOnUpdate="0" expression="" field="thickness"/>
    <default applyOnUpdate="0" expression="" field="wide_floodgate"/>
    <default applyOnUpdate="0" expression="" field="lawfile"/>
    <default applyOnUpdate="0" expression="" field="active"/>
    <default applyOnUpdate="0" expression="" field="active_mob"/>
    <default applyOnUpdate="0" expression="" field="method_mob"/>
  </defaults>
  <constraints>
    <constraint unique_strength="1" constraints="3" exp_strength="0" notnull_strength="1" field="gid"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="name"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="type"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="branchnum"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="abscissa"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="z_crest"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="z_average_crest"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="z_break"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="flowratecoeff"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="thickness"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="wide_floodgate"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="lawfile"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="active"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="active_mob"/>
    <constraint unique_strength="0" constraints="0" exp_strength="0" notnull_strength="0" field="method_mob"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="gid"/>
    <constraint exp="" desc="" field="name"/>
    <constraint exp="" desc="" field="type"/>
    <constraint exp="" desc="" field="branchnum"/>
    <constraint exp="" desc="" field="abscissa"/>
    <constraint exp="" desc="" field="z_crest"/>
    <constraint exp="" desc="" field="z_average_crest"/>
    <constraint exp="" desc="" field="z_break"/>
    <constraint exp="" desc="" field="flowratecoeff"/>
    <constraint exp="" desc="" field="thickness"/>
    <constraint exp="" desc="" field="wide_floodgate"/>
    <constraint exp="" desc="" field="lawfile"/>
    <constraint exp="" desc="" field="active"/>
    <constraint exp="" desc="" field="active_mob"/>
    <constraint exp="" desc="" field="method_mob"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig sortOrder="0" actionWidgetStyle="dropDown" sortExpression="">
    <columns>
      <column width="-1" name="gid" hidden="0" type="field"/>
      <column width="-1" name="name" hidden="0" type="field"/>
      <column width="-1" name="type" hidden="0" type="field"/>
      <column width="-1" name="branchnum" hidden="0" type="field"/>
      <column width="-1" name="abscissa" hidden="0" type="field"/>
      <column width="-1" name="z_crest" hidden="0" type="field"/>
      <column width="-1" name="z_average_crest" hidden="0" type="field"/>
      <column width="-1" name="z_break" hidden="0" type="field"/>
      <column width="-1" name="flowratecoeff" hidden="0" type="field"/>
      <column width="-1" name="thickness" hidden="0" type="field"/>
      <column width="-1" name="wide_floodgate" hidden="0" type="field"/>
      <column width="-1" name="lawfile" hidden="0" type="field"/>
      <column width="-1" name="active" hidden="0" type="field"/>
      <column width="-1" hidden="1" type="actions"/>
      <column width="-1" name="active_mob" hidden="0" type="field"/>
      <column width="-1" name="method_mob" hidden="0" type="field"/>
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
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>tablayout</editorlayout>
  <attributeEditorForm>
    <attributeEditorContainer name="infos" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="0" showLabel="1">
      <attributeEditorField name="name" index="1" showLabel="1"/>
      <attributeEditorField name="type" index="2" showLabel="1"/>
      <attributeEditorField name="active" index="12" showLabel="1"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Abacuses" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="0" showLabel="1">
      <attributeEditorContainer name="Break" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="z_crest" index="5" showLabel="1"/>
        <attributeEditorField name="z_break" index="7" showLabel="1"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer name="Crest profile" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="0" showLabel="1">
      <attributeEditorContainer name="Weir characteristics" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="z_average_crest" index="6" showLabel="1"/>
        <attributeEditorField name="flowratecoeff" index="8" showLabel="1"/>
      </attributeEditorContainer>
      <attributeEditorContainer name="Break" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="z_break" index="7" showLabel="1"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer name="Weir law" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="0" showLabel="1">
      <attributeEditorContainer name="Weir characteristics" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="z_crest" index="5" showLabel="1"/>
        <attributeEditorField name="flowratecoeff" index="8" showLabel="1"/>
        <attributeEditorField name="thickness" index="9" showLabel="1"/>
      </attributeEditorContainer>
      <attributeEditorContainer name="Break" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="z_break" index="7" showLabel="1"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer name="Floodgate" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="0" showLabel="1">
      <attributeEditorContainer name="Weir characteristics" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="wide_floodgate" index="10" showLabel="1"/>
        <attributeEditorField name="lawfile" index="11" showLabel="1"/>
      </attributeEditorContainer>
      <attributeEditorContainer name="Break" columnCount="0" visibilityExpressionEnabled="0" visibilityExpression="" groupBox="1" showLabel="1">
        <attributeEditorField name="z_break" index="7" showLabel="1"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field name="abscissa" editable="1"/>
    <field name="active" editable="1"/>
    <field name="active_mob" editable="1"/>
    <field name="branchnum" editable="1"/>
    <field name="flowratecoeff" editable="1"/>
    <field name="gid" editable="1"/>
    <field name="lawfile" editable="1"/>
    <field name="method_mob" editable="1"/>
    <field name="name" editable="1"/>
    <field name="thickness" editable="1"/>
    <field name="type" editable="1"/>
    <field name="wide_floodgate" editable="1"/>
    <field name="z_average_crest" editable="1"/>
    <field name="z_break" editable="1"/>
    <field name="z_crest" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="abscissa" labelOnTop="0"/>
    <field name="active" labelOnTop="0"/>
    <field name="active_mob" labelOnTop="0"/>
    <field name="branchnum" labelOnTop="0"/>
    <field name="flowratecoeff" labelOnTop="0"/>
    <field name="gid" labelOnTop="0"/>
    <field name="lawfile" labelOnTop="0"/>
    <field name="method_mob" labelOnTop="0"/>
    <field name="name" labelOnTop="0"/>
    <field name="thickness" labelOnTop="0"/>
    <field name="type" labelOnTop="0"/>
    <field name="wide_floodgate" labelOnTop="0"/>
    <field name="z_average_crest" labelOnTop="0"/>
    <field name="z_break" labelOnTop="0"/>
    <field name="z_crest" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>gid</previewExpression>
  <mapTip>&lt;img src="Z:\modelisation\mascaret\sarthe_amont\photos\[% "nom" %]" /></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
