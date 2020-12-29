import pandas
import os

resultfile = pandas.DataFrame(columns=['filename', 'statdict'])
directory = (r"R:\users\anagha.uppal\MapRE\REzoningGIStools_v1_6\REzoningGIStools_v1_6\sitesuitability_constraint")
for filename in os.listdir(directory):
    if filename.endswith(".csv") and "_1" in filename:
        addfile = pandas.read_csv(filename, sep=",")

        value1 = filename[22:]
        resultfile = resultfile.append({'filename': value1}, ignore_index=True)
        statdict = {}
        statdict[filename] = [addfile['percent_total'].mean(), addfile['percent_total'].std(), addfile['percent_total'].median()]
        resultfile = resultfile.append({'statdict': statdict}, ignore_index=True)
        for i in range(len(addfile)):

            #print(addfile.iloc[i]['percent_solar'])
            #print(addfile.dtypes)
            if addfile.iloc[i]['percent_total'] < 80.0:
                print(filename)
                print(addfile.iloc[i])
                resultfile = resultfile.append(addfile.iloc[i])
    else:
        continue
resultfile.to_csv("resultfile.csv")