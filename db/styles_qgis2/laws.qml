<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.18" minimumScale="-4.65661e-10" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="id">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="name">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="DateTime" name="starttime">
      <widgetv2config fieldEditable="1" calendar_popup="1" allow_null="0" display_format="dd/MM/yyyy HH:mm:ss" field_format="yyyy-MM-dd HH:mm:ss" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="DateTime" name="endtime">
      <widgetv2config fieldEditable="1" calendar_popup="1" allow_null="0" display_format="dd/MM/yyyy HH:mm:ss" field_format="yyyy-MM-dd HH:mm:ss" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="H">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="ValueMap" name="type">
      <widgetv2config fieldEditable="1" labelOnTop="0">
        <value key="Rating curve Q=f(Z)" value="5"/>
        <value key="Rating curve Z=f(Q)" value="4"/>
        <value key="Hydrograph Q(t)" value="1"/>
        <value key="limnigraph Z(t)" value="2"/>
        <value key="Limnihydrograph Z,Q(t)" value="3"/>
        <value key="Weir Zam=f(Q,Zav)" value="6"/>
        <value key="Floodgate Zinf,Zsup=f(t)" value="7"/>
      </widgetv2config>
    </edittype>
    <edittype widgetv2type="TextEdit" name="flowrate">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="time">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="z_upstream">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="z_downstream">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="z_lower">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="z_up">
      <widgetv2config IsMultiline="0" fieldEditable="1" UseHtml="0" labelOnTop="0"/>
    </edittype>
  </edittypes>
  <editform>.</editform>
  <editforminit></editforminit>
  <featformsuppress>0</featformsuppress>
  <annotationform>.</annotationform>
  <editorlayout>tablayout</editorlayout>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeEditorForm>
    <attributeEditorContainer name="infos">
      <attributeEditorField index="1" name="name"/>
      <attributeEditorField index="2" name="starttime"/>
      <attributeEditorField index="3" name="endtime"/>
      <attributeEditorField index="5" name="type"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Tarage">
      <attributeEditorField index="4" name="z"/>
      <attributeEditorField index="6" name="flowrate"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Limnigraph">
      <attributeEditorField index="7" name="time"/>
      <attributeEditorField index="4" name="z"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Hydrograph">
      <attributeEditorField index="7" name="time"/>
      <attributeEditorField index="6" name="flowrate"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Limnihydrograph">
      <attributeEditorField index="7" name="time"/>
      <attributeEditorField index="4" name="z"/>
      <attributeEditorField index="6" name="flowrate"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Weir law">
      <attributeEditorField index="9" name="z_downstream"/>
      <attributeEditorField index="6" name="flowrate"/>
      <attributeEditorField index="8" name="z_upstream"/>
    </attributeEditorContainer>
    <attributeEditorContainer name="Floodgate law">
      <attributeEditorField index="7" name="time"/>
      <attributeEditorField index="10" name="z_lower"/>
      <attributeEditorField index="11" name="z_up"/>
    </attributeEditorContainer>
  </attributeEditorForm>
  <attributeactions/>
</qgis>
