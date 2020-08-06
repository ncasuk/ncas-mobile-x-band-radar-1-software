# vim: et ts=4
import sys
import glob
import os

#must be given in this format yyyymmddhhmmss
start_time=sys.argv[1]
end_time=sys.argv[2]
scan_type=sys.argv[3]
params_index=int(sys.argv[4])

datadir = '/gws/nopw/j04/ncas_radar_vol2/data/xband/raine/cfradial/uncalib_v1/' + scan_type
#params_file= '/home/users/lbennett/lrose/ingest_params/raine/RadxConvert.raine.calib.0' + params_index

daydir=os.listdir(datadir)

start_date=str(start_time)[0:8]
end_date=str(end_time)[0:8]
#print start_date, end_date

files = []
for day in daydir:
    if day >= start_date and day <= end_date:
        for each in glob.glob(datadir + '/' + day + '/*.nc'):
            #print each
            filetime = os.path.basename(each).split('_')[2].replace('-','')
            if start_time <= filetime and end_time >= filetime:
                files.append(each)
print 'number of files = ', len(files)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

#print len(files)
chunk_index=0
for file_chunk in chunks(files,62):
#for file_chunk in chunks(files,142):
#   print str(chunk_index), file_chunk
    #print str(chunk_index)
    #print (' '.join(['/home/users/lbennett/lrose/ncas-radar-lotus-processor/src/calibrate_raine.sh', scan_type, str(params_index), str(chunk_index)] + file_chunk))
    os.system(' '.join(['/home/users/lbennett/lrose/ncas-radar-lotus-processor/src/calibrate_raine.sh', scan_type, str(params_index), str(chunk_index)] + file_chunk))
    chunk_index=chunk_index+1
    #if chunk_index==2:
    #break;
