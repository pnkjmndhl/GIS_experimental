import arcpy
import pandas
import csv
from merge import *


arcpy.env.overwriteOutput = True

# shapefiles
other = "./intermediate/NARN_LINE_03162018.shp"
other_f = "other_f"
arcpy.MakeFeatureLayer_management(other, other_f)



def import_dict_from_csv(filename):
    data = pandas.read_csv(filename)
    no_of_columns = len(data.columns)
    if no_of_columns == 2:
        datadict = {int(column[0]): [column[1]] for index, column in data.iterrows()}
    elif no_of_columns == 3:
        datadict = {int(column[0]): [column[1], column[2]] for index, column in data.iterrows()}
    else:
        print("number of columns exceeded")
    return datadict


# read from csv files to a dict
route_not_found_dict = import_dict_from_csv("noroutes.csv")
route_tolerance_exceed_dict = import_dict_from_csv("notolerance.csv")
route_buffer_exceed_dict = import_dict_from_csv("notolerancebuffer.csv")


def get_where_clause(colname, list_of_link_ids):
    wh_cl = ""
    for id in list_of_link_ids:
        wh_cl = wh_cl + """"{0}" = {1} OR """.format(colname, id)
    return wh_cl[:-4]


# create no_route_shp
where_clause = get_where_clause("_ID_", route_not_found_dict.keys())
arcpy.SelectLayerByAttribute_management(other_f, "NEW_SELECTION", where_clause)
arcpy.CopyFeatures_management(other_f, output_no_routes_shp)

# create no_tolerance_within_buffer shp
route_within_threshold_dict = {x: y for x, y in route_tolerance_exceed_dict.iteritems() if
                               (abs(y[0] - y[1]) / y[1]) > threshold / 100}
where_clause = get_where_clause("_ID_", route_within_threshold_dict.keys())
arcpy.SelectLayerByAttribute_management(other_f, "NEW_SELECTION", where_clause)
arcpy.CopyFeatures_management(other_f, output_tolerance_exceed_shp)
arcpy.AddField_management(output_tolerance_exceed_shp, '_RLENG_', "FLOAT")
with arcpy.da.UpdateCursor(output_tolerance_exceed_shp, ['_ID_', '_RLENG_']) as cursor:
    for row in cursor:
        row[1] = route_within_threshold_dict[row[0]][0]
        cursor.updateRow(row)

# create no_tolerance_shp
route_buffer_within_threshold_dict = {x: y for x, y in route_buffer_exceed_dict.iteritems() if
                                      (abs(y[0] - y[1]) / y[1]) > threshold / 100}
where_clause = get_where_clause("_ID_", route_buffer_within_threshold_dict.keys())
arcpy.SelectLayerByAttribute_management(other_f, "NEW_SELECTION", where_clause)
arcpy.CopyFeatures_management(other_f, output_buffer_tolerance_exceed_shp)
arcpy.AddField_management(output_buffer_tolerance_exceed_shp, '_RLENG_', "FLOAT")
with arcpy.da.UpdateCursor(output_buffer_tolerance_exceed_shp, ['_ID_', '_RLENG_']) as cursor:
    for row in cursor:
        row[1] = route_buffer_within_threshold_dict[row[0]][0]
        cursor.updateRow(row)