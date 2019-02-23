This directory contains a few scripts and utilities for benchmarking ITURHFProp against the D1 Dataset.

The scripts assume the presence of the 'data' and 'run' subdiectories.  The data directory is typically a link to your system ITURHFProp data directory.  The run directory is used to hold .in and .out files for the purposes checking the results.

1. Run the buildPredictionTable.py to create a table of predicted values corresponding to the paths in d1_data_measured.csv.  This command will take several minutes to process as predictions are created for all 1613 paths.

    python3 generatePredictionTable.py

2. Run buildResidualCSV.py to create a table of residual (error) values (Epredicted − Emeasured)

    python3 generateResidualCSV.py d1_data_predicted.csv d1_data_measured.csv

3. Run create DistPlot.py to create a plot of the errors and detremine the mean and standard deviation.

4. An ITU-R P.1148-1 style report may be generated using the following command;

    python3 generate1148Report.py diff.csv > 1148.txt
