<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis hasScaleBasedVisibilityFlag="1" simplifyDrawingHints="0" simplifyDrawingTol="1" labelsEnabled="0" simplifyLocal="1" readOnly="0" styleCategories="AllStyleCategories" simplifyAlgorithm="0" simplifyMaxScale="1" version="3.16.7-Hannover" minScale="200000" maxScale="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <temporal durationField="" startField="" startExpression="" accumulate="0" fixedDuration="0" endField="" mode="0" durationUnit="min" endExpression="" enabled="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 type="categorizedSymbol" forceraster="0" attr="CASE WHEN  &quot;active&quot; = 'true'  THEN if( &quot;type&quot; =4 and  &quot;thickness&quot; =1,44, &quot;type&quot; ) ELSE 0 END" enableorderby="0" symbollevels="0">
    <categories>
      <category symbol="0" label="Rating curve weir (Abacuses Zam/Zav/Q)" render="true" value="1"/>
      <category symbol="1" label="Rating curve weir (Abacuses Zam=f(Q))" render="true" value="2"/>
      <category symbol="2" label="Geometric weir (Crest profile)" render="true" value="3"/>
      <category symbol="3" label="Weir law (thin)" render="true" value="4"/>
      <category symbol="4" label="Weir law (thick)" render="true" value="44"/>
      <category symbol="5" label="Limni upstream weir (Abacuses (Zam, t))" render="true" value="5"/>
      <category symbol="6" label="Upstream rating weir(Abacuses Q=f(Zam))" render="true" value="6"/>
      <category symbol="7" label="Downstream rating curve weir(Abacuses (Q, Zav))" render="true" value="7"/>
      <category symbol="8" label="Floodgate" render="true" value="8"/>
      <category symbol="9" label="inactive" render="true" value="0"/>
    </categories>
    <symbols>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="0">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="26,105,201,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="1">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="240,240,240,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="2">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="46,91,37,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="3">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,127,0,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="4">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="56,255,7,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="5">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="101,189,0,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="6">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="113,232,253,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="7">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,146,210,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="8">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="219,169,225,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="9">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="159,159,159,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol clip_to_extent="1" type="marker" alpha="1" force_rhr="0" name="0">
        <layer locked="0" pass="0" class="SimpleMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="251,154,153,255"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="name" v="triangle"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="area"/>
          <prop k="size" v="3"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" value="" name="name"/>
              <Option name="properties"/>
              <Option type="QString" value="collection" name="type"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property value="&quot;gid&quot;" key="dualview/previewExpressions"/>
    <property value="0" key="embeddedWidgets/count"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <LinearlyInterpolatedDiagramRenderer diagramType="Text" upperWidth="50" lowerHeight="0" lowerValue="0" attributeLegend="1" classificationAttributeExpression="" upperValue="0" lowerWidth="0" upperHeight="50">
    <DiagramCategory direction="1" backgroundColor="#ffffff" minScaleDenominator="100000" sizeScale="3x:0,0,0,0,0,0" lineSizeScale="3x:0,0,0,0,0,0" penAlpha="255" enabled="0" scaleBasedVisibility="1" rotationOffset="270" spacing="0" barWidth="5" diagramOrientation="Up" labelPlacementMethod="XHeight" width="15" minimumSize="0" opacity="1" maxScaleDenominator="200000" spacingUnitScale="3x:0,0,0,0,0,0" penWidth="0" penColor="#000000" spacingUnit="MM" backgroundAlpha="255" showAxis="0" sizeType="MM" height="15" scaleDependency="Area" lineSizeType="MM">
      <fontProperties style="" description=",8.25,-1,5,50,0,0,0,0,0"/>
      <attribute field="&quot;abscissa&quot;" label="&quot;abscissa&quot;" color="#04a3d0"/>
      <attribute field="&quot;branchnum&quot;" label="&quot;branchnum&quot;" color="#254877"/>
      <axisSymbol>
        <symbol clip_to_extent="1" type="line" alpha="1" force_rhr="0" name="">
          <layer locked="0" pass="0" class="SimpleLine" enabled="1">
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
                <Option type="QString" value="" name="name"/>
                <Option name="properties"/>
                <Option type="QString" value="collection" name="type"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </LinearlyInterpolatedDiagramRenderer>
  <DiagramLayerSettings showAll="0" linePlacementFlags="0" zIndex="0" dist="0" placement="0" priority="0" obstacle="0">
    <properties>
      <Option type="Map">
        <Option type="QString" value="" name="name"/>
        <Option type="Map" name="properties">
          <Option type="Map" name="show">
            <Option type="bool" value="true" name="active"/>
            <Option type="QString" value="gid" name="field"/>
            <Option type="int" value="2" name="type"/>
          </Option>
        </Option>
        <Option type="QString" value="collection" name="type"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend type="default-vector"/>
  <referencedLayers/>
  <fieldConfiguration>
    <field configurationFlags="None" name="gid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="name">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="type">
      <editWidget type="ValueMap">
        <config>
          <Option type="Map">
            <Option type="List" name="map">
              <Option type="Map">
                <Option type="QString" value="7" name="Downstream rating curve weir(Abacuses (Q, Zav))"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="8" name="Floodgate"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="3" name="Geometric weir (Crest profile)"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="5" name="Limni upstream weir (Abacuses (Zam, t))"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="1" name="Rating curve weir (Abacuses Zam/Zav/Q)"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="2" name="Rating curve weir (Abacuses Zam=f(Q))"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="6" name="Upstream rating weir( (Abacuses Q=f(Zam))"/>
              </Option>
              <Option type="Map">
                <Option type="QString" value="4" name="Weir law"/>
              </Option>
            </Option>
          </Option>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="branchnum">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="abscissa">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="z_crest">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="z_average_crest">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="z_break">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="flowratecoeff">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="thickness">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="wide_floodgate">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="lawfile">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="active">
      <editWidget type="CheckBox">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="active_mob">
      <editWidget type="CheckBox">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="None" name="method_mob">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="gid" name=""/>
    <alias index="1" field="name" name=""/>
    <alias index="2" field="type" name=""/>
    <alias index="3" field="branchnum" name=""/>
    <alias index="4" field="abscissa" name=""/>
    <alias index="5" field="z_crest" name=""/>
    <alias index="6" field="z_average_crest" name=""/>
    <alias index="7" field="z_break" name=""/>
    <alias index="8" field="flowratecoeff" name=""/>
    <alias index="9" field="thickness" name=""/>
    <alias index="10" field="wide_floodgate" name=""/>
    <alias index="11" field="lawfile" name=""/>
    <alias index="12" field="active" name=""/>
    <alias index="13" field="active_mob" name=""/>
    <alias index="14" field="method_mob" name=""/>
  </aliases>
  <defaults>
    <default field="gid" expression="" applyOnUpdate="0"/>
    <default field="name" expression="" applyOnUpdate="0"/>
    <default field="type" expression="" applyOnUpdate="0"/>
    <default field="branchnum" expression="" applyOnUpdate="0"/>
    <default field="abscissa" expression="" applyOnUpdate="0"/>
    <default field="z_crest" expression="" applyOnUpdate="0"/>
    <default field="z_average_crest" expression="" applyOnUpdate="0"/>
    <default field="z_break" expression="" applyOnUpdate="0"/>
    <default field="flowratecoeff" expression="" applyOnUpdate="0"/>
    <default field="thickness" expression="" applyOnUpdate="0"/>
    <default field="wide_floodgate" expression="" applyOnUpdate="0"/>
    <default field="lawfile" expression="" applyOnUpdate="0"/>
    <default field="active" expression="" applyOnUpdate="0"/>
    <default field="active_mob" expression="" applyOnUpdate="0"/>
    <default field="method_mob" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint constraints="3" field="gid" unique_strength="1" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="name" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="type" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="branchnum" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="abscissa" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="z_crest" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="z_average_crest" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="z_break" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="flowratecoeff" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="thickness" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="wide_floodgate" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="0" field="lawfile" unique_strength="0" notnull_strength="0" exp_strength="0"/>
    <constraint constraints="1" field="active" unique_strength="0" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="1" field="active_mob" unique_strength="0" notnull_strength="1" exp_strength="0"/>
    <constraint constraints="0" field="method_mob" unique_strength="0" notnull_strength="0" exp_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint desc="" field="gid" exp=""/>
    <constraint desc="" field="name" exp=""/>
    <constraint desc="" field="type" exp=""/>
    <constraint desc="" field="branchnum" exp=""/>
    <constraint desc="" field="abscissa" exp=""/>
    <constraint desc="" field="z_crest" exp=""/>
    <constraint desc="" field="z_average_crest" exp=""/>
    <constraint desc="" field="z_break" exp=""/>
    <constraint desc="" field="flowratecoeff" exp=""/>
    <constraint desc="" field="thickness" exp=""/>
    <constraint desc="" field="wide_floodgate" exp=""/>
    <constraint desc="" field="lawfile" exp=""/>
    <constraint desc="" field="active" exp=""/>
    <constraint desc="" field="active_mob" exp=""/>
    <constraint desc="" field="method_mob" exp=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column hidden="0" type="field" width="-1" name="gid"/>
      <column hidden="0" type="field" width="-1" name="name"/>
      <column hidden="0" type="field" width="-1" name="type"/>
      <column hidden="0" type="field" width="-1" name="branchnum"/>
      <column hidden="0" type="field" width="-1" name="abscissa"/>
      <column hidden="0" type="field" width="-1" name="z_crest"/>
      <column hidden="0" type="field" width="-1" name="z_average_crest"/>
      <column hidden="0" type="field" width="-1" name="z_break"/>
      <column hidden="0" type="field" width="-1" name="flowratecoeff"/>
      <column hidden="0" type="field" width="-1" name="thickness"/>
      <column hidden="0" type="field" width="-1" name="wide_floodgate"/>
      <column hidden="0" type="field" width="-1" name="lawfile"/>
      <column hidden="0" type="field" width="-1" name="active"/>
      <column hidden="1" type="actions" width="-1"/>
      <column hidden="0" type="field" width="-1" name="active_mob"/>
      <column hidden="0" type="field" width="-1" name="method_mob"/>
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
    <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="0" name="infos">
      <attributeEditorField showLabel="1" index="1" name="name"/>
      <attributeEditorField showLabel="1" index="2" name="type"/>
      <attributeEditorField showLabel="1" index="12" name="active"/>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="0" name="Abacuses">
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Break">
        <attributeEditorField showLabel="1" index="5" name="z_crest"/>
        <attributeEditorField showLabel="1" index="7" name="z_break"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="0" name="Crest profile">
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Weir characteristics">
        <attributeEditorField showLabel="1" index="6" name="z_average_crest"/>
        <attributeEditorField showLabel="1" index="8" name="flowratecoeff"/>
      </attributeEditorContainer>
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Break">
        <attributeEditorField showLabel="1" index="7" name="z_break"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="0" name="Weir law">
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Weir characteristics">
        <attributeEditorField showLabel="1" index="5" name="z_crest"/>
        <attributeEditorField showLabel="1" index="8" name="flowratecoeff"/>
        <attributeEditorField showLabel="1" index="9" name="thickness"/>
      </attributeEditorContainer>
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Break">
        <attributeEditorField showLabel="1" index="7" name="z_break"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
    <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="0" name="Floodgate">
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Weir characteristics">
        <attributeEditorField showLabel="1" index="10" name="wide_floodgate"/>
        <attributeEditorField showLabel="1" index="11" name="lawfile"/>
      </attributeEditorContainer>
      <attributeEditorContainer showLabel="1" columnCount="0" visibilityExpression="" visibilityExpressionEnabled="0" groupBox="1" name="Break">
        <attributeEditorField showLabel="1" index="7" name="z_break"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field editable="1" name="abscissa"/>
    <field editable="1" name="active"/>
    <field editable="1" name="active_mob"/>
    <field editable="1" name="branchnum"/>
    <field editable="1" name="flowratecoeff"/>
    <field editable="1" name="gid"/>
    <field editable="1" name="lawfile"/>
    <field editable="1" name="method_mob"/>
    <field editable="1" name="name"/>
    <field editable="1" name="thickness"/>
    <field editable="1" name="type"/>
    <field editable="1" name="wide_floodgate"/>
    <field editable="1" name="z_average_crest"/>
    <field editable="1" name="z_break"/>
    <field editable="1" name="z_crest"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abscissa"/>
    <field labelOnTop="0" name="active"/>
    <field labelOnTop="0" name="active_mob"/>
    <field labelOnTop="0" name="branchnum"/>
    <field labelOnTop="0" name="flowratecoeff"/>
    <field labelOnTop="0" name="gid"/>
    <field labelOnTop="0" name="lawfile"/>
    <field labelOnTop="0" name="method_mob"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="thickness"/>
    <field labelOnTop="0" name="type"/>
    <field labelOnTop="0" name="wide_floodgate"/>
    <field labelOnTop="0" name="z_average_crest"/>
    <field labelOnTop="0" name="z_break"/>
    <field labelOnTop="0" name="z_crest"/>
  </labelOnTop>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"gid"</previewExpression>
  <mapTip>&lt;img src="Z:\modelisation\mascaret\sarthe_amont\photos\[% "nom" %]" /></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
