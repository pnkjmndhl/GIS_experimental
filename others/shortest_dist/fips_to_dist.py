# creates links between given FIPS to calculate distance
import arcpy
import pandas

# takes time but works like charm

arcpy.env.overwriteOutput = True  # overwrite files if its already present

alllinks = "../shp/NHP/nhp_dissolved/nhp.shp"
fips = 'C:/Users/pankaj/Desktop/RAIL/gis/standards/FIPS.shp'

#road network with length and speed limit
networkDataset = "../shp/NHP/nhpnv14-05shp/NHPNLine_ND"
arcpy.CalculateField_management(alllinks, "Length", '!Shape.length@miles!', "PYTHON")

snapped_dumm = "C:\GIS\deletethis1.shp"

# snap FIPS to nearest links
arcpy.Copy_management(fips, snapped_dumm)
arcpy.Snap_edit(snapped_dumm, [[alllinks, "EDGE", "100 Miles"]])

# update the network dataset if required (this is not required generally)
ND = "../shp/NHP/nhp_dissolved/NHP_ND.nd"
feature = "C:/GIS/temp.shp"  # i guess this is just a temporary layer/ no worries
arcpy.MakeRouteLayer_na(ND, "Route", "Length")

snapped_nodes = "allnodes_Snapped_rail2.shp"
sumlayer = "C:/GIS/temptemptemp.shp"
templayer = "C:/GIS/temp1.shp"

emptyshapefile = "C:/GIS/empty.shp"

o = "C:/GIS/o.shp"  # temporary files
d = "C:/GIS/d.shp"
m = "C:/GIS/m.shp"


def get_dist_AB(fips_a, fips_b):
    #print ("ArgGIS analyst: Job Received, ONODE: {0}, DNODE: {1} *".format(fips_a, fips_b))
    arcpy.CheckOutExtension("Network")
    arcpy.Select_analysis(snapped_dumm, o, 'FIPS = {0}'.format(fips_a))
    arcpy.Select_analysis(snapped_dumm, d, 'FIPS = {0}'.format(fips_b))
    arcpy.Merge_management([o, d], m)
    arcpy.AddLocations_na("Route", "Stops", m, "Name Name #", "5000 Kilometers", "", "B1 SHAPE;B1_ND_Junctions SHAPE",
                          "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "INCLUDE", "B1 #;B1_ND_Junctions #")
    try:
        arcpy.Solve_na("Route", "SKIP", "TERMINATE", "500 Kilometers")
        arcpy.SelectData_management("Route", "Routes")
        arcpy.FeatureToLine_management("Route/Routes", feature, "", "ATTRIBUTES")
    except:
        print ("Route not found. 999999 Returned")
        return -99
    dummy = [row.getValue("Total_Leng") for row in arcpy.SearchCursor(feature)][0]
    return dummy * 0.000621371



OD = pandas.ExcelFile("GNBC 2017 Traffic OD Test1.xlsx").parse("GNBC 2017 Traffic")
name_to_FIPS_df = pandas.ExcelFile("FIPS.xls").parse("FIPS")
name_to_FIPS_df.columns = ["FIPS", "COUNTY", "STATE"]
name_to_FIPS_df["mapper"]=name_to_FIPS_df["COUNTY"].astype(str)+","+name_to_FIPS_df["STATE"].astype(str)
name_to_FIPS_df = name_to_FIPS_df.set_index("mapper")
name_to_FIPS_df = name_to_FIPS_df["FIPS"]
county_to_fips_dict = name_to_FIPS_df.to_dict()

OD["OFIPS"] = OD['Ostate'].map(county_to_fips_dict)
OD["DFIPS"] = OD['Dstate'].map(county_to_fips_dict)


OD = OD.fillna(0)


for i in range(len(OD)):
    origin = int(OD["OFIPS"][i])
    destination = int(OD["DFIPS"][i])
    time, distance = get_dist_AB(origin,destination)
    print("{0}->{1}:{2}".format(origin,destination,distance))
    OD["dist"][i] = distance

OD.to_csv("aaa.csv",encoding='utf-8-sig')