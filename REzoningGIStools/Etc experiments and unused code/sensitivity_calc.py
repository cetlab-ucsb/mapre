import pandas
import os
import glob

templatefile = pandas.read_csv("sitesuitability_solar_airports.csv", header=None, sep=",")
templatefile = templatefile.transpose()
templatefile.columns = templatefile.iloc[0]
templatefile = templatefile[1:]
templatefile = templatefile.sort_values('Subregions').reset_index()

total = templatefile['total']
total = total.astype(float)

directory = (r"R:\users\anagha.uppal\MapRE\REzoningGIStools_v1_6\REzoningGIStools_v1_6\sitesuitability_constraint")
for filename in os.listdir(directory):
    if filename.endswith(".csv") and filename != "sitesuitability_solar_airports.csv" and filename != "combined_sitesuitability.csv":
        print("filename is :", filename)
        addfile = pandas.read_csv(filename, header=None, sep=",",skiprows=1)
        addfile = addfile.transpose()
        addfile.columns = addfile.iloc[0]
        addfile = addfile[1:]
        addfile = addfile.sort_values('Subregions').reset_index()
        area = addfile['Area_km2']
        area = area.astype(float)
        addfile['total'] = total
        #addfile = addfile.append(solar)
        #addfile = addfile.append(total)
        # print(type(area[1]))
        # print(type(solar[1]))
        #percent_solar = percent_solar.reset_index(name="Percent_solar", inplace=True)
        percent_total = pandas.DataFrame(area.div(total) * 100)
        #percent_total = percent_total.reset_index(name="Percent_total", inplace=True)
        print(percent_total)
        addfile['percent_total'] = percent_total
        #addfile = addfile.append(percent_solar)
        #addfile = addfile.append(percent_total)
        #print(addfile)
        addfile.to_csv(str(filename)[:-4]+"_1.csv")
    else:
        continue

templatefile.to_csv("sitesuitability_solar_airports_1.csv")

