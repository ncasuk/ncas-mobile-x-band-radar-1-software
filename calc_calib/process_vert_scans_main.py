import SETTINGS
import os
import glob
from datetime import date

today = date.today().strftime("%Y-%m-%d")

if not os.path.exists(os.path.join(SETTINGS.LOTUS_DIR,today)):
    os.makedirs(os.path.join(SETTINGS.LOTUS_DIR,today))

#dates = [os.path.basename(x) for x in glob.glob(SETTINGS.DATA_DIR+'20*')]
dates = os.listdir(SETTINGS.DATA_DIR)
dates.sort()

current_directory = os.getcwd()  # get current working directory
dates=['20181031']
#for day in dates[0:1]:
for day in dates:
    print(day)

# command to submit to lotus
    sbatch_command = f"sbatch -p {SETTINGS.QUEUE} -t {SETTINGS.WALLCLOCK} -o " \
                       f"{SETTINGS.LOTUS_DIR}{today}/{day}.out -e {SETTINGS.LOTUS_DIR}{today}/{day}.err "\
                       f"--wrap=\"python {current_directory}/process_raine_vert_scans.py {day} {SETTINGS.PLOT}\""

    #subprocess.call(sbatch_command, shell=True)

    print(f"running {sbatch_command}")

