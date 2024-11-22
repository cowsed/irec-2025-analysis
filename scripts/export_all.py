#!/usr/bin/env python3
import os
import sys

import orhelper
import jpype

if len(sys.argv) < 4:
    print("Usage: export_all.py OPENROCKET.jar FILE.ork OUTPUT_DIR")
    sys.exit(1)

orJarPath = sys.argv[1]
rocketFile = sys.argv[2]
outputDir = sys.argv[3]

with orhelper.OpenRocketInstance(jar_path=orJarPath, log_level='ALL') as instance:
    orh = orhelper.Helper(instance)
    orp = jpype.JPackage("net").sf.openrocket

    FileOutputStream = jpype.JClass("java.io.FileOutputStream")
    CSVExport = orp.file.CSVExport

    doc = orh.load_doc(rocketFile)
    numSims = doc.getSimulationCount()
    print(f'Generating Data for {numSims} simulation(s)')
    print(f'Saving results to {outputDir}')

    os.makedirs(outputDir, exist_ok=True)

    sims = doc.getSimulations()
    for sim in sims:
        simName = str(sim.getName())
        print(f"Running '{simName}'")
        orh.run_simulation(sim)

        branch = sim.getSimulatedData().getBranch(0)
        if sim.getSimulatedData().getBranchCount() > 1:
            print(f"Only using branch 1 of {
                  sim.getSimulatedData().getBranchCount()}")

        flight_data_types = branch.getTypes()
        units = [datatype.getUnitGroup().getSIUnit()
                 for datatype in flight_data_types]

        path = os.path.join(outputDir, simName+'.csv')

        fos = FileOutputStream(path)
        decimalPoints = 6
        isExponential = False
        separator = ','
        comment = '#'
        sim_comments, field_comments, event_comments = True, True, True

        CSVExport.exportCSV(fos, sim, branch, flight_data_types, units,
                            separator, decimalPoints, isExponential, comment, sim_comments, field_comments, event_comments)
        fos.close()
