# vim: et ts=4
import sys
import glob
import os

#must be given in this format yyyymmddhhmmss
#start_time=sys.argv[1]
#end_time=sys.argv[2]
scan_type=sys.argv[1]
params_index=int(sys.argv[2])

start_times=[20161101093004,20170515090847,20170515100631,20170614000021, 20180111173507, 20180328095415, 20180420000134, 20180509123544]
end_times=[20170515085501, 20170515094914, 20170611235929, 20171215103708, 20180328092801,20180416155357, 20180509112845, 20180604145537]

datadir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/chilbolton/cfradial/uncalib_v1/' + scan_type
#params_file= '/home/users/lbennett/lrose/ingest_params/RadxConvert.chilbolton.calib.0' + params_index

daydir=os.listdir(datadir)

start_date=str(start_times[params_index-1])[0:8]
end_date=str(end_times[params_index-1])[0:8]

files = []
for day in daydir:
    if day >= start_date and day <= end_date:
        for each in glob.glob(datadir + '/' + day + '/*.nc'):
            filetime = os.path.basename(each).split('_')[2].replace('-','')
            #if start_time <= filetime and end_time >= filetime:
            if str(start_times[params_index-1]) <= filetime and str(end_times[params_index-1]) >= filetime:
                 files.append(each)
#print len(files)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

#print len(files)
chunk_index=0
for file_chunk in chunks(files,62):
#   print str(chunk_index), file_chunk
    #print str(chunk_index)
    #print(' '.join(['~/lrose/ncas-radar-lotus-processor/src/calibrate_chilbolton.sh', scan_type, str(params_index), str(chunk_index)] + file_chunk))
    os.system(' '.join(['/home/users/lbennett/proc_test/calibrate_chilbolton.sh', scan_type, str(params_index), str(chunk_index)] + file_chunk))
    #print(' '.join(['~/lrose/ncas-radar-lotus-processor/calibrate_chilbolton.sh', params_file, str(chunk_index)] + file_chunk))
    chunk_index=chunk_index+1
    #if chunk_index==2:
    #break;
