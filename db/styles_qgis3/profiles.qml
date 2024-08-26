<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis labelsEnabled="1" simplifyAlgorithm="0" simplifyDrawingTol="1" simplifyLocal="1" hasScaleBasedVisibilityFlag="0" readOnly="0" symbologyReferenceScale="-1" minScale="100000000" version="3.22.9-Białowieża" maxScale="-4.6566128730773926e-10" simplifyMaxScale="1" styleCategories="AllStyleCategories" simplifyDrawingHints="1">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal accumulate="0" endField="" startField="" fixedDuration="0" limitMode="0" mode="0" startExpression="" durationUnit="min" enabled="0" endExpression="" durationField="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <renderer-v2 attr=" CASE &#xd;&#xa;WHEN &quot;active&quot;=false AND struct =0 THEN 0&#xd;&#xa;WHEN &quot;active&quot;=true AND struct = 0 THEN 1&#xd;&#xa;WHEN &quot;active&quot;=true AND struct =1  THEN 3&#xd;&#xa;WHEN &quot;active&quot;=true AND struct =2 THEN 2&#xd;&#xa;WHEN &quot;active&quot;=false AND struct =2 THEN 4&#xd;&#xa;WHEN &quot;active&quot;=false AND struct =1 THEN 5&#xd;&#xa; END" symbollevels="0" enableorderby="0" forceraster="0" type="categorizedSymbol" referencescale="-1">
    <categories>
      <category label="Inactive" value="0" render="true" symbol="0"/>
      <category label="Active" value="1" render="true" symbol="1"/>
      <category label="Active +Active Structure" value="2" render="true" symbol="2"/>
      <category label="Active + Inactive Structure" value="3" render="true" symbol="3"/>
      <category label="Inactive +Active Structure" value="4" render="true" symbol="4"/>
      <category label="Inactive + Inactive Structure" value="5" render="true" symbol="5"/>
      <category label="" value="" render="true" symbol="6"/>
    </categories>
    <symbols>
      <symbol alpha="1" name="0" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="170,110,142,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.66" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="170,110,142,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.66"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleLine" locked="1" pass="2" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="0,0,0,255" name="line_color" type="QString"/>
            <Option value="dot" name="line_style" type="QString"/>
            <Option value="0.53" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="0,0,0,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.53"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" name="1" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value="line_substring( $geometry, rightstock,  $length)" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="line_substring( $geometry, rightstock,  $length)"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@1@0" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="51,160,44,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="51,160,44,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value="line_substring( $geometry, 0, leftstock )" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="line_substring( $geometry, 0, leftstock )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@1@1" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="51,160,44,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="51,160,44,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value=" line_substring( $geometry, &quot;leftminbed&quot; , &quot;rightminbed&quot; )" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" line_substring( $geometry, &quot;leftminbed&quot; , &quot;rightminbed&quot; )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@1@2" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="12,98,218,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="12,98,218,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="170,110,142,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.99" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="170,110,142,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.99"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleLine" locked="1" pass="2" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="255,255,255,255" name="line_color" type="QString"/>
            <Option value="dot" name="line_style" type="QString"/>
            <Option value="0.795" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="255,255,255,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.795"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="firstvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="firstvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@1@5" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="lastvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="lastvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@1@6" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="180" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="0,128,255,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="180"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="0,128,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
      </symbol>
      <symbol alpha="1" name="2" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value="line_substring( $geometry, rightstock,  $length)" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="line_substring( $geometry, rightstock,  $length)"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@2@0" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="51,160,44,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="51,160,44,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value="line_substring( $geometry, 0, leftstock )" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="line_substring( $geometry, 0, leftstock )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@2@1" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="51,160,44,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="51,160,44,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value=" line_substring( $geometry, &quot;leftminbed&quot; , &quot;rightminbed&quot; )" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" line_substring( $geometry, &quot;leftminbed&quot; , &quot;rightminbed&quot; )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@2@2" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="12,98,218,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="12,98,218,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="170,110,142,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.99" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="170,110,142,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.99"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleLine" locked="1" pass="2" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="255,255,255,255" name="line_color" type="QString"/>
            <Option value="dot" name="line_style" type="QString"/>
            <Option value="0.795" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="255,255,255,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.795"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="firstvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="firstvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@2@5" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="lastvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="lastvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@2@6" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="180" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="0,128,255,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="180"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="0,128,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="interval" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="interval"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@2@7" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="circle" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="1.5" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1.5"/>
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
        </layer>
      </symbol>
      <symbol alpha="1" name="3" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value="line_substring( $geometry, rightstock,  $length)" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="line_substring( $geometry, rightstock,  $length)"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@3@0" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="51,160,44,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="51,160,44,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value="line_substring( $geometry, 0, leftstock )" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v="line_substring( $geometry, 0, leftstock )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@3@1" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="51,160,44,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="51,160,44,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="GeometryGenerator" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="Line" name="SymbolType" type="QString"/>
            <Option value=" line_substring( $geometry, &quot;leftminbed&quot; , &quot;rightminbed&quot; )" name="geometryModifier" type="QString"/>
            <Option value="MapUnit" name="units" type="QString"/>
          </Option>
          <prop k="SymbolType" v="Line"/>
          <prop k="geometryModifier" v=" line_substring( $geometry, &quot;leftminbed&quot; , &quot;rightminbed&quot; )"/>
          <prop k="units" v="MapUnit"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@3@2" type="line" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleLine" locked="1" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="round" name="joinstyle" type="QString"/>
                <Option value="0,0,0,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="4.06" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="round"/>
              <prop k="line_color" v="0,0,0,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="4.06"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="227,26,28,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="227,26,28,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
            <layer class="SimpleLine" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="align_dash_pattern" type="QString"/>
                <Option value="flat" name="capstyle" type="QString"/>
                <Option value="5;2" name="customdash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
                <Option value="MM" name="customdash_unit" type="QString"/>
                <Option value="0" name="dash_pattern_offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
                <Option value="0" name="draw_inside_polygon" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="12,98,218,255" name="line_color" type="QString"/>
                <Option value="solid" name="line_style" type="QString"/>
                <Option value="3.6" name="line_width" type="QString"/>
                <Option value="MM" name="line_width_unit" type="QString"/>
                <Option value="0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="0" name="ring_filter" type="QString"/>
                <Option value="0" name="trim_distance_end" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_end_unit" type="QString"/>
                <Option value="0" name="trim_distance_start" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
                <Option value="MM" name="trim_distance_start_unit" type="QString"/>
                <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
                <Option value="0" name="use_custom_dash" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
              </Option>
              <prop k="align_dash_pattern" v="0"/>
              <prop k="capstyle" v="flat"/>
              <prop k="customdash" v="5;2"/>
              <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="customdash_unit" v="MM"/>
              <prop k="dash_pattern_offset" v="0"/>
              <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="dash_pattern_offset_unit" v="MM"/>
              <prop k="draw_inside_polygon" v="0"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="line_color" v="12,98,218,255"/>
              <prop k="line_style" v="solid"/>
              <prop k="line_width" v="3.6"/>
              <prop k="line_width_unit" v="MM"/>
              <prop k="offset" v="0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="ring_filter" v="0"/>
              <prop k="trim_distance_end" v="0"/>
              <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_end_unit" v="MM"/>
              <prop k="trim_distance_start" v="0"/>
              <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="trim_distance_start_unit" v="MM"/>
              <prop k="tweak_dash_pattern_on_corners" v="0"/>
              <prop k="use_custom_dash" v="0"/>
              <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <effect type="effectStack" enabled="0">
                <effect type="dropShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="outerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.7935" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="255,255,255,255" name="single_color" type="QString"/>
                    <Option value="2" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.7935"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="255,255,255,255"/>
                  <prop k="spread" v="2"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
                <effect type="drawSource">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerShadow">
                  <Option type="Map">
                    <Option value="13" name="blend_mode" type="QString"/>
                    <Option value="2.645" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,0,255" name="color" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="1" name="enabled" type="QString"/>
                    <Option value="135" name="offset_angle" type="QString"/>
                    <Option value="2" name="offset_distance" type="QString"/>
                    <Option value="MM" name="offset_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="offset_unit_scale" type="QString"/>
                    <Option value="1" name="opacity" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="13"/>
                  <prop k="blur_level" v="2.645"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color" v="0,0,0,255"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="1"/>
                  <prop k="offset_angle" v="135"/>
                  <prop k="offset_distance" v="2"/>
                  <prop k="offset_unit" v="MM"/>
                  <prop k="offset_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="opacity" v="1"/>
                </effect>
                <effect type="innerGlow">
                  <Option type="Map">
                    <Option value="0" name="blend_mode" type="QString"/>
                    <Option value="0.529" name="blur_level" type="QString"/>
                    <Option value="MM" name="blur_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="blur_unit_scale" type="QString"/>
                    <Option value="0,0,255,255" name="color1" type="QString"/>
                    <Option value="0,255,0,255" name="color2" type="QString"/>
                    <Option value="0" name="color_type" type="QString"/>
                    <Option value="0" name="discrete" type="QString"/>
                    <Option value="2" name="draw_mode" type="QString"/>
                    <Option value="0" name="enabled" type="QString"/>
                    <Option value="0.5" name="opacity" type="QString"/>
                    <Option value="gradient" name="rampType" type="QString"/>
                    <Option value="239,47,172,255" name="single_color" type="QString"/>
                    <Option value="1" name="spread" type="QString"/>
                    <Option value="MM" name="spread_unit" type="QString"/>
                    <Option value="3x:0,0,0,0,0,0" name="spread_unit_scale" type="QString"/>
                  </Option>
                  <prop k="blend_mode" v="0"/>
                  <prop k="blur_level" v="0.529"/>
                  <prop k="blur_unit" v="MM"/>
                  <prop k="blur_unit_scale" v="3x:0,0,0,0,0,0"/>
                  <prop k="color1" v="0,0,255,255"/>
                  <prop k="color2" v="0,255,0,255"/>
                  <prop k="color_type" v="0"/>
                  <prop k="discrete" v="0"/>
                  <prop k="draw_mode" v="2"/>
                  <prop k="enabled" v="0"/>
                  <prop k="opacity" v="0.5"/>
                  <prop k="rampType" v="gradient"/>
                  <prop k="single_color" v="239,47,172,255"/>
                  <prop k="spread" v="1"/>
                  <prop k="spread_unit" v="MM"/>
                  <prop k="spread_unit_scale" v="3x:0,0,0,0,0,0"/>
                </effect>
              </effect>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="170,110,142,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.99" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="170,110,142,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.99"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleLine" locked="1" pass="2" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="round" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="round" name="joinstyle" type="QString"/>
            <Option value="255,255,255,255" name="line_color" type="QString"/>
            <Option value="dot" name="line_style" type="QString"/>
            <Option value="0.795" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <prop k="align_dash_pattern" v="0"/>
          <prop k="capstyle" v="round"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="dash_pattern_offset" v="0"/>
          <prop k="dash_pattern_offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="dash_pattern_offset_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="round"/>
          <prop k="line_color" v="255,255,255,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.795"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="firstvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="firstvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@3@5" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="lastvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="lastvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@3@6" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="180" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="0,128,255,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="180"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="0,128,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="interval" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="interval"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@3@7" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="154,154,154,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="circle" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="1.5" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="154,154,154,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1.5"/>
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
        </layer>
      </symbol>
      <symbol alpha="1" name="4" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="170,110,142,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.99" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
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
          <prop k="line_color" v="170,110,142,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.99"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="2,2,2,255" name="line_color" type="QString"/>
            <Option value="dot" name="line_style" type="QString"/>
            <Option value="0.79" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
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
          <prop k="line_color" v="2,2,2,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.79"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="lastvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="lastvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@4@2" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="180" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="0,128,255,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="180"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="0,128,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="firstvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="firstvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@4@3" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="interval" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="interval"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@4@4" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="hexagon" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="1.5" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="hexagon"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1.5"/>
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
        </layer>
      </symbol>
      <symbol alpha="1" name="5" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="170,110,142,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.99" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
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
          <prop k="line_color" v="170,110,142,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.99"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="0,0,0,255" name="line_color" type="QString"/>
            <Option value="dot" name="line_style" type="QString"/>
            <Option value="0.79" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
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
          <prop k="line_color" v="0,0,0,255"/>
          <prop k="line_style" v="dot"/>
          <prop k="line_width" v="0.79"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="lastvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="lastvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@5@2" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="180" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="0,128,255,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="180"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="0,128,255,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="firstvertex" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="firstvertex"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@5@3" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="255,0,0,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="filled_arrowhead" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="3" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="255,0,0,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="filled_arrowhead"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </layer>
        <layer class="MarkerLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="4" name="average_angle_length" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="average_angle_map_unit_scale" type="QString"/>
            <Option value="MM" name="average_angle_unit" type="QString"/>
            <Option value="3" name="interval" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="interval_map_unit_scale" type="QString"/>
            <Option value="MM" name="interval_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="0" name="offset_along_line" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_along_line_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_along_line_unit" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="interval" name="placement" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="1" name="rotate" type="QString"/>
          </Option>
          <prop k="average_angle_length" v="4"/>
          <prop k="average_angle_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="average_angle_unit" v="MM"/>
          <prop k="interval" v="3"/>
          <prop k="interval_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="interval_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_along_line" v="0"/>
          <prop k="offset_along_line_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_along_line_unit" v="MM"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="placement" v="interval"/>
          <prop k="ring_filter" v="0"/>
          <prop k="rotate" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <symbol alpha="1" name="@5@4" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="154,154,154,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="hexagon" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="1.5" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="154,154,154,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="hexagon"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
              <prop k="outline_style" v="solid"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="scale_method" v="diameter"/>
              <prop k="size" v="1.5"/>
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
        </layer>
      </symbol>
      <symbol alpha="1" name="6" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="232,113,141,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.26" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
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
          <prop k="line_color" v="232,113,141,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.26"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
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
    <source-symbol>
      <symbol alpha="1" name="0" type="line" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer class="SimpleLine" locked="0" pass="0" enabled="1">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="207,119,47,255" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.26" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
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
          <prop k="line_color" v="207,119,47,255"/>
          <prop k="line_style" v="solid"/>
          <prop k="line_width" v="0.26"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="trim_distance_end" v="0"/>
          <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_end_unit" v="MM"/>
          <prop k="trim_distance_start" v="0"/>
          <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="trim_distance_start_unit" v="MM"/>
          <prop k="tweak_dash_pattern_on_corners" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp name="[source]" type="gradient">
      <Option type="Map">
        <Option value="247,251,255,255" name="color1" type="QString"/>
        <Option value="8,48,107,255" name="color2" type="QString"/>
        <Option value="0" name="discrete" type="QString"/>
        <Option value="gradient" name="rampType" type="QString"/>
        <Option value="0.13;222,235,247,255:0;0,0,0,255:0.26;198,219,239,255:0;0,0,0,255:0.39;158,202,225,255:0;0,0,0,255:0.52;107,174,214,255:0;0,0,0,255:0.65;66,146,198,255:0;0,0,0,255:0.78;33,113,181,255:0;0,0,0,255:0.9;8,81,156,255:0;0,0,0,255" name="stops" type="QString"/>
      </Option>
      <prop k="color1" v="247,251,255,255"/>
      <prop k="color2" v="8,48,107,255"/>
      <prop k="discrete" v="0"/>
      <prop k="rampType" v="gradient"/>
      <prop k="stops" v="0.13;222,235,247,255:0;0,0,0,255:0.26;198,219,239,255:0;0,0,0,255:0.39;158,202,225,255:0;0,0,0,255:0.52;107,174,214,255:0;0,0,0,255:0.65;66,146,198,255:0;0,0,0,255:0.78;33,113,181,255:0;0,0,0,255:0.9;8,81,156,255:0;0,0,0,255"/>
    </colorramp>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style multilineHeight="1" capitalization="0" textOrientation="horizontal" fontSize="8.25" fontUnderline="0" isExpression="1" useSubstitutions="0" previewBkgrdColor="255,255,255,255" fontKerning="1" fontSizeUnit="Point" textOpacity="1" namedStyle="Normal" blendMode="0" fontLetterSpacing="0" fontWordSpacing="0" fontFamily="MS Shell Dlg 2" fontStrikeout="0" textColor="0,0,0,255" legendString="Aa" fieldName="concat(&quot;name&quot;,' - ',&quot;abscissa&quot;)" fontWeight="50" fontSizeMapUnitScale="3x:0,0,0,0,0,0" allowHtml="0" fontItalic="0">
        <families/>
        <text-buffer bufferJoinStyle="64" bufferDraw="0" bufferNoFill="0" bufferSize="1" bufferBlendMode="0" bufferOpacity="1" bufferSizeMapUnitScale="3x:0,0,0,0,0,0" bufferColor="255,255,255,255" bufferSizeUnits="MM"/>
        <text-mask maskSizeUnits="MM" maskOpacity="1" maskEnabled="0" maskSizeMapUnitScale="3x:0,0,0,0,0,0" maskedSymbolLayers="" maskJoinStyle="128" maskType="0" maskSize="1.5"/>
        <background shapeOffsetUnit="MM" shapeBorderWidthMapUnitScale="3x:0,0,0,0,0,0" shapeSizeMapUnitScale="3x:0,0,0,0,0,0" shapeRotationType="0" shapeOpacity="1" shapeRadiiUnit="MM" shapeSizeY="0" shapeDraw="0" shapeFillColor="255,255,255,255" shapeOffsetY="0" shapeOffsetX="0" shapeRotation="0" shapeSizeType="0" shapeSizeX="0" shapeBorderWidthUnit="MM" shapeSVGFile="" shapeRadiiX="0" shapeBlendMode="0" shapeSizeUnit="MM" shapeBorderWidth="0" shapeOffsetMapUnitScale="3x:0,0,0,0,0,0" shapeType="0" shapeBorderColor="128,128,128,255" shapeRadiiY="0" shapeRadiiMapUnitScale="3x:0,0,0,0,0,0" shapeJoinStyle="64">
          <symbol alpha="1" name="markerSymbol" type="marker" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleMarker" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="0" name="angle" type="QString"/>
                <Option value="square" name="cap_style" type="QString"/>
                <Option value="190,178,151,255" name="color" type="QString"/>
                <Option value="1" name="horizontal_anchor_point" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="circle" name="name" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="35,35,35,255" name="outline_color" type="QString"/>
                <Option value="solid" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="diameter" name="scale_method" type="QString"/>
                <Option value="2" name="size" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
                <Option value="MM" name="size_unit" type="QString"/>
                <Option value="1" name="vertical_anchor_point" type="QString"/>
              </Option>
              <prop k="angle" v="0"/>
              <prop k="cap_style" v="square"/>
              <prop k="color" v="190,178,151,255"/>
              <prop k="horizontal_anchor_point" v="1"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="name" v="circle"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="35,35,35,255"/>
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
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
          <symbol alpha="1" name="fillSymbol" type="fill" clip_to_extent="1" force_rhr="0">
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
            <layer class="SimpleFill" locked="0" pass="0" enabled="1">
              <Option type="Map">
                <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
                <Option value="255,255,255,255" name="color" type="QString"/>
                <Option value="bevel" name="joinstyle" type="QString"/>
                <Option value="0,0" name="offset" type="QString"/>
                <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
                <Option value="MM" name="offset_unit" type="QString"/>
                <Option value="128,128,128,255" name="outline_color" type="QString"/>
                <Option value="no" name="outline_style" type="QString"/>
                <Option value="0" name="outline_width" type="QString"/>
                <Option value="MM" name="outline_width_unit" type="QString"/>
                <Option value="solid" name="style" type="QString"/>
              </Option>
              <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="color" v="255,255,255,255"/>
              <prop k="joinstyle" v="bevel"/>
              <prop k="offset" v="0,0"/>
              <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
              <prop k="offset_unit" v="MM"/>
              <prop k="outline_color" v="128,128,128,255"/>
              <prop k="outline_style" v="no"/>
              <prop k="outline_width" v="0"/>
              <prop k="outline_width_unit" v="MM"/>
              <prop k="style" v="solid"/>
              <data_defined_properties>
                <Option type="Map">
                  <Option value="" name="name" type="QString"/>
                  <Option name="properties"/>
                  <Option value="collection" name="type" type="QString"/>
                </Option>
              </data_defined_properties>
            </layer>
          </symbol>
        </background>
        <shadow shadowOffsetGlobal="1" shadowScale="100" shadowOffsetUnit="MM" shadowRadiusUnit="MM" shadowRadius="1.5" shadowOffsetAngle="135" shadowRadiusMapUnitScale="3x:0,0,0,0,0,0" shadowRadiusAlphaOnly="0" shadowBlendMode="6" shadowDraw="0" shadowColor="0,0,0,255" shadowOffsetDist="1" shadowUnder="0" shadowOffsetMapUnitScale="3x:0,0,0,0,0,0" shadowOpacity="0.69999999999999996"/>
        <dd_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </dd_properties>
        <substitutions/>
      </text-style>
      <text-format plussign="0" multilineAlign="0" formatNumbers="0" useMaxLineLengthForAutoWrap="1" rightDirectionSymbol=">" decimals="3" leftDirectionSymbol="&lt;" addDirectionSymbol="0" wrapChar="" autoWrapLength="0" reverseDirectionSymbol="0" placeDirectionSymbol="0"/>
      <placement offsetUnits="MapUnit" maxCurvedCharAngleOut="-20" layerType="LineGeometry" yOffset="0" polygonPlacementFlags="2" geometryGeneratorType="PointGeometry" centroidWhole="0" lineAnchorPercent="0.5" xOffset="0" priority="5" overrunDistanceMapUnitScale="3x:0,0,0,0,0,0" geometryGeneratorEnabled="0" offsetType="0" predefinedPositionOrder="TR,TL,BR,BL,R,L,TSR,BSR" distUnits="MM" quadOffset="4" rotationUnit="AngleDegrees" overrunDistanceUnit="MM" lineAnchorClipping="0" centroidInside="0" fitInPolygonOnly="0" maxCurvedCharAngleIn="20" preserveRotation="1" repeatDistanceMapUnitScale="3x:0,0,0,0,0,0" rotationAngle="0" labelOffsetMapUnitScale="3x:0,0,0,0,0,0" overrunDistance="0" repeatDistance="0" dist="0" repeatDistanceUnits="MM" placement="2" geometryGenerator="" distMapUnitScale="3x:0,0,0,0,0,0" placementFlags="10" lineAnchorType="0"/>
      <rendering minFeatureSize="0" labelPerPart="0" fontLimitPixelSize="0" drawLabels="1" scaleMin="1" scaleVisibility="0" limitNumLabels="0" fontMaxPixelSize="10000" fontMinPixelSize="3" unplacedVisibility="0" obstacleFactor="1" zIndex="0" maxNumLabels="2000" upsidedownLabels="0" scaleMax="10000000" obstacleType="0" displayAll="0" mergeLines="0" obstacle="1"/>
      <dd_properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties"/>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </dd_properties>
      <callout type="simple">
        <Option type="Map">
          <Option value="pole_of_inaccessibility" name="anchorPoint" type="QString"/>
          <Option value="0" name="blendMode" type="int"/>
          <Option name="ddProperties" type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
          <Option value="false" name="drawToAllParts" type="bool"/>
          <Option value="0" name="enabled" type="QString"/>
          <Option value="point_on_exterior" name="labelAnchorPoint" type="QString"/>
          <Option value="&lt;symbol alpha=&quot;1&quot; name=&quot;symbol&quot; type=&quot;line&quot; clip_to_extent=&quot;1&quot; force_rhr=&quot;0&quot;>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;layer class=&quot;SimpleLine&quot; locked=&quot;0&quot; pass=&quot;0&quot; enabled=&quot;1&quot;>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;0&quot; name=&quot;align_dash_pattern&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;square&quot; name=&quot;capstyle&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;5;2&quot; name=&quot;customdash&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;customdash_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;customdash_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;dash_pattern_offset&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;dash_pattern_offset_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;dash_pattern_offset_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;draw_inside_polygon&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;bevel&quot; name=&quot;joinstyle&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;60,60,60,255&quot; name=&quot;line_color&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;solid&quot; name=&quot;line_style&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0.3&quot; name=&quot;line_width&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;line_width_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;offset&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;offset_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;offset_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;ring_filter&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;trim_distance_end&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_end_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;trim_distance_end_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;trim_distance_start&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;trim_distance_start_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;MM&quot; name=&quot;trim_distance_start_unit&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;tweak_dash_pattern_on_corners&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;0&quot; name=&quot;use_custom_dash&quot; type=&quot;QString&quot;/>&lt;Option value=&quot;3x:0,0,0,0,0,0&quot; name=&quot;width_map_unit_scale&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;prop k=&quot;align_dash_pattern&quot; v=&quot;0&quot;/>&lt;prop k=&quot;capstyle&quot; v=&quot;square&quot;/>&lt;prop k=&quot;customdash&quot; v=&quot;5;2&quot;/>&lt;prop k=&quot;customdash_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;customdash_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;dash_pattern_offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;dash_pattern_offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;dash_pattern_offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;draw_inside_polygon&quot; v=&quot;0&quot;/>&lt;prop k=&quot;joinstyle&quot; v=&quot;bevel&quot;/>&lt;prop k=&quot;line_color&quot; v=&quot;60,60,60,255&quot;/>&lt;prop k=&quot;line_style&quot; v=&quot;solid&quot;/>&lt;prop k=&quot;line_width&quot; v=&quot;0.3&quot;/>&lt;prop k=&quot;line_width_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;offset&quot; v=&quot;0&quot;/>&lt;prop k=&quot;offset_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;offset_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;ring_filter&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_end&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_end_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;trim_distance_end_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;trim_distance_start&quot; v=&quot;0&quot;/>&lt;prop k=&quot;trim_distance_start_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;prop k=&quot;trim_distance_start_unit&quot; v=&quot;MM&quot;/>&lt;prop k=&quot;tweak_dash_pattern_on_corners&quot; v=&quot;0&quot;/>&lt;prop k=&quot;use_custom_dash&quot; v=&quot;0&quot;/>&lt;prop k=&quot;width_map_unit_scale&quot; v=&quot;3x:0,0,0,0,0,0&quot;/>&lt;data_defined_properties>&lt;Option type=&quot;Map&quot;>&lt;Option value=&quot;&quot; name=&quot;name&quot; type=&quot;QString&quot;/>&lt;Option name=&quot;properties&quot;/>&lt;Option value=&quot;collection&quot; name=&quot;type&quot; type=&quot;QString&quot;/>&lt;/Option>&lt;/data_defined_properties>&lt;/layer>&lt;/symbol>" name="lineSymbol" type="QString"/>
          <Option value="0" name="minLength" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="minLengthMapUnitScale" type="QString"/>
          <Option value="MM" name="minLengthUnit" type="QString"/>
          <Option value="0" name="offsetFromAnchor" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromAnchorMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromAnchorUnit" type="QString"/>
          <Option value="0" name="offsetFromLabel" type="double"/>
          <Option value="3x:0,0,0,0,0,0" name="offsetFromLabelMapUnitScale" type="QString"/>
          <Option value="MM" name="offsetFromLabelUnit" type="QString"/>
        </Option>
      </callout>
    </settings>
  </labeling>
  <customproperties>
    <Option type="Map">
      <Option name="dualview/previewExpressions" type="List">
        <Option value="&quot;gid&quot;" type="QString"/>
      </Option>
      <Option value="0" name="embeddedWidgets/count" type="QString"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory height="15" backgroundColor="#ffffff" spacingUnit="MM" barWidth="5" sizeType="MM" scaleDependency="Area" minimumSize="0" penColor="#000000" lineSizeScale="3x:0,0,0,0,0,0" enabled="0" spacingUnitScale="3x:0,0,0,0,0,0" showAxis="0" backgroundAlpha="255" labelPlacementMethod="XHeight" lineSizeType="MM" minScaleDenominator="-4.65661e-10" penAlpha="255" maxScaleDenominator="1e+08" penWidth="0" direction="1" rotationOffset="270" scaleBasedVisibility="0" diagramOrientation="Up" spacing="0" opacity="1" width="15" sizeScale="3x:0,0,0,0,0,0">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute label="" field="" color="#000000"/>
      <axisSymbol>
        <symbol alpha="1" name="" type="line" clip_to_extent="1" force_rhr="0">
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
          <layer class="SimpleLine" locked="0" pass="0" enabled="1">
            <Option type="Map">
              <Option value="0" name="align_dash_pattern" type="QString"/>
              <Option value="square" name="capstyle" type="QString"/>
              <Option value="5;2" name="customdash" type="QString"/>
              <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
              <Option value="MM" name="customdash_unit" type="QString"/>
              <Option value="0" name="dash_pattern_offset" type="QString"/>
              <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
              <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
              <Option value="0" name="draw_inside_polygon" type="QString"/>
              <Option value="bevel" name="joinstyle" type="QString"/>
              <Option value="35,35,35,255" name="line_color" type="QString"/>
              <Option value="solid" name="line_style" type="QString"/>
              <Option value="0.26" name="line_width" type="QString"/>
              <Option value="MM" name="line_width_unit" type="QString"/>
              <Option value="0" name="offset" type="QString"/>
              <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
              <Option value="MM" name="offset_unit" type="QString"/>
              <Option value="0" name="ring_filter" type="QString"/>
              <Option value="0" name="trim_distance_end" type="QString"/>
              <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
              <Option value="MM" name="trim_distance_end_unit" type="QString"/>
              <Option value="0" name="trim_distance_start" type="QString"/>
              <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
              <Option value="MM" name="trim_distance_start_unit" type="QString"/>
              <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
              <Option value="0" name="use_custom_dash" type="QString"/>
              <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
            </Option>
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
            <prop k="trim_distance_end" v="0"/>
            <prop k="trim_distance_end_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="trim_distance_end_unit" v="MM"/>
            <prop k="trim_distance_start" v="0"/>
            <prop k="trim_distance_start_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <prop k="trim_distance_start_unit" v="MM"/>
            <prop k="tweak_dash_pattern_on_corners" v="0"/>
            <prop k="use_custom_dash" v="0"/>
            <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
            <data_defined_properties>
              <Option type="Map">
                <Option value="" name="name" type="QString"/>
                <Option name="properties"/>
                <Option value="collection" name="type" type="QString"/>
              </Option>
            </data_defined_properties>
          </layer>
        </symbol>
      </axisSymbol>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings linePlacementFlags="18" dist="0" priority="0" showAll="1" obstacle="0" zIndex="0" placement="2">
    <properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
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
    <field name="branchnum" configurationFlags="None">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="abscissa" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="x" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
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
    <field name="leftminbed" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="rightminbed" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="leftstock" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="rightstock" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="xmnt" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="zmnt" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="active" configurationFlags="None">
      <editWidget type="CheckBox">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="struct" configurationFlags="None">
      <editWidget type="UniqueValues">
        <config>
          <Option type="Map">
            <Option value="false" name="Editable" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="zleftminbed" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="zrightminbed" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="minbedcoef" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" name="IsMultiline" type="bool"/>
            <Option value="false" name="UseHtml" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="majbedcoef" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" name="IsMultiline" type="bool"/>
            <Option value="false" name="UseHtml" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="mesh" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" name="IsMultiline" type="bool"/>
            <Option value="false" name="UseHtml" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="planim" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option type="Map">
            <Option value="false" name="IsMultiline" type="bool"/>
            <Option value="false" name="UseHtml" type="bool"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="leftminbed_g" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="rightminbed_g" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="leftstock_g" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="rightstock_g" configurationFlags="None">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="gid" name="" index="0"/>
    <alias field="name" name="" index="1"/>
    <alias field="branchnum" name="" index="2"/>
    <alias field="abscissa" name="" index="3"/>
    <alias field="x" name="" index="4"/>
    <alias field="z" name="" index="5"/>
    <alias field="leftminbed" name="" index="6"/>
    <alias field="rightminbed" name="" index="7"/>
    <alias field="leftstock" name="" index="8"/>
    <alias field="rightstock" name="" index="9"/>
    <alias field="xmnt" name="" index="10"/>
    <alias field="zmnt" name="" index="11"/>
    <alias field="active" name="" index="12"/>
    <alias field="struct" name="" index="13"/>
    <alias field="zleftminbed" name="" index="14"/>
    <alias field="zrightminbed" name="" index="15"/>
    <alias field="minbedcoef" name="" index="16"/>
    <alias field="majbedcoef" name="" index="17"/>
    <alias field="mesh" name="" index="18"/>
    <alias field="planim" name="" index="19"/>
    <alias field="leftminbed_g" name="" index="20"/>
    <alias field="rightminbed_g" name="" index="21"/>
    <alias field="leftstock_g" name="" index="22"/>
    <alias field="rightstock_g" name="" index="23"/>
  </aliases>
  <defaults>
    <default applyOnUpdate="0" field="gid" expression=""/>
    <default applyOnUpdate="0" field="name" expression=""/>
    <default applyOnUpdate="0" field="branchnum" expression=""/>
    <default applyOnUpdate="0" field="abscissa" expression=""/>
    <default applyOnUpdate="0" field="x" expression=""/>
    <default applyOnUpdate="0" field="z" expression=""/>
    <default applyOnUpdate="0" field="leftminbed" expression=""/>
    <default applyOnUpdate="0" field="rightminbed" expression=""/>
    <default applyOnUpdate="0" field="leftstock" expression=""/>
    <default applyOnUpdate="0" field="rightstock" expression=""/>
    <default applyOnUpdate="0" field="xmnt" expression=""/>
    <default applyOnUpdate="0" field="zmnt" expression=""/>
    <default applyOnUpdate="0" field="active" expression=""/>
    <default applyOnUpdate="0" field="struct" expression="0"/>
    <default applyOnUpdate="0" field="zleftminbed" expression=""/>
    <default applyOnUpdate="0" field="zrightminbed" expression=""/>
    <default applyOnUpdate="0" field="minbedcoef" expression=""/>
    <default applyOnUpdate="0" field="majbedcoef" expression=""/>
    <default applyOnUpdate="0" field="mesh" expression=""/>
    <default applyOnUpdate="0" field="planim" expression=""/>
    <default applyOnUpdate="0" field="leftminbed_g" expression=""/>
    <default applyOnUpdate="0" field="rightminbed_g" expression=""/>
    <default applyOnUpdate="0" field="leftstock_g" expression=""/>
    <default applyOnUpdate="0" field="rightstock_g" expression=""/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" field="gid" unique_strength="1" constraints="3" notnull_strength="1"/>
    <constraint exp_strength="0" field="name" unique_strength="1" constraints="2" notnull_strength="0"/>
    <constraint exp_strength="0" field="branchnum" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="abscissa" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="x" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="z" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="leftminbed" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="rightminbed" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="leftstock" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="rightstock" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="xmnt" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="zmnt" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="active" unique_strength="0" constraints="1" notnull_strength="1"/>
    <constraint exp_strength="0" field="struct" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="zleftminbed" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="zrightminbed" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="minbedcoef" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="majbedcoef" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="mesh" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="planim" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="leftminbed_g" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="rightminbed_g" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="leftstock_g" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="rightstock_g" unique_strength="0" constraints="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="gid"/>
    <constraint exp="" desc="" field="name"/>
    <constraint exp="" desc="" field="branchnum"/>
    <constraint exp="" desc="" field="abscissa"/>
    <constraint exp="" desc="" field="x"/>
    <constraint exp="" desc="" field="z"/>
    <constraint exp="" desc="" field="leftminbed"/>
    <constraint exp="" desc="" field="rightminbed"/>
    <constraint exp="" desc="" field="leftstock"/>
    <constraint exp="" desc="" field="rightstock"/>
    <constraint exp="" desc="" field="xmnt"/>
    <constraint exp="" desc="" field="zmnt"/>
    <constraint exp="" desc="" field="active"/>
    <constraint exp="" desc="" field="struct"/>
    <constraint exp="" desc="" field="zleftminbed"/>
    <constraint exp="" desc="" field="zrightminbed"/>
    <constraint exp="" desc="" field="minbedcoef"/>
    <constraint exp="" desc="" field="majbedcoef"/>
    <constraint exp="" desc="" field="mesh"/>
    <constraint exp="" desc="" field="planim"/>
    <constraint exp="" desc="" field="leftminbed_g"/>
    <constraint exp="" desc="" field="rightminbed_g"/>
    <constraint exp="" desc="" field="leftstock_g"/>
    <constraint exp="" desc="" field="rightstock_g"/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction value="{00000000-0000-0000-0000-000000000000}" key="Canvas"/>
    <actionsetting icon="" action="import os&#xa;&#xa;canvas=qgis.utils.iface.mapCanvas()&#xa;layer=canvas.currentLayer()&#xa;os.chdir(os.path.dirname(QgsProject.instance().fileName()))&#xa;&#xa;import graph&#xa;&#xa;request = QgsFeatureRequest()&#xa;request.setFilterFids([[% $id %]])&#xa;features = layer.getFeatures(request)&#xa;&#xa;for feature in features:&#xa;        print feature.id(), feature&#xa;&#xa;graph.trace_graph(&quot;[% profile %]&quot;,feature,QgsVectorLayer(r&quot;X:\SRNT\DHHPC\Geomatique\MNT\sarthe_amont_2m_mm.tif&quot;,True,2)" capture="0" isEnabledOnlyWhenEditable="0" shortTitle="" id="{89f281eb-bbea-46e0-9201-92c4da05979b}" name="test2" notificationMessage="" type="1">
      <actionScope id="Field"/>
      <actionScope id="Canvas"/>
      <actionScope id="Feature"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="&quot;struct&quot;">
    <columns>
      <column width="-1" name="gid" type="field" hidden="0"/>
      <column width="-1" name="name" type="field" hidden="0"/>
      <column width="-1" name="branchnum" type="field" hidden="0"/>
      <column width="-1" name="abscissa" type="field" hidden="0"/>
      <column width="-1" name="x" type="field" hidden="0"/>
      <column width="-1" name="z" type="field" hidden="0"/>
      <column width="-1" name="leftminbed" type="field" hidden="0"/>
      <column width="-1" name="rightminbed" type="field" hidden="0"/>
      <column width="-1" name="leftstock" type="field" hidden="0"/>
      <column width="-1" name="rightstock" type="field" hidden="0"/>
      <column width="-1" name="xmnt" type="field" hidden="0"/>
      <column width="-1" name="zmnt" type="field" hidden="0"/>
      <column width="-1" name="active" type="field" hidden="0"/>
      <column width="-1" type="actions" hidden="1"/>
      <column width="-1" name="zleftminbed" type="field" hidden="0"/>
      <column width="-1" name="zrightminbed" type="field" hidden="0"/>
      <column width="-1" name="minbedcoef" type="field" hidden="0"/>
      <column width="-1" name="majbedcoef" type="field" hidden="0"/>
      <column width="-1" name="mesh" type="field" hidden="0"/>
      <column width="-1" name="planim" type="field" hidden="0"/>
      <column width="-1" name="leftminbed_g" type="field" hidden="0"/>
      <column width="-1" name="rightminbed_g" type="field" hidden="0"/>
      <column width="-1" name="leftstock_g" type="field" hidden="0"/>
      <column width="-1" name="rightstock_g" type="field" hidden="0"/>
      <column width="-1" name="struct" type="field" hidden="0"/>
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
    <attributeEditorContainer groupBox="0" visibilityExpression="" name="infos" showLabel="1" visibilityExpressionEnabled="0" columnCount="0">
      <attributeEditorField name="name" showLabel="1" index="1"/>
      <attributeEditorField name="minbedcoef" showLabel="1" index="16"/>
      <attributeEditorField name="majbedcoef" showLabel="1" index="17"/>
      <attributeEditorField name="mesh" showLabel="1" index="18"/>
      <attributeEditorField name="planim" showLabel="1" index="19"/>
      <attributeEditorField name="active" showLabel="1" index="12"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <editable>
    <field editable="1" name="abscissa"/>
    <field editable="1" name="active"/>
    <field editable="1" name="branchnum"/>
    <field editable="1" name="gid"/>
    <field editable="1" name="leftminbed"/>
    <field editable="1" name="leftminbed_g"/>
    <field editable="1" name="leftstock"/>
    <field editable="1" name="leftstock_g"/>
    <field editable="1" name="majbedcoef"/>
    <field editable="1" name="mesh"/>
    <field editable="1" name="minbedcoef"/>
    <field editable="1" name="name"/>
    <field editable="1" name="planim"/>
    <field editable="1" name="rightminbed"/>
    <field editable="1" name="rightminbed_g"/>
    <field editable="1" name="rightstock"/>
    <field editable="1" name="rightstock_g"/>
    <field editable="1" name="struct"/>
    <field editable="1" name="x"/>
    <field editable="1" name="xmnt"/>
    <field editable="1" name="z"/>
    <field editable="1" name="zleftminbed"/>
    <field editable="1" name="zmnt"/>
    <field editable="1" name="zrightminbed"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="abscissa"/>
    <field labelOnTop="0" name="active"/>
    <field labelOnTop="0" name="branchnum"/>
    <field labelOnTop="0" name="gid"/>
    <field labelOnTop="0" name="leftminbed"/>
    <field labelOnTop="0" name="leftminbed_g"/>
    <field labelOnTop="0" name="leftstock"/>
    <field labelOnTop="0" name="leftstock_g"/>
    <field labelOnTop="0" name="majbedcoef"/>
    <field labelOnTop="0" name="mesh"/>
    <field labelOnTop="0" name="minbedcoef"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="planim"/>
    <field labelOnTop="0" name="rightminbed"/>
    <field labelOnTop="0" name="rightminbed_g"/>
    <field labelOnTop="0" name="rightstock"/>
    <field labelOnTop="0" name="rightstock_g"/>
    <field labelOnTop="0" name="struct"/>
    <field labelOnTop="0" name="x"/>
    <field labelOnTop="0" name="xmnt"/>
    <field labelOnTop="0" name="z"/>
    <field labelOnTop="0" name="zleftminbed"/>
    <field labelOnTop="0" name="zmnt"/>
    <field labelOnTop="0" name="zrightminbed"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="abscissa"/>
    <field reuseLastValue="0" name="active"/>
    <field reuseLastValue="0" name="branchnum"/>
    <field reuseLastValue="0" name="gid"/>
    <field reuseLastValue="0" name="leftminbed"/>
    <field reuseLastValue="0" name="leftminbed_g"/>
    <field reuseLastValue="0" name="leftstock"/>
    <field reuseLastValue="0" name="leftstock_g"/>
    <field reuseLastValue="0" name="majbedcoef"/>
    <field reuseLastValue="0" name="mesh"/>
    <field reuseLastValue="0" name="minbedcoef"/>
    <field reuseLastValue="0" name="name"/>
    <field reuseLastValue="0" name="planim"/>
    <field reuseLastValue="0" name="rightminbed"/>
    <field reuseLastValue="0" name="rightminbed_g"/>
    <field reuseLastValue="0" name="rightstock"/>
    <field reuseLastValue="0" name="rightstock_g"/>
    <field reuseLastValue="0" name="struct"/>
    <field reuseLastValue="0" name="x"/>
    <field reuseLastValue="0" name="xmnt"/>
    <field reuseLastValue="0" name="z"/>
    <field reuseLastValue="0" name="zleftminbed"/>
    <field reuseLastValue="0" name="zmnt"/>
    <field reuseLastValue="0" name="zrightminbed"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"gid"</previewExpression>
  <mapTip>profile</mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
