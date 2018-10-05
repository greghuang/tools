import pandas as pd
import sys
import datetime
import tarfile
import os

from re import match

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Please provide correct parameters")
        print("Execution syntax: python package.py [teamID] [folder_name] [*attribute]")
        print("ex. python package.py 001 Log nobump nozigzag")
        sys.exit(1)

    attr_labels = ["nobump", "nozigzag", "noreverse", "fork", "obstacle", "shortest"]
    team_id = sys.argv[1]
    folder = sys.argv[2]
    log_file = sys.argv[2] + "/driving_log.csv"
    attributes = ""

    for s in sys.argv[3:]:
        if s in attr_labels:
            attributes += '_' + s
        else:
            print("{} is not a correct attribute".format(s)) 
            sys.exit(1)

    # Get current date
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d")

    # Check driving log
    try:
        log_csv = pd.read_csv(log_file, header=None)
        track_num = log_csv[0][0].split("/")[-1].split("-")[1]
        last_lap_num = log_csv.iloc[-1][6]
    except:
        print("Error: Can't find the driving_log.csv in the folder")
        print("Error: Or data was recorded by the older SDK. Please use the latest SDK instead")
        sys.exit(1)

    if last_lap_num == 1:
        print("Error: This log didn't complete 1 lap")
        sys.exit(1)

    # Calculate # of lap and avg of lap time
    finished_lap_num = last_lap_num - 1
    finished_lap_time = log_csv.groupby([6])[5].max()[finished_lap_num]
    average_lap_time = int(1000 * (finished_lap_time / finished_lap_num))

    out_folder = "{}_{}_{}_{:02}_{:.0f}{}".format(date, team_id, track_num, finished_lap_num, average_lap_time, attributes)
    out_file = out_folder + ".tar.gz"
    
    # tar the folder with gz
    tar = tarfile.open(out_file, "w:gz")
    for root, dir, files in os.walk(folder):        
        # print("root:"+os.path.basename(root))
        for file in files:
            fullpath = os.path.join(root,file)
            arcpath = fullpath.replace(folder, out_folder)            
            tar.add(fullpath, arcname=arcpath)
    tar.close()

    print("Package training data into {} done".format(out_file))

    # Check file size
    statinfo = os.stat(out_file)
    if statinfo.st_size < 20971520:
        print("Error: The size of file is less than 20MB")
        sys.exit(1)
