<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.16.3" simplifyAlgorithm="0" minimumScale="100000" maximumScale="200000" simplifyDrawingHints="0" minLabelScale="0" maxLabelScale="1e+08" simplifyDrawingTol="1" simplifyMaxScale="1" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" scaleBasedLabelVisibilityFlag="0">
  <edittypes>
    <edittype widgetv2type="TextEdit" name="gid">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="name">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="basinnum">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="initlevel">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="level">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="area">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="TextEdit" name="volume">
      <widgetv2config IsMultiline="0" fieldEditable="1" constraint="" UseHtml="0" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
    <edittype widgetv2type="CheckBox" name="active">
      <widgetv2config fieldEditable="1" UncheckedState="f" constraint="" CheckedState="t" labelOnTop="0" constraintDescription="" notNull="0"/>
    </edittype>
  </edittypes>
  <renderer-v2 attr="active" forceraster="0" symbollevels="0" type="categorizedSymbol" enableorderby="0">
    <categories>
      <category render="true" symbol="0" value="t" label="Active"/>
      <category render="true" symbol="1" value="f" label="Inactive"/>
    </categories>
    <symbols>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="0">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="51,172,208,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
        </layer>
      </symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="1">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
        </layer>
      </symbol>
    </symbols>
    <source-symbol>
      <symbol alpha="1" clip_to_extent="1" type="fill" name="0">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="border_width_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="color" v="152,81,14,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
        </layer>
      </symbol>
    </source-symbol>
    <colorramp type="gradient" name="[source]">
      <prop k="color1" v="255,255,204,255"/>
      <prop k="color2" v="37,52,148,255"/>
      <prop k="discrete" v="0"/>
      <prop k="stops" v="0.25;161,218,180,255:0.5;65,182,196,255:0.75;44,127,184,255"/>
    </colorramp>
    <invertedcolorramp value="0"/>
    <rotation/>
    <sizescale scalemethod="diameter"/>
  </renderer-v2>
  <labeling type="simple"/>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="labeling" value="pal"/>
    <property key="labeling/addDirectionSymbol" value="false"/>
    <property key="labeling/angleOffset" value="0"/>
    <property key="labeling/blendMode" value="0"/>
    <property key="labeling/bufferBlendMode" value="0"/>
    <property key="labeling/bufferColorA" value="255"/>
    <property key="labeling/bufferColorB" value="255"/>
    <property key="labeling/bufferColorG" value="255"/>
    <property key="labeling/bufferColorR" value="255"/>
    <property key="labeling/bufferDraw" value="false"/>
    <property key="labeling/bufferJoinStyle" value="64"/>
    <property key="labeling/bufferNoFill" value="false"/>
    <property key="labeling/bufferSize" value="1"/>
    <property key="labeling/bufferSizeInMapUnits" value="false"/>
    <property key="labeling/bufferSizeMapUnitMaxScale" value="0"/>
    <property key="labeling/bufferSizeMapUnitMinScale" value="0"/>
    <property key="labeling/bufferSizeMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/bufferTransp" value="0"/>
    <property key="labeling/centroidInside" value="false"/>
    <property key="labeling/centroidWhole" value="false"/>
    <property key="labeling/decimals" value="3"/>
    <property key="labeling/displayAll" value="false"/>
    <property key="labeling/dist" value="0"/>
    <property key="labeling/distInMapUnits" value="false"/>
    <property key="labeling/distMapUnitMaxScale" value="0"/>
    <property key="labeling/distMapUnitMinScale" value="0"/>
    <property key="labeling/distMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/drawLabels" value="true"/>
    <property key="labeling/enabled" value="true"/>
    <property key="labeling/fieldName" value="name"/>
    <property key="labeling/fitInPolygonOnly" value="false"/>
    <property key="labeling/fontBold" value="false"/>
    <property key="labeling/fontCapitals" value="0"/>
    <property key="labeling/fontFamily" value="MS Shell Dlg 2"/>
    <property key="labeling/fontItalic" value="false"/>
    <property key="labeling/fontLetterSpacing" value="0"/>
    <property key="labeling/fontLimitPixelSize" value="false"/>
    <property key="labeling/fontMaxPixelSize" value="10000"/>
    <property key="labeling/fontMinPixelSize" value="3"/>
    <property key="labeling/fontSize" value="8.25"/>
    <property key="labeling/fontSizeInMapUnits" value="false"/>
    <property key="labeling/fontSizeMapUnitMaxScale" value="0"/>
    <property key="labeling/fontSizeMapUnitMinScale" value="0"/>
    <property key="labeling/fontSizeMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/fontStrikeout" value="false"/>
    <property key="labeling/fontUnderline" value="false"/>
    <property key="labeling/fontWeight" value="50"/>
    <property key="labeling/fontWordSpacing" value="0"/>
    <property key="labeling/formatNumbers" value="false"/>
    <property key="labeling/isExpression" value="false"/>
    <property key="labeling/labelOffsetInMapUnits" value="true"/>
    <property key="labeling/labelOffsetMapUnitMaxScale" value="0"/>
    <property key="labeling/labelOffsetMapUnitMinScale" value="0"/>
    <property key="labeling/labelOffsetMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/labelPerPart" value="false"/>
    <property key="labeling/leftDirectionSymbol" value="&lt;"/>
    <property key="labeling/limitNumLabels" value="false"/>
    <property key="labeling/maxCurvedCharAngleIn" value="20"/>
    <property key="labeling/maxCurvedCharAngleOut" value="-20"/>
    <property key="labeling/maxNumLabels" value="2000"/>
    <property key="labeling/mergeLines" value="false"/>
    <property key="labeling/minFeatureSize" value="0"/>
    <property key="labeling/multilineAlign" value="0"/>
    <property key="labeling/multilineHeight" value="1"/>
    <property key="labeling/namedStyle" value="Normal"/>
    <property key="labeling/obstacle" value="true"/>
    <property key="labeling/obstacleFactor" value="1"/>
    <property key="labeling/obstacleType" value="0"/>
    <property key="labeling/offsetType" value="0"/>
    <property key="labeling/placeDirectionSymbol" value="0"/>
    <property key="labeling/placement" value="0"/>
    <property key="labeling/placementFlags" value="0"/>
    <property key="labeling/plussign" value="false"/>
    <property key="labeling/predefinedPositionOrder" value="TR,TL,BR,BL,R,L,TSR,BSR"/>
    <property key="labeling/preserveRotation" value="true"/>
    <property key="labeling/previewBkgrdColor" value="#ffffff"/>
    <property key="labeling/priority" value="5"/>
    <property key="labeling/quadOffset" value="4"/>
    <property key="labeling/repeatDistance" value="0"/>
    <property key="labeling/repeatDistanceMapUnitMaxScale" value="0"/>
    <property key="labeling/repeatDistanceMapUnitMinScale" value="0"/>
    <property key="labeling/repeatDistanceMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/repeatDistanceUnit" value="1"/>
    <property key="labeling/reverseDirectionSymbol" value="false"/>
    <property key="labeling/rightDirectionSymbol" value=">"/>
    <property key="labeling/scaleMax" value="10000000"/>
    <property key="labeling/scaleMin" value="1"/>
    <property key="labeling/scaleVisibility" value="false"/>
    <property key="labeling/shadowBlendMode" value="6"/>
    <property key="labeling/shadowColorB" value="0"/>
    <property key="labeling/shadowColorG" value="0"/>
    <property key="labeling/shadowColorR" value="0"/>
    <property key="labeling/shadowDraw" value="false"/>
    <property key="labeling/shadowOffsetAngle" value="135"/>
    <property key="labeling/shadowOffsetDist" value="1"/>
    <property key="labeling/shadowOffsetGlobal" value="true"/>
    <property key="labeling/shadowOffsetMapUnitMaxScale" value="0"/>
    <property key="labeling/shadowOffsetMapUnitMinScale" value="0"/>
    <property key="labeling/shadowOffsetMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shadowOffsetUnits" value="1"/>
    <property key="labeling/shadowRadius" value="1.5"/>
    <property key="labeling/shadowRadiusAlphaOnly" value="false"/>
    <property key="labeling/shadowRadiusMapUnitMaxScale" value="0"/>
    <property key="labeling/shadowRadiusMapUnitMinScale" value="0"/>
    <property key="labeling/shadowRadiusMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shadowRadiusUnits" value="1"/>
    <property key="labeling/shadowScale" value="100"/>
    <property key="labeling/shadowTransparency" value="30"/>
    <property key="labeling/shadowUnder" value="0"/>
    <property key="labeling/shapeBlendMode" value="0"/>
    <property key="labeling/shapeBorderColorA" value="255"/>
    <property key="labeling/shapeBorderColorB" value="128"/>
    <property key="labeling/shapeBorderColorG" value="128"/>
    <property key="labeling/shapeBorderColorR" value="128"/>
    <property key="labeling/shapeBorderWidth" value="0"/>
    <property key="labeling/shapeBorderWidthMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeBorderWidthMapUnitMinScale" value="0"/>
    <property key="labeling/shapeBorderWidthMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeBorderWidthUnits" value="1"/>
    <property key="labeling/shapeDraw" value="false"/>
    <property key="labeling/shapeFillColorA" value="255"/>
    <property key="labeling/shapeFillColorB" value="255"/>
    <property key="labeling/shapeFillColorG" value="255"/>
    <property key="labeling/shapeFillColorR" value="255"/>
    <property key="labeling/shapeJoinStyle" value="64"/>
    <property key="labeling/shapeOffsetMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeOffsetMapUnitMinScale" value="0"/>
    <property key="labeling/shapeOffsetMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeOffsetUnits" value="1"/>
    <property key="labeling/shapeOffsetX" value="0"/>
    <property key="labeling/shapeOffsetY" value="0"/>
    <property key="labeling/shapeRadiiMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeRadiiMapUnitMinScale" value="0"/>
    <property key="labeling/shapeRadiiMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeRadiiUnits" value="1"/>
    <property key="labeling/shapeRadiiX" value="0"/>
    <property key="labeling/shapeRadiiY" value="0"/>
    <property key="labeling/shapeRotation" value="0"/>
    <property key="labeling/shapeRotationType" value="0"/>
    <property key="labeling/shapeSVGFile" value=""/>
    <property key="labeling/shapeSizeMapUnitMaxScale" value="0"/>
    <property key="labeling/shapeSizeMapUnitMinScale" value="0"/>
    <property key="labeling/shapeSizeMapUnitScale" value="0,0,0,0,0,0"/>
    <property key="labeling/shapeSizeType" value="0"/>
    <property key="labeling/shapeSizeUnits" value="1"/>
    <property key="labeling/shapeSizeX" value="0"/>
    <property key="labeling/shapeSizeY" value="0"/>
    <property key="labeling/shapeTransparency" value="0"/>
    <property key="labeling/shapeType" value="0"/>
    <property key="labeling/textColorA" value="255"/>
    <property key="labeling/textColorB" value="0"/>
    <property key="labeling/textColorG" value="0"/>
    <property key="labeling/textColorR" value="0"/>
    <property key="labeling/textTransp" value="0"/>
    <property key="labeling/upsidedownLabels" value="0"/>
    <property key="labeling/wrapChar" value=""/>
    <property key="labeling/xOffset" value="0"/>
    <property key="labeling/yOffset" value="0"/>
    <property key="labeling/zIndex" value="0"/>
    <property key="variableNames" value="_fields_"/>
    <property key="variableValues" value=""/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerTransparency>0</layerTransparency>
  <displayfield>branch</displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Label"/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <SingleCategoryDiagramRenderer diagramType="Histogram" sizeLegend="0" attributeLegend="1">
    <DiagramCategory penColor="#000000" labelPlacementMethod="XHeight" penWidth="0" diagramOrientation="Up" sizeScale="0,0,0,0,0,0" minimumSize="0" barWidth="5" penAlpha="255" maxScaleDenominator="200000" backgroundColor="#ffffff" transparency="0" width="15" scaleDependency="Area" backgroundAlpha="255" angleOffset="1440" scaleBasedVisibility="1" enabled="0" height="15" lineSizeScale="0,0,0,0,0,0" sizeType="MM" lineSizeType="MM" minScaleDenominator="100000">
      <fontProperties description="MS Shell Dlg 2,8.25,-1,5,50,0,0,0,0,0" style=""/>
      <attribute field="" color="#000000" label=""/>
    </DiagramCategory>
    <symbol alpha="1" clip_to_extent="1" type="marker" name="sizeSymbol">
      <layer pass="0" class="SimpleMarker" locked="0">
        <prop k="angle" v="0"/>
        <prop k="color" v="255,0,0,255"/>
        <prop k="horizontal_anchor_point" v="1"/>
        <prop k="joinstyle" v="bevel"/>
        <prop k="name" v="circle"/>
        <prop k="offset" v="0,0"/>
        <prop k="offset_map_unit_scale" v="0,0,0,0,0,0"/>
        <prop k="offset_unit" v="MM"/>
        <prop k="outline_color" v="0,0,0,255"/>
        <prop k="outline_style" v="solid"/>
        <prop k="outline_width" v="0"/>
        <prop k="outline_width_map_unit_scale" v="0,0,0,0,0,0"/>
        <prop k="outline_width_unit" v="MM"/>
        <prop k="scale_method" v="diameter"/>
        <prop k="size" v="2"/>
        <prop k="size_map_unit_scale" v="0,0,0,0,0,0"/>
        <prop k="size_unit" v="MM"/>
        <prop k="vertical_anchor_point" v="1"/>
      </layer>
    </symbol>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings yPosColumn="-1" showColumn="-1" linePlacementFlags="10" placement="0" dist="0" xPosColumn="-1" priority="0" obstacle="0" zIndex="0" showAll="1"/>
  <annotationform>PROGRA~2/QGIS_2.6/profil/python/plugins/MascPlug/mascaret</annotationform>
  <aliases>
    <alias field="active" index="7" name="Active"/>
    <alias field="area" index="5" name="Area (m2)"/>
    <alias field="basinnum" index="2" name="Basin number"/>
    <alias field="initlevel" index="3" name="Reference level (m)"/>
    <alias field="level" index="4" name="Level (m)"/>
    <alias field="name" index="1" name="Name"/>
    <alias field="volume" index="6" name="Volume (m3)"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeactions default="0">
    <actionsetting showInAttributeTable="0" action="from qgis.utils import iface&#xd;&#xa;from qgis.gui import QgsMessageBar&#xd;&#xa;import processing&#xd;&#xa;&#xd;&#xa;# Initialisation des parametres pour le calcul des courbes hypsometriques&#xd;&#xa;nom_MNT = 'DEM_basins' #couche raster MNT&#xd;&#xa;nom_casiers = 'basins' # couche vectorielle des casiers&#xd;&#xa;delta_z = 1 # loi surface volume tous les metres&#xd;&#xa;sortie = None # fichiers resultats dans repertoire users/Appdata/Local/temp&#xd;&#xa;&#xd;&#xa;# couches Qgis&#xd;&#xa;existence_couches = True&#xd;&#xa;try:&#xd;&#xa;&#x9;couche_MNT = QgsMapLayerRegistry.instance().mapLayersByName(nom_MNT)[0]&#xd;&#xa;except:&#xd;&#xa;&#x9;#print('DEM pas trouvé')&#xd;&#xa;&#x9;iface.messageBar().pushMessage('','no DEM_basins layer found', QgsMessageBar.WARNING, 3)&#xd;&#xa;&#x9;existence_couches = False&#xd;&#xa;&#xd;&#xa;try:&#xd;&#xa;&#x9;couche_basins = QgsMapLayerRegistry.instance().mapLayersByName(nom_casiers)[0]&#xd;&#xa;except:&#xd;&#xa;&#x9;#print('basins pas trouvé')&#xd;&#xa;&#x9;iface.messageBar().pushMessage('','no basins layer found', QgsMessageBar.WARNING, 3)&#xd;&#xa;&#x9;existence_couches = False&#xd;&#xa;&#xd;&#xa;# Generation de la loi surface volume&#xd;&#xa;if existence_couches:&#xd;&#xa;&#x9;# Execution de l'algorithme QGis de courbes hypsometriques &#xd;&#xa;&#x9;resultat = processing.runalg(&quot;qgis:hypsometriccurves&quot;,nom_MNT,nom_casiers,delta_z,False,sortie)&#xd;&#xa;&#x9;resultat_chemin = resultat['OUTPUT_DIRECTORY']&#xd;&#xa;&#x9;#print(resultat_chemin)&#xd;&#xa;&#x9;&#xd;&#xa;&#x9;# Traitement des casiers selectionnes&#xd;&#xa;&#x9;features = couche_basins.selectedFeatures()&#xd;&#xa;&#x9;if features == []:&#xd;&#xa;&#x9;&#x9;iface.messageBar().pushMessage('','no selected features in basins layer', QgsMessageBar.WARNING, 3)&#xd;&#xa;&#x9;else:&#xd;&#xa;&#x9;&#x9;couche_basins.startEditing()&#xd;&#xa;&#x9;&#x9;for feature in features:&#xd;&#xa;&#x9;&#x9;&#x9;id = feature.id() # gid du casier&#xd;&#xa;&#x9;&#x9;&#x9;nom_fichier = 'hystogram_basins_'+str(id)+'.csv'&#xd;&#xa;&#x9;&#x9;&#x9;chemin_fichier = resultat_chemin+'\\'+nom_fichier&#xd;&#xa;&#x9;&#x9;&#x9;lignes = []&#xd;&#xa;&#x9;&#x9;&#x9;try:&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;fichier = open(chemin_fichier,'r')&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;fichier.readline() # entete&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;lignes = fichier.readlines() # lignes surface, elevation&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;fichier.close()&#xd;&#xa;&#x9;&#x9;&#x9;except IOError:&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;#print('no DEM found for Basin gid:'+str(id))&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;iface.messageBar().pushMessage('','no DEM found for Basin gid:'+str(id), QgsMessageBar.WARNING, 3)&#xd;&#xa;&#x9;&#x9;&#xd;&#xa;&#x9;&#x9;&#x9;# Calcul du volume&#xd;&#xa;&#x9;&#x9;&#x9;if lignes &lt;>[]:&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;# initialisation&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;volume = 0&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;delta_z = 1.0 # metre&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;surface_inf = 0&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;surface_sup = 0&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;liste_Z =[]&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;liste_S = []&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;liste_V = []&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;index = 0&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;z = 0&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;# Traitement&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;for ligne in lignes:&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;chaine = ligne.split(',')&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;surface_inf = surface_sup&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;surface_sup = float(chaine[0])&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;if index ==0:&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;&#x9;z = float(chaine[1])&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;&#x9;volume = 0&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;else:&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;&#x9;z += delta_z&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;&#x9;# Ajout du volume elementaire calcule sur la surface moyenne&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;&#x9;volume += delta_z*(surface_sup+surface_inf)/2&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;# Listes pour la loi surface-volume&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;liste_Z.append(&quot;%0.2f&quot; %z)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;liste_S.append(&quot;%0.0f&quot; %surface_sup)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;liste_V.append(&quot;%0.0f&quot; %volume)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;#print(liste_Z)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;#print(liste_S)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;#print(liste_V)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#x9;index +=1&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;# Ecriture de la loi surface-volume&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;feature['level']=' '.join(liste_Z)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;feature['area']=' '.join(liste_S)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;feature['volume']=' '.join(liste_V)&#xd;&#xa;&#x9;&#x9;&#x9;&#x9;couche_basins.updateFeature(feature)&#xd;&#xa;&#x9;&#xd;&#xa;&#x9;&#x9;# Commit et fin de l'edition&#xd;&#xa;&#x9;&#x9;couche_basins.commitChanges()&#xd;&#xa;&#x9;&#x9;#print('loi surface volume calculee')&#xd;&#xa;&#x9;&#x9;iface.messageBar().pushMessage('','water storage relationship generated', QgsMessageBar.SUCCESS, 3)&#xd;&#xa;&#xd;&#xa;&#xd;&#xa;&#x9;&#x9;&#xd;&#xa;" icon="" capture="0" type="1" name="Generate water storage relationship" shortTitle=""/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="COALESCE(&quot;branch&quot;, '&lt;NULL>')" sortOrder="0">
    <columns>
      <column width="337" hidden="0" type="field" name="gid"/>
      <column width="-1" hidden="0" type="field" name="name"/>
      <column width="-1" hidden="0" type="field" name="basinnum"/>
      <column width="-1" hidden="0" type="field" name="initlevel"/>
      <column width="27" hidden="0" type="field" name="level"/>
      <column width="27" hidden="0" type="field" name="area"/>
      <column width="1323" hidden="0" type="field" name="volume"/>
      <column width="-1" hidden="0" type="field" name="active"/>
      <column width="-1" hidden="1" type="actions"/>
    </columns>
  </attributetableconfig>
  <editform>PROGRA~2/QGIS_2.6/profil/python/plugins/MascPlug/mascaret</editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath>../../../Program Files/QGIS/bin</editforminitfilepath>
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
    <attributeEditorContainer name="Basin" groupBox="0" columnCount="1">
      <attributeEditorField index="1" name="name"/>
      <attributeEditorField index="2" name="basinnum"/>
      <attributeEditorField index="3" name="initlevel"/>
      <attributeEditorField index="7" name="active"/>
      <attributeEditorContainer name="Water storage relationship" groupBox="1" columnCount="1">
        <attributeEditorField index="4" name="level"/>
        <attributeEditorField index="5" name="area"/>
        <attributeEditorField index="6" name="volume"/>
      </attributeEditorContainer>
    </attributeEditorContainer>
  </attributeEditorForm>
  <widgets>
    <widget name="R_basin_link">
      <config/>
    </widget>
  </widgets>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <layerGeometryType>2</layerGeometryType>
</qgis>
