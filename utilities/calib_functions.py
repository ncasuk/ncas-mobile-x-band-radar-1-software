import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from datetime import time
from datetime import timedelta
import pandas as pd
#from functions import moving_average
from calc_calib import SETTINGS
import warnings
import glob
import gc
import copy
import os
import scipy as scipy
from scipy import signal
#import peakdetect
#from peakdetect import peakdet

plt.switch_backend('agg')

warnings.filterwarnings("ignore", category=UserWarning) 
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

#---------------------------------------------------------------------------------------
#Extract Melting Layer and mean ZDR values from vertical scans and save to csv file'

def process_zdr_scans(outdir,raddir,date,file,plot):
 
    filelist = glob.glob(raddir+date+'/*.nc')
    filelist.sort()    
    MLB=np.zeros(300)*np.nan;
    TopRain=np.zeros(300)*np.nan;
    nvals=np.zeros(301)*np.nan;
    mean_zdr=np.zeros(300)*np.nan;
    med_zdr=np.zeros(300)*np.nan;
    std_zdr=np.zeros(300)*np.nan;
    std_err=np.zeros(300)*np.nan;
    T=np.zeros(300)*np.nan;
    fileindex=np.zeros(300)*np.nan;

    #Loop through files for a given day
    for F in range (0,len(filelist)):
        print(F)
        #Read file
        rad=pyart.io.read(filelist[F])

        el = copy.deepcopy(rad.elevation['data'])
        el = el[::360]
        radh = copy.deepcopy(rad.altitude['data'])
        az = copy.deepcopy(rad.azimuth['data'])
        rg = copy.deepcopy(rad.range['data']/1000)
        ind=rg<0.36
        rg[ind]=np.nan
                #ax2b.set_ylim([0, peak+2])
        #Height above sea level
        rg=rg+radh/1000
        rg2=rg
        rg_sp = rg[1]-rg[0]
        max_gate = rg.size
        #print(max_gate) 

       	try:
            rhohv = copy.deepcopy(rad.fields['RhoHVu']['data'])
            rhohv[rhohv.mask]=np.nan
            rhohv=rhohv.data
            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
            uzh[uzh.mask]=np.nan
            uzh=uzh.data
            zdru = copy.deepcopy(rad.fields['ZDRu']['data'])
            zdru[zdru.mask]=np.nan
            zdru=zdru.data
            #RV for radial velocity
            rv = copy.deepcopy(rad.fields['Vu']['data'])
            rv[rv.mask]=np.nan
            rv=rv.data
            rv2 = copy.deepcopy(rad.fields['Vu']['data'])
            rv2[rv2.mask]=np.nan
            rv2=rv2.data

       	except:
            print("Couldn't load all variables")    
            continue

        rhohv[:,ind]=np.nan
        uzh[:,ind]=np.nan
        zdru[:,ind]=np.nan
        rv[:,ind]=np.nan
        rv2[:,ind]=np.nan

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
        T[F] = hh + mm/60.0 + ss/3600.0
        T2 = pd.to_datetime(date) + pd.to_timedelta(T, unit='h')
        daystr = time[0:4]+time[5:7]+time[8:10]
       
        #Create string for timestamp 
        if hh<10:
            if mm<10:
                timestr = '0' + str(int(hh)) + '0' + str(int(mm))
            else:
                timestr = '0' + str(int(hh)) + str(int(mm))
        elif mm<10:
            timestr = str(int(hh)) + '0' + str(int(mm))
        else:
            timestr = str(int(hh)) + str(int(mm))

        rhv_prof = np.nanmean(rhohv,axis=0)
        uzh_lin= 10**(uzh/10)
        uzh_lin_prof = np.nanmean(uzh_lin,axis=0)
        uzh_prof = 10*np.log10(uzh_lin_prof)
        rv_prof = np.nanmean(rv2,axis=0)
        zdru_prof = np.nanmean(zdru,axis=0)

        #Threshold the data to select regions of rain
        ind1 = np.logical_and(rhv_prof > 0.99, np.logical_and(uzh_prof > 0,  uzh_prof < 30, rv_prof < -2))
        
        #Find data that meets these criteria, which are a good indication of rain. It will also find areas above the melting later, 
        #as snow has similar characteristics
              
        #If no data exists, skip to next iteration of the loop i.e. next file
        if np.sum(ind1==True)==0:
            print('no data meets criteria')
            continue

        #Find index of good data
        i = np.where(ind1==True)

        #Find starting point, lowest rain gate
        ind2 = i[0][0]
        if rg[ind2]>1.0:
            print('lowest point is above 1km')
            continue       

        #Normalize Z and RhoHV profiles, and combine
        Znorm = (uzh_prof - -10)/70       #-10 to 60
        Znorm[Znorm<0]=0
        Znorm[Znorm>1]=1
        
        Rnorm = (rhv_prof - 0.85)/0.15    #0.85 to 1
        Rnorm[Rnorm<0]=0
        Rnorm[Rnorm>1]=1
        
        #Calculate the vertical gradient of radial velocity to use as an indication for the base of the melting layer.
        grad_RV = np.gradient(rv_prof)
        
        #Normalized gradRV
        #gradRV_norm = (grad_RV - -0.5)/ 1  #-0.5 to 1
        gradRV_norm = (grad_RV - np.nanmin(grad_RV))/ (np.nanmax(grad_RV)-np.nanmin(grad_RV))  #min to max
    
        #Combined profile, using normalised profiles of dBZ, 1-rhohv and gradient of RV 
        P26=Znorm*(1-Rnorm)*(gradRV_norm)      
        #First derivative of P26
        P26d = np.gradient(P26)
        #Second derivative of P26
        P26dd = np.gradient(P26d)
        #Enhanced profile
        P26_E = P26 - (0.75*P26dd)
    
        #Find peaks in the profile
        all_peaks = scipy.signal.find_peaks(P26_E,0.05)
        #print(all_peaks)
        peaks=all_peaks[0]
        #print('height of peaks = ', rg[peaks])
    
        #Limit ML peaks to below 4km
        r1=rg[peaks]<4
        peaks=peaks[r1]
        
        #If the array is empty there are no peaks, move to next file
        if peaks.size==0:
            print('no peaks found')
            continue
        #If there is a single value, find the index
        elif peaks.size==1:
            print('peak found')
            peak_ind = peaks[0]    
        #If there is more than one value, find the largest peak, below 4km, and its index
        elif peaks.size>1:   
            print('more than one peak found')
            p1=np.where(P26_E[peaks]==np.max(P26_E[peaks]))[0][0]
            peak_ind=peaks[p1]
        
        #Find the index and rg of the peak
        peak=rg[peak_ind]
        #print('peak_ind = ', peak_ind, ' peak height = ', peak)
    
        #Find the inverse peaks (valleys) to find the MLT and MLB (i.e boundaries of the melting layer)
        bounds = scipy.signal.find_peaks(-P26_E)
        bounds = bounds[0]
        
        ubounds = bounds[np.where(bounds-peak_ind>0)]
        lbounds = bounds[np.where(bounds-peak_ind<0)]
    
        #print(bounds-peak_ind)
        #If there are no positive values for the difference between the peak and values of bounds, 
        #this implies there is no MLT, skip to next file  
        if np.sum(bounds-peak_ind>0)==0:
            print('no MLT found')
            continue
        #If there are no negative values for the difference between the peak and values of bounds, 
        #this implies there is no MLB, skip to next file    
        if np.sum(bounds-peak_ind<0)==0:
            print('no MLB found')
            continue
    
        #MLT_ind = ubounds[0]
        MLB_ind = lbounds[-1]
        i=0
        while P26_E[MLB_ind]>0.05:
            i=i+1
            MLB_ind=lbounds[-1-i]    
        
        #Now extract data below MLB that fits the criteria for rain determined earlier (ind1)
        x1=np.where(ind1==True)[0]
        ind_rain = x1[np.where(x1<MLB_ind)] 
    
        #Find data gaps greater than 8 points. There could be points of good data separated by areas where the criteria isn't met. 
        #If size>0 then there are gaps in the section of good data, so we need to extract the lowest section
        # if np.where(np.diff(ind_rain)>=8)[0].size==0:
        #     print('no gaps')
        # else:
        #     gaps= np.where(np.diff(ind_rain)>=8)[0][0]
        #     #if gaps.size > 0:
        #     ind_rain = ind_rain[0:gaps+1]
        
        #If the section of data is less than 0.25km (8*0.03) then skip to next volume
        if len(ind_rain)<8:
            print('Insufficient data')
            continue

        #Height of the top of the rain
        TopRain[F] = rg[ind_rain[-1]]

        #Create image filename 
        img_name = os.path.join(outdir,date,'vert_profs_' + daystr + '_' + timestr + '.png') 
        #if os.path.exists(img_name):
        #    print('File already processed, image created')
        #    continue

        #Count the number of data points
        nvals[F] = len(ind_rain)
        fileindex[F] = F

        #If profile data is extracted create output directory for this date
        if not os.path.exists(os.path.join(outdir,date)):
            os.makedirs(os.path.join(outdir,date))

        MLB[F] = rg[MLB_ind]
        #Save ZDR values 
        med_zdr[F] = np.nanmedian(zdru_prof[ind_rain])
        mean_zdr[F] = np.nanmean(zdru_prof[ind_rain])
        std_zdr[F] = np.nanstd(zdru_prof[ind_rain]) 

        #Make plot if user has requested them
        #This is a plot for every time step
        if plot==1:
            fig = plt.figure(figsize=(10,7))    
            ax1 = fig.add_subplot(141)
            ax1.plot(rhv_prof,rg,'k',linewidth=2)
            ax1.plot(rhv_prof[ind1],rg[ind1],'kx',markersize=8,linewidth=2,label='matches criteria')
            ax1.set_ylim([0, 4])
            ax1.set_xlim(0.8,1)
            ax1.set_xlabel('RhoHV')
            ax1.grid(axis='y')
            ax1b=ax1.twiny()
            ax1b.plot(uzh_prof,rg,'b-',linewidth=2)
            ax1b.plot(uzh_prof[ind1],rg[ind1],'bx',markersize=8,linewidth=2,label='matches criteria')
            ax1b.set_ylim([0, 4])
            ax1b.set_xlabel('dBZ',color='blue')
            ax1b.set_xlim([-10, 40])
            ax1b.tick_params(axis='x', colors='blue')
            ax1b.legend(loc=1,fontsize=12) 

            ax2 = fig.add_subplot(142)
            ax2.plot(rv_prof,rg,'k-',linewidth=2)
            ax2.set_ylim([0, 4])
            ax2.set_xlabel('V')
            ax2.grid(axis='y')
            ax2b=ax2.twiny()
            ax2b.plot(zdru_prof,rg,'b-',linewidth=2)
            ax2b.plot(zdru_prof[ind1],rg[ind1],'bx',markersize=8,linewidth=2,label='matches criteria')
            ax2b.plot(zdru_prof[ind_rain],rg[ind_rain],'gx',markersize=8,linewidth=2,label='final data')
            ax2b.set_xlim([-1, 1])
            ax2b.set_xlabel('ZDR',color='blue')
            ax2b.tick_params(axis='x', colors='blue')
            ax2b.plot(zdru_prof[MLB_ind],rg[MLB_ind],'ro',markersize=8,linewidth=2,label='MLB')       
            ax2b.legend(loc=1,fontsize=12)
       
            ax3 = fig.add_subplot(143)
            ax3.plot(Znorm,rg,'k-',linewidth=2,label='Znorm')
            ax3.plot(1-Rnorm,rg,'b-',linewidth=2,label='1-Rnorm')
            ax3.plot(gradRV_norm,rg,'g-',linewidth=2,label='gradRVnorm')
            ax3.grid(axis='y')
            ax3.set_ylim([0,4])
            ax3.title.set_text(daystr + timestr)
            ax3.legend(loc=1,fontsize=12)  
                
            ax4 = fig.add_subplot(144)
            ax4.plot(P26,rg,'k-',linewidth=2,label='P26')
            ax4.plot(P26d,rg,'b-',linewidth=2,label='P26d\'')
            ax4.plot(-1*P26dd,rg,'g-',linewidth=2,label='-P26d\'\'')
            ax4.plot(P26_E,rg,'r-',linewidth=2,label='P26_E')
            ax4.grid(axis='y')
            ax4.set_ylim([0,4])
            ax4.set_xlim([-0.1, np.nanmax(P26_E)])
            ax4.set_xlabel('P26')
            ax4.plot(P26_E[peak_ind],rg[peak_ind],'rs',markersize=8,linewidth=2,label='Peak')    
            ax4.plot(P26_E[MLB_ind],rg[MLB_ind],'ro',markersize=8,linewidth=2,label='MLB')
            ax4.legend(loc=1,fontsize=12)
        
            #Plot and save figure 
            plt.savefig(img_name,dpi=150)
            print('graph plotted')
            plt.close()
            plt.clf()

        #Combine the profile variables to output to text file
        data_array = np.stack([zdru_prof, rhv_prof, uzh_prof, rv_prof],axis=1)
        np.savetxt(os.path.join(outdir, date, 'vert_profs_' + daystr + '_' + timestr + '.txt'), data_array, delimiter=',')
        print('data file saved')

       	del rad
       	del zdru, rhohv, uzh, rv 
       	gc.collect()

    #If a melting layer and/or a value of ZDR offset for the profile can be determined then save the data to file
    if np.isfinite(MLB).any() or np.isfinite(med_zdr).any():
        print("valid values")
        if not os.path.exists(os.path.join(outdir,date)):
            os.makedirs(os.path.join(outdir,date))

        output = pd.DataFrame({'ZDR' : med_zdr, 'MLB' : MLB}, index=T2)
        output.to_csv(file)
        return True

    else:
       	return False
#        output = pd.DataFrame()
#        output.to_csv(file)



#---------------------------------------------------------------------------------------
#New function inserted into file above on 16/10/23
##Extract Melting Layer and mean ZDR values from vertical scans and save to csv file'
#
#def process_zdr_scans(outdir,raddir,date,file,plot):
# 
#    filelist = glob.glob(raddir+date+'/*.nc')
#    filelist.sort()    
#    ML=np.zeros(300)*np.nan;
#    nvals=np.zeros(300)*np.nan;
#    mean_zdr=np.zeros(300)*np.nan;
#    med_zdr=np.zeros(300)*np.nan;
#    std_zdr=np.zeros(300)*np.nan;
#    std_err=np.zeros(300)*np.nan;
#    T=np.zeros(300)*np.nan;
#    fileindex=np.zeros(300)*np.nan;
#
#    #Loop through files for a given day
#    for F in range (0,len(filelist)):
#        print(F)
#        #Read file
#        rad=pyart.io.read(filelist[F])
#
#        el = copy.deepcopy(rad.elevation['data'])
#        el = el[::360]
#        radh = copy.deepcopy(rad.altitude['data'])
#        az = copy.deepcopy(rad.azimuth['data'])
#        rg = copy.deepcopy(rad.range['data']/1000)
#        rg_sp = rg[1]-rg[0]
#        max_gate = rg.size
#        #print(max_gate) 
#       	try:
#            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
#            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
#            zdru = copy.deepcopy(rad.fields['ZDRu']['data'])
#            v = copy.deepcopy(rad.fields['Vu']['data'])
#            v2 = copy.deepcopy(rad.fields['Vu']['data'])
#
#       	except:
#            print("Couldn't load all variables")    
#            continue
#
#        #Create time array
#        time = rad.metadata['start_datetime']
#        hh = float(time[11:13])
#        mm = float(time[14:16])
#        ss = float(time[17:19])
#        T[F] = hh + mm/60.0 + ss/3600.0
#        daystr = time[0:4]+time[5:7]+time[8:10]
#       
#        #Create string for timestamp 
#        if hh<10:
#            if mm<10:
#                timestr = '0' + str(int(hh)) + '0' + str(int(mm))
#            else:
#                timestr = '0' + str(int(hh)) + str(int(mm))
#        elif mm<10:
#            timestr = str(int(hh)) + '0' + str(int(mm))
#        else:
#            timestr = str(int(hh)) + str(int(mm))
#
#        #Create image filename 
#        img_name = os.path.join(outdir,date,'vert_profs_' + daystr + '_' + timestr + '.png') 
#        if os.path.exists(img_name):
#            print('File already processed, image created')
#            continue
#
#        #Simple unfolding method for velocity profile - this was set for RAINE when the nyquist was -8. 
#       	ind = v>6.0
#        v2[ind] = -7.9725 - (7.9725-v[ind])
#
#        #Calculate mean values of all azimuths for each range step 
#        rhv_prof = np.nanmean(rhohv,axis=0)
#        uzh_prof = np.nanmean(uzh,axis=0)
#        v_prof = np.nanmean(v2,axis=0)
#        zdru_prof = np.nanmean(zdru,axis=0)
#
#        #Threshold the data to select regions of rain
#        ind = np.logical_and(rhv_prof > 0.99, np.logical_and(uzh_prof > 0,  v_prof <- 2))
#
#        #Check if any of the data fit the criteria
#        #If no, skip to next iteration of the loop i.e. next file
#        if np.sum(ind==True)==0:
#            continue
#
#        #Find index of good data
#        i = np.where(ind==True)
#        
#        #Find starting point, lowest rain gate
#        ind2 = i[0][0]
#        if rg[ind2]>1.0:
#            print('lowest point is above 1km')
#            continue       
# 
#        #Find bottom of the melting layer, i.e. top of the rain by finding gaps in the good data
#        #First check if there are any gaps
#	#Find data gaps greater than 8 points. If size==0 then there arent any gaps, so use the top point of the selected data
#        if np.where(np.diff(i[0])>8)[0].size == 0:
#            ind3=i[0][-1]            
#        else:
#            ind3 = i[0][np.where(np.diff(i[0])>8)[0][0]]+1                        
#        
#        #If the section of data is less than 0.48km (16*0.03) then skip to next volume
#        if ind3-ind2<16:
#            continue
#
#        #Count the number of data points
#        nvals[F] = ind3-ind2+1
#
#        #Calculate the vertical gradient of velocity and RhoHV, to use an indications for the base of the melting layer.
#       	grad_v = np.gradient(v_prof)
#       	grad_rhv = np.gradient(rhv_prof)
#
#        #Finds the maximum gradient of velocity within the region extracted
#       	max_grad_v_ind = np.where(grad_v==np.max(grad_v[ind3:ind3+17]))[0][0]
#       	max_grad_v = grad_v[max_grad_v_ind]
#       	#print 'max grad_v = ', max_grad_v, ' at height of ', rg[max_grad_v_ind]
#    
#        #Finds the maximum gradient of RhoHV within the region extracted
#       	min_grad_rhv_ind = np.where(grad_rhv==np.min(grad_rhv[ind3:ind3+17]))[0][0]
#       	min_grad_rhv = grad_rhv[min_grad_rhv_ind]
#    	#print 'max_grad_rhv = ', max_grad_rhv, 'at height of ', rg[max_grad_rhv_ind]
#	
#        #Looks to see if the gradients are large enough, either in velocity alone or a combination of velocity and RhoHV 
#        #These values were chosen after analysing a number of cases.
#       	if np.logical_or(np.logical_and(np.logical_and(max_grad_v_ind > ind3, 0.15 <= max_grad_v < 0.25), min_grad_rhv <-0.015),\
#            np.logical_and(max_grad_v_ind > ind3, max_grad_v >0.25)):
#
#            #If profile data is extracted create output directory for this date
#            if not os.path.exists(os.path.join(outdir,date)):
#                os.makedirs(os.path.join(outdir,date))
#
#            #Define Melting Level height as the height at the top of the valid data i.e. first rain point 
#            #Need to add on radar height to get height above sea level
#            fileindex[F] = F
#            ML[F] = rg[ind3] + (radh /1000)
#            med_zdr[F] = np.median(zdru_prof[ind2:ind3])
#            std_zdr[F] = np.std(zdru_prof[ind2:ind3])
#
#            #Make plot if user has requested them
#            if plot==1:
#               	fig = plt.figure(figsize=(10,7))    
#                ax1 = fig.add_subplot(141)
#                ax1.plot(rhv_prof,rg,'kx-')
#                ax1.plot(rhv_prof[ind2:ind3],rg[ind2:ind3],'bx')
#                ax1.set_ylim([0, 6])
#                ax1.set_xlim(0.9,1)
#                ax1.set_xlabel('RhoHV')
#                ax2 = fig.add_subplot(142)
#                ax2.plot(uzh_prof,rg,'kx-')
#                ax2.plot(uzh_prof[ind2:ind3],rg[ind2:ind3],'bx')
#                ax2.set_ylim([0, 6])
#                ax2.set_xlabel('dBuZ')
#                ax3 = fig.add_subplot(143)
#                ax3.plot(v_prof,rg,'kx-')
#                ax3.plot(v_prof[ind2:ind3],rg[ind2:ind3],'bx')
#                ax3.set_ylim([0, 6])
#                ax3.set_xlabel('V')
#                ax4 = fig.add_subplot(144)
#                ax4.plot(zdru_prof,rg,'kx-')
#                ax4.plot(zdru_prof[ind2:ind3],rg[ind2:ind3],'bx')
#                ax4.set_ylim([0, 6])
#                ax4.set_xlabel('ZDRu')
#                #if mm<10:
#                #   timestr = str(int(hh)) + '0' + str(int(mm))
#                #    fig.suptitle(timestr)
#                #else:
#                #   timestr = str(int(hh)) + str(int(mm))
#                #    fig.suptitle(timestr)
#           
#                #plt.tight_layout()
#                #file_name = os.path.join(outdir,date,'vert_profs_' + daystr + '_' + timestr + '.png') 
#                #print file_name
#                #file_path = os.path.join(outdir,date,file_name)
#                
#
#                #Plot and save figure 
#                plt.savefig(img_name,dpi=150)
#                print('graph plotted')
#                plt.close()
#                plt.clf()
#
#    	    #Combine the profile variables to output to text file
#            data_array = np.stack([zdru_prof, rhv_prof, uzh_prof, v_prof],axis=1)
#            np.savetxt(os.path.join(outdir, date, 'vert_profs_' + daystr + '_' + timestr + '.txt'), data_array, delimiter=',')
#            print('data file saved')
#
#       	del rad
#       	del zdru, rhohv, uzh, v 
#       	gc.collect()
#
#    #If a melting layer and/or a value of ZDR offset for the profile can be determined then save the data to file
#    if np.isfinite(ML).any() or np.isfinite(med_zdr).any():
#        print("valid values")
#        if not os.path.exists(os.path.join(outdir,date)):
#            os.makedirs(os.path.join(outdir,date))
#
#        #T2 = timestamp for file
#        T2 = pd.to_datetime(date) + pd.to_timedelta(T, unit='h')
#        output = pd.DataFrame({'ZDR' : med_zdr, 'ML' : ML}, index=T2)
#        output.to_csv(file)
#        return True
#
#    else:
#       	return False
##        output = pd.DataFrame()
##        output.to_csv(file)

#---------------------------------------------------------------------------------------------
#Calculate hourly median values of melting layer heights to use for Z calibration

def calc_hourly_ML(outdir,date):        
  
    #Output variable 
    hourly_ml_zdr = pd.DataFrame() 
    #Input file (full day)
    file1 = os.path.join(outdir, date, 'day_ml_zdr.csv')
    #Output file (hourly values for each day)
    file2 = os.path.join(outdir, date, 'hourly_ml_zdr.csv')

    data = pd.read_csv(file1,index_col=0, parse_dates=True)

    if data.empty==False:

        hourly_ml = np.zeros(24)*np.nan
        hourly_zdr = np.zeros(24)*np.nan
    
        for hh in range(0,24):
            beg=time(hh,0,0)
            print(beg)
            if hh==23:
                end=time(23,59,0)            
                print(end)
            else:
                end=time(hh+1,0,0)
                print(end)
            #Find values of melting layer and median ZDR between each hourly period
            #ml_zdr=data[['MLB','ZDR']].between_time(beg,end,include_end=False)
            ml_zdr=data[['MLB','ZDR']].between_time(beg,end,inclusive='left')
        
            #If there are less than 3 (out of 6) valid values, set all to NaN and continue
            #Else calculate median value of melting layer height and ZDR
            if ml_zdr['MLB'].count()<3:
                hourly_ml[hh]=float('nan')
                hourly_zdr[hh]=float('nan')
                continue
            else:
                M=ml_zdr.median()
        
                #Median Absolute Deviation
                mad=1.4826*(abs(ml_zdr-M)).median()
                out=mad*2.5
                ind = np.logical_or(ml_zdr <= M-out, ml_zdr >= M+out)
        
                ml_zdr[ind==True]=np.nan
      
                hourly_ml[hh]=ml_zdr['MLB'].median()
                hourly_zdr[hh]=ml_zdr['ZDR'].median()
           
        if np.isfinite(hourly_ml).any():      
        
            #Construct time array for hourly medians i.e. 00:30, 01:30
            hourly_T = pd.to_datetime(date) + pd.timedelta_range('00:30:00','23:30:00',freq='1H')
            hourly_ml_zdr = pd.DataFrame({'H_MLB' : hourly_ml, 'H_ZDR' : hourly_zdr}, index=hourly_T)
        
            hourly_ml_zdr = hourly_ml_zdr.dropna()
            hourly_ml_zdr.to_csv(file2)
        
            return True        
        else:
            return False

#------------------------------------------------------------------------------------------------------
def extract_ml_zdr(time, ml_zdr):

#Extract ML and ZDR values corresponding to radar file time
#ml_zdr is the dataframe
#ft = radar file time   
    ft = pd.to_datetime(time)
    ft=ft.tz_convert(None)

#Index of nearest values to ft
#    indf = ml_zdr.index.get_loc(ft, method='nearest')
    indf = ml_zdr.index.get_indexer([ft], method='nearest')
    indf = indf[0]
    #print ft, ml_zdr.index[indf] 
#If radar file time is earlier than first index of ml_zdr, set ml and zdr to first value in file
    if ft >= ml_zdr.index[-1]:

        mlh=ml_zdr['H_MLB'][-1]
        zdr_bias=ml_zdr['H_ZDR'][-1]

#If radar file time is later than last index of ml_zdr, set ml and zdr to last value in file
    elif ft <= ml_zdr.index[0]:

        mlh=ml_zdr['H_MLB'][0]
        zdr_bias=ml_zdr['H_ZDR'][0]

#If radar file time equals an index of ml_zdr, set ml and zdr to those values.
    elif ft == ml_zdr.index[indf]:

        mlh=ml_zdr['H_MLB'][indf]
        zdr_bias=ml_zdr['H_ZDR'][indf]
   
#Else find time indices either side of file time and linearly interpolate between them               
    else:
        if ft > ml_zdr.index[indf]:

            st = indf
            fn = indf+1

        elif ft < ml_zdr.index[indf]:

            st = indf-1
            fn = indf

        t2 = (abs(ft - ml_zdr.index[st])).seconds
        t3 = (abs(ml_zdr.index[fn]-ml_zdr.index[st])).seconds
        t4 = float(t2) / float(t3)

        #Melting layer height interpolated linearly between hourly values
        mlh = ml_zdr['H_MLB'][st] + (ml_zdr['H_MLB'][fn] - ml_zdr['H_MLB'][st]) * t4

        #ZDR interpolated linearly between hourly values
        zdr_bias = ml_zdr['H_ZDR'][st] + (ml_zdr['H_ZDR'][fn] - ml_zdr['H_ZDR'][st]) * t4

    return mlh, zdr_bias

#--------------------------------------------------------------------------------------------------------------------------
#def calibrate_day_norm(raddir, outdir, day, ml_zdr):
#
#    ZDRmax = 2.0
#    min_path = 15
#    filelist = glob.glob(os.path.join(raddir,'*.nc'))
#    filelist.sort()
#    nfiles=len(filelist)
#    print(nfiles)
#
#    #Extract number of rays 
#    rad=pyart.io.read(filelist[0])
#    ss = rad.nrays
#
#    #create empty array for calibration offsets
#    delta_all=np.zeros((nfiles,ss))*np.nan
#    #create empty array for PhiEst and PhiObs
#    phiest_all=np.zeros((nfiles,ss))*np.nan
#    phiobs_all=np.zeros((nfiles,ss))*np.nan
#    startphi_all=np.zeros((nfiles,ss))*np.nan
#    #create empty array for Time
#    T = np.zeros((nfiles))*np.nan
#    #create empty array for number of good rays in each volume
#    good_rays = np.zeros((nfiles))*np.nan
#    #Create empty array for good ray index
#    ray_index = np.zeros((nfiles,ss))*np.nan
#    ray_az = np.zeros((nfiles,ss))*np.nan
#    ray_el = np.zeros((nfiles,ss))*np.nan
#
#
#
#    for file in range(1,nfiles,2):
#    #for file in (181,):
#        print(file)
#
#        #Read file
#        rad=pyart.io.read(filelist[file])
#
#        #Create time array
#        time = rad.metadata['start_datetime']
#        hh = float(time[11:13])
#        mm = float(time[14:16])
#        ss = float(time[17:19])
#        T[file] = hh + mm/60.0 + ss/3600.0
#
#        #Extract dimensions
#        Rdim = rad.ngates
#        Edim = rad.nsweeps
#        Tdim = rad.nrays
#        Adim = Tdim/Edim
#
#        #Extract data
#        try:
#            rg = copy.deepcopy(rad.range['data']/1000)
#            rg_sp = rg[1]-rg[0]
#            max_gate = rg.size
#            el = copy.deepcopy(rad.elevation['data'])
#            el = el[::360]
#            radh = copy.deepcopy(rad.altitude['data'])
#            az = copy.deepcopy(rad.azimuth['data'])
#            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
#            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
#            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
#            kdp = copy.deepcopy(rad.fields['KDP']['data'])
#
#            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
#            ind = phidp > 180
#            phidp[ind] = phidp[ind] - 360
#            ind = phidp < -180
#            phidp[ind] = phidp[ind] + 360
#
#       	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
#            #Set invalid values (-9e33) to nans
#            ind = uphidp.mask==True
#            uphidp[ind]=np.nan
#
#        except:
#            print("Couldn't load all variables")    
#            continue
#
#        #Calculate height of every range gate
#        beam_height = np.empty((Tdim,Rdim))
#        for j in np.arange(0,Edim):
#            for i in np.arange(0,Adim):
#                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);
#        #Extract melting layer height and ZDR bias for current file time
#        mlh, zdr_bias = extract_ml_zdr(time, ml_zdr)
#
#        zind = beam_height > mlh   
#        uzh[zind==True] = np.nan
#
#        zdr[zind==True] = np.nan
#        phidp[zind==True] = np.nan
#        uphidp[zind==True] = np.nan
#        kdp[zind==True] = np.nan
#        rhohv[zind==True] = np.nan
#
#        #Remove first 2km of data
#        n=13
#        uzh = uzh[:,n:]
#        zdr = zdr[:,n:]
#        phidp = phidp[:,n:]
#        uphidp = uphidp[:,n:]
#        kdp = kdp[:,n:] 
#        rhohv = rhohv[:,n:]
#        rg = rg[n:] - rg[n]
#
#        #Create empty arrays for observed and calculated PhiDP
#        phiobs = np.zeros([Tdim])*np.nan
#        phiest = np.zeros([Tdim])*np.nan        
#        startphi = np.zeros([Tdim])*np.nan        
#
##        c=0
#
## Exclusions is a list of tuples (), where each tuple is a pair of 
## tuples. 
## The first tuple of each pair is the start and stop elevation of the 
## segment to exclude.
## The second tuple contains the start and stop azimuth of the segment 
## to exclude.
## This "one-liner" builds a generator from the list of tuples so each 
## tuple defines a binary array which is True where the segment occurs 
## and false elsewhere. 
## All conditions must be met, so between start and stop in both azimuth 
## and elevation. 
## These are then combined to a single array using np.any to create a 
## single exclude binary array which is True where any of the segments 
## are found and False in non-excluded places
#
#    	#raine exclusions = [((0,90.1),(20,160)),((0,90.1),(201,207)),((0,0.51),(185,201.5))]
#        #chilbolton
#       	#exclusions = [((0,90.1),(49,90)),((0,90.1),(130,190)),((0,1.01),(0,360))]
#        #lyneham
#       	exclusions = [((0,90.1),(307,321))]
#        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
#                                  rad.elevation['data']<ele[1],
#                                  rad.azimuth['data']>=azi[0],
#                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
#       	az_index = np.where(~exclude_radials)[0]
#
#        for i in az_index:
#
#            #Extract ray
#            phidp_f1 = phidp[i,:]
#            uphidp_f = uphidp[i,:]
#            #uphidp_sm_f = uphidp_sm[i,:]
#            uzh_f = uzh[i,:]
#            zdr_f = zdr[i,:] - zdr_bias
#            rhohv_f = rhohv[i,:]
#
#            phidp_f = phidp_f1 - phidp_f1[0]
#
#            #Check for all-nan array, go to next iteration of loop if so
#            if np.sum(np.isfinite(phidp_f)==True)==0:
#                continue
#            
#            #Find minimum value of PhiDP
#            phi1_valid = (np.nonzero(np.isfinite(phidp_f)))[0]
#            if phi1_valid.size != 0:
#                phi1 = phi1_valid[0]
#            else:
#                continue
#            #Find indices where PhiDP is between 4 and 6 degs    
#            ind = np.where(np.logical_and(phidp_f > 4, phidp_f < 6))[0]
#
#            #If values exist, 
#            if ind.size != 0:
#                #Find the index of the maximum value of PhiDP between 4 and 6
#                ib = np.where(phidp_f==max(phidp_f[ind]))[0][0]
#                #print '1. index and value of maximum phidp_f between 4&6=', ib, phidp_f[ib]
#
#                pdpmax = phidp_f[ib]
#                path_len = rg[ib]
#                #print '2. maxmimum phidp=', pdpmax, 'Path length=', path_len
#
#                #if path of significant returns exceeds min_path
#                #if np.logical_and(path_len > min_path, pdpmax > 4):
#                if path_len > min_path:
#                    #print '3.', con1
#                    #print "step1"
#                    #plt.plot(zdr_f[0:ib+1])
#
#                    #exclude rays with any bad pixels (heavy rain (mie-scattering))
##                    ind = zdr_f[0:ib+1] > ZDRmax
#                    ind = zdr_f[phi1:ib+1] > ZDRmax
#                    #print '4.', np.sum(ind) < 1
#
#                    if np.sum(ind) < 1:
#                        #plt.plot(rhohv_f[0:ib+1])
#                        #print "step2"
#
#                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
#                        #ind = rhohv_f[0:ib+1] < 0.98
#                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)
#                        #print '5.', np.sum(ind) < 3
#                        #print uzh_f[0:10]
#                        #print uzh_f_all[0,0:10]
#                        #if np.sum(ind) < 3:   
#
##                        if np.sum(ind[0:ib+1]) < 3:   
#                        if np.sum(ind[phi1:ib+1]) < 3:   
#                            #print i
#                            #index of good rays (value from 0 to 4320)
#                            ray_index[file,i] = i
#                            ray_az[file,i] = rad.azimuth['data'][i]
#                            ray_el[file,i] = rad.elevation['data'][i]
#
#                            #print i
#                            uzh_f[ind] = np.nan
#                            zdr_f[ind] = np.nan
#                            #phidp_f[ind] = np.nan
#                            #uphidp_sm_f[ind] = np.nan
#			    #uphidp_sm_f.mask[ind] = np.nan
#                            #rhohv_f[ind] = np.nan
#
#                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])
#
#                            phiobs[i] = pdpmax
#                            #phiobs_all[file,:] = phiobs
#
#                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
#                            kdpest = 1e-05 * (11.74 - 4.020*zdr_f[phi1:] - 0.140*zdr_f[phi1:]**2 + 0.130*zdr_f[phi1:]**3)*10 ** (uzh_f[phi1:]/10)
#
#                            tmpphi = np.nancumsum(kdpest)*rg_sp*2
#
#                            phiest[i] = tmpphi[ib]
#                            #phiest[i] = tmpphi[ib-phi1]
#
#        #phiest is a function of ray, phiest(nrays)
#        #phiest_all is a function of volume and ray, phiest_all(nvols,nrays)
#        #delta is a function of ray, delta(nrays)
#        #delta_all is a function of volume and ray, delta_all(nvols,nrays)
#
#       	phiobs_all[file,0:Tdim] = phiobs
#       	phiest_all[file,0:Tdim] = phiest
#       	startphi_all[file,0:Tdim] = startphi
#
#       	good_rays = np.sum(np.isfinite(phiest))
#       	print('file=',file,'rays=',str(good_rays))
#       	del rad
#       	del zdr, rhohv, kdp, phidp, uzh, uphidp
#       	gc.collect()
#                    
#        #print phiobs.shape   
#        #delta = ((phiest-phiobs)/phiobs)*100
#        #print delta.shape
#        #print file
#        #delta_all[file,:] = delta
#        #print 'end'    
#        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
#        #data_save=np.vstack((phiest,phiobs,delta))
#        #np.save(filename,data_save)          
#
#    #filename = outdir + 'good_rays'     
#    #np.save(filename,good_rays)
#    print("total rays = ", np.sum(np.isfinite(phiest_all.flatten())))
#    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
#        print("phiest and phiobs values exist")
#        phiest_filename = os.path.join(outdir, 'phiest_all_' + day)
#        np.save(phiest_filename,phiest_all)
#        phiobs_filename = os.path.join(outdir, 'phiobs_all_' + day)
#        np.save(phiobs_filename,phiobs_all)
#        startphi_filename = os.path.join(outdir, 'startphi_all_' + day)
#        np.save(startphi_filename,startphi_all)
#        return True
#    else:
#        return False
#
#--------------------------------------------------------------------------------------------------------------------------
def identify_first_phase_ray(data, mask, starting_gate, window_size, filter_size, end_gate_limit, missing_points=0):
    valid_data = np.where(np.logical_or(mask,
                                        ~np.isfinite(data)),
                          np.zeros(data.shape),
                          np.ones(data.shape))
    if valid_data[starting_gate:end_gate_limit].sum() < window_size-missing_points:
        return np.nan, np.nan

    j = starting_gate
    start_not_found = True
    while start_not_found:
        if j == data.shape[0]:
            return np.nan, np.nan

        if valid_data[j]:
            valid_sum = valid_data[j:window_size+j].sum()
            #print(valid_sum)
            if valid_sum >= (window_size-missing_points):
                phase = np.nanmedian(data[j:j+filter_size])
                return phase, j
            elif j > end_gate_limit:
                return np.nan, np.nan
            else:
                j += 1
        elif j > end_gate_limit:
            return np.nan, np.nan

        else:
            j += 1


#--------------------------------------------------------------------------------------------------------------------------
def calibrate_day_att(raddir, outdir, day, ml_zdr):

    ZDRmax = 2.0
    min_path = 10
    filelist = glob.glob(os.path.join(raddir,'*.nc'))
    filelist.sort()
    nfiles=len(filelist)
    print('Number of files = ',nfiles)

    #Extract number of rays 
    rad=pyart.io.read(filelist[0])
    ss = rad.nrays

    #create empty array for calibration offsets
    delta_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for PhiEst and PhiObs
    phiest_all=np.zeros((nfiles,ss))*np.nan
    phiobs_all=np.zeros((nfiles,ss))*np.nan
    startphi_all=np.zeros((nfiles,ss))*np.nan
    #create empty array for Time
    T = np.zeros((nfiles))*np.nan
    #create empty array for number of good rays in each volume
    good_rays = np.zeros((nfiles))*np.nan
    #Create empty array for good ray index
    ray_index = np.zeros((nfiles,ss))*np.nan
    ray_az = np.zeros((nfiles,ss))*np.nan
    ray_el = np.zeros((nfiles,ss))*np.nan


    for file in range(nfiles):
        print(file)

        #Read file
        rad=pyart.io.read(filelist[file])

        #Create time array
        time = rad.metadata['start_datetime']
        hh = float(time[11:13])
        mm = float(time[14:16])
        ss = float(time[17:19])
        T[file] = hh + mm/60.0 + ss/3600.0

        #Extract dimensions
        ind = rad.rays_per_sweep['data'] !=360
        if np.sum(ind)>0:
            print('At least one sweep does not have 360 rays')
            continue        

        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = int(Tdim/Edim)
        if Adim!=360:
            print('azimuths not equal to 360')
            print(Adim)
            continue
        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el2 = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])
            uzh = copy.deepcopy(rad.fields['dBuZ']['data'])
            zdr = copy.deepcopy(rad.fields['ZDR']['data'])
            rhohv = copy.deepcopy(rad.fields['RhoHV']['data'])
            kdp = copy.deepcopy(rad.fields['KDP']['data'])

            phidp = copy.deepcopy(rad.fields['PhiDP']['data'])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360

       	    uphidp = copy.deepcopy(rad.fields['uPhiDP']['data'])
            #Set invalid values (-9e33) to nans
            ind = uphidp.mask==True
            uphidp[ind]=np.nan

        except:
            print("Couldn't load all variables")    
            continue

        #Calculate height of every range gate
        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(360*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        mlh, zdr_bias = extract_ml_zdr(time, ml_zdr)

        zind = beam_height > mlh   
        uzh[zind==True] = np.nan
        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        uphidp[zind==True] = np.nan
        kdp[zind==True] = np.nan
        rhohv[zind==True] = np.nan

        #Get rid of first 2km
        #n=13 for 1us pulse
#        n=26 #for 0.5us pulse
#        uzh = uzh[:,n:]
#        zdr = zdr[:,n:]
#        phidp = phidp[:,n:]
#        uphidp = uphidp[:,n:]
#        kdp = kdp[:,n:] 
#        rhohv = rhohv[:,n:]
#        rg = rg[n:] - rg[n]

        #Create empty arrays for observed and calculated PhiDP
        phiobs = np.zeros([Tdim])*np.nan
        phiest = np.zeros([Tdim])*np.nan        
        startphi = np.zeros([Tdim])*np.nan        

#        c=0

# A list of tuples is imported from the SETTINGS file. This "one-liner" 
# builds a generator from the list of tuples so each tuple defines a 
# binary array which is True where the segment occurs and false 
# elsewhere. All conditions must be met, so between start and stop in 
# both azimuth and elevation. 
# These are then combined to a single array using np.any to create a 
# single exclude binary array which is True where any of the segments 
# are found and False in non-excluded places

        exclusions = SETTINGS.EXCLUSIONS
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)

       	az_index = np.where(~exclude_radials)[0]

        for i in az_index:
        #for i in (778,):
            print('1. az_index = ', i, 'azimuth = ', az[i], 'El = ', el2[i])

#This function uses a moving window to find the first 10 valid values of phidp and uses this as the starting point of the ray.
            data=phidp[i,:]
            [phase1,r1] = identify_first_phase_ray(data, data.mask, 0, 10, 5, len(data), missing_points=0)
            if np.isnan(r1):
                print('insufficient phidp')
                continue

            #Extract ray
            phidp_f = phidp[i,r1:]
            uphidp_f = uphidp[i,r1:]
            uzh_f = uzh[i,r1:]
            zdr_f = zdr[i,r1:] - zdr_bias
            rhohv_f = rhohv[i,r1:]
            rg_f = rg[r1:]

            #attenuation correction
            #phidp_att = copy.deepcopy(phidp_f)
            phidp_att = phidp_f - phidp_f[0]

            PA = np.maximum.accumulate(phidp_att) 
            uzh_att = uzh_f + 0.28*PA
            zdr_att = zdr_f + 0.04*PA

            #Check for all-nan array, go to next iteration of loop if so
            #if np.sum(np.isfinite(phidp_att)==True)==0:
            #    continue

            #Find minimum value of PhiDP
            #phi1_valid = np.where(np.isfinite(phidp_att))[0]
            #if phi1_valid.size != 0:
             #   phi1 = phi1_valid[0]
            #else:
            #    continue
            phi1=0
#            #Find indices where PhiDP is between 4 and 6 degs    
            ind = np.where(np.logical_and(phidp_att > 4, phidp_att < 6))[0]

            #If values exist, 
            if ind.size != 0:
                #Find the index of the maximum value of PhiDP between 4 and 6
                ib = np.where(phidp_att==max(phidp_att[ind]))[0][0]

                pdpmax = phidp_att[ib]
                print('2. maxmimum phidp=', pdpmax)
                path_len = rg_f[ib]-rg[r1]

                if path_len < min_path:
                    print('3. path too short')                

                #if path of significant returns exceeds min_path
                if path_len > min_path:
                    print('3.',  'Path length = ', path_len)                    

                    #exclude rays with large ZDR (heavy rain (mie-scattering))
                    ind = zdr_att[phi1:ib+1] > ZDRmax

                    if np.sum(ind) > 1:                    
                        print('4. Number of large ZDR = ', np.sum(ind)) 

                    if np.sum(ind) < 1:

                        #exclude rays where 3 or more values of RhoHV are less than 0.98, i.e. not rain
                        ind = np.logical_and(rhohv_f > 0.0, rhohv_f < 0.98)

                        if np.sum(ind[phi1:ib+1]) > 2:   
                            print('5. number of rhohv<0.98 = ', np.sum(ind[phi1:ib+1]))

                        if np.sum(ind[phi1:ib+1]) < 3:   
                            print('6. all conditions met for az_index = ',i,', azimuth = ',az[i], ', elevation = ', el2[i])

                            #index of good rays (value from 0 to 4320)
                            ray_index[file,i] = i
                            ray_az[file,i] = rad.azimuth['data'][i]
                            ray_el[file,i] = rad.elevation['data'][i]

                            uzh_att[ind] = np.nan
                            zdr_att[ind] = np.nan
                            #phidp_f[ind] = np.nan
                            #uphidp_sm_f[ind] = np.nan
			    #uphidp_sm_f.mask[ind] = np.nan
                            #rhohv_f[ind] = np.nan

                            startphi[i] = np.nanmedian(uphidp_f[phi1:phi1+10])

                            phiobs[i] = pdpmax
                            #phiobs_all[file,:] = phiobs

                            #kdpest = 1e-05 * (11.74 - 4.020*zdr_f - 0.140*zdr_f**2 + 0.130*zdr_f**3)*10 ** (uzh_f/10)
                            kdpest = 1e-05 * (11.74 - 4.020*zdr_att[phi1:] - 0.140*zdr_att[phi1:]**2 + 0.130*zdr_att[phi1:]**3)*10 ** (uzh_att[phi1:]/10)

                            tmpphi = np.nancumsum(kdpest)*rg_sp*2
                            #phiest[c] = tmpphi[ib]
                            phiest[i] = tmpphi[ib]
#                           print 'phiest = ', phiest[i] 

            else:
                print('2. No PhiDP between 4-6')
        #phiest is a function of ray, phiest(nrays)
        #phiest_all is a function of volume and ray, phiest_all(nvols,nrays)
        #delta is a function of ray, delta(nrays)
        #delta_all is a function of volume and ray, delta_all(nvols,nrays)

       	phiobs_all[file,0:Tdim] = phiobs
       	phiest_all[file,0:Tdim] = phiest
       	startphi_all[file,0:Tdim] = startphi

       	good_rays = np.sum(np.isfinite(phiest));
       	print('file =',file,'rays =',str(good_rays))
       	del rad
       	del zdr, rhohv, kdp, phidp, uzh, uphidp
       	gc.collect()
                    
        #print phiobs.shape   
        #delta = ((phiest-phiobs)/phiobs)*100
        #print delta.shape
        #print file
        #delta_all[file,:] = delta
        #print 'end'    
        #filename = outdir + 'file%03.d_phiest_phiobs_delta' %(file)
        #data_save=np.vstack((phiest,phiobs,delta))
        #np.save(filename,data_save)          

    #filename = outdir + 'good_rays'     
    #np.save(filename,good_rays)
    
    print("total rays = ", np.sum(np.isfinite(phiest_all.flatten())))
    if np.sum(np.isfinite(phiest_all.flatten())) !=0:
        print("phiest and phiobs values exist")
        phi_dir=os.path.join(outdir,'phi_files')
        if not os.path.exists(phi_dir):
            os.makedirs(phi_dir) 
        phase_dir=os.path.join(outdir,'phase_files')
        if not os.path.exists(phase_dir):
            os.makedirs(phase_dir) 

        phiest_filename = os.path.join(phi_dir, 'phiest_all_att_' + day)
        np.save(phiest_filename,phiest_all)
        phiobs_filename = os.path.join(phi_dir, 'phiobs_all_att_' + day)
        np.save(phiobs_filename,phiobs_all)
        startphi_filename = os.path.join(phase_dir, 'startphi_all_' + day)
        np.save(startphi_filename,startphi_all)
        return True
    else:
        return False



#--------------------------------------------------------------------------------------------------------------------------
def horiz_zdr(datadir, date, outdir, ml_zdr, zcorr,scan_type):
    
    filelist = glob.glob(datadir + date + '/' + scan_type + '/*.nc')
    filelist.sort()
    nfiles=len(filelist)
    
#   T = np.zeros((nfiles))*np.nan
#   num18 = np.zeros(nfiles)*np.nan
#   stdZDR18  = np.zeros(nfiles)*np.nan
#    medZDR18  = np.zeros(int(nfiles/2))*np.nan
    medZDR18 =[]
    T_arr = []

    
    for file in range(0,nfiles):
        #print filelist[file]
        print(file)
        rad=pyart.io.read(filelist[file])

        #Create time array
        timeT = rad.metadata['start_datetime']
        print(timeT)
        hh = float(timeT[11:13])
        mm = float(timeT[14:16])
        ss = float(timeT[17:19])
#        T[file] = hh + mm/60.0 + ss/3600.0

       	#T_arr.append(time)

        #Extract dimensions
        Rdim = rad.ngates
        Edim = rad.nsweeps
        Tdim = rad.nrays
        Adim = int(Tdim/Edim)
        
       	exclusions = SETTINGS.EXCLUSIONS 
        exclude_radials = np.any([np.all([rad.elevation['data']>=ele[0],
                                  rad.elevation['data']<ele[1],
                                  rad.azimuth['data']>=azi[0],
                                  rad.azimuth['data']<azi[1]],axis=0) for ele, azi in exclusions],axis=0)
       	az_index = np.where(~exclude_radials)[0]

        #Extract data
        try:
            rg = copy.deepcopy(rad.range['data']/1000)
            rg_sp = rg[1]-rg[0]
            max_gate = rg.size
            el = copy.deepcopy(rad.elevation['data'])
            el = el[::360]
            radh = copy.deepcopy(rad.altitude['data'])
            az = copy.deepcopy(rad.azimuth['data'])

            uzh = copy.deepcopy(rad.fields['dBuZ']['data'][az_index,:])#[rad.sweep_start_ray_index['data'][0]]
            uzh = uzh + zcorr
            zdr = copy.deepcopy(rad.fields['ZDRu']['data'][az_index,:])
            rhohv = copy.deepcopy(rad.fields['RhoHVu']['data'][az_index,:])
            phidp = copy.deepcopy(rad.fields['PhiDP']['data'][az_index,:])
            ind = phidp > 180
            phidp[ind] = phidp[ind] - 360
            ind = phidp < -180
            phidp[ind] = phidp[ind] + 360
            sqi = copy.deepcopy(rad.fields['SQIu']['data'][az_index,:])
        except:
            print("Couldn't load all variables")    
            continue

        beam_height = np.empty((Tdim,Rdim))
        for j in np.arange(0,Edim):
            for i in np.arange(0,Adim):
                beam_height[(Adim*j)+i,:] = radh/1000 + np.sin(np.deg2rad(el[j]))*rg + np.sqrt(rg**2 + (6371*4/3.0)**2) - (6371*4/3.0);

        beam_height = beam_height[az_index,:]

        #Extract melting layer height for the given radar scan time to use as a threshold on data selection
        mlh, _ = extract_ml_zdr(timeT, ml_zdr)

        zind = beam_height > mlh   
        uzh[zind==True] = np.nan    
        zdr[zind==True] = np.nan
        phidp[zind==True] = np.nan
        rhohv[zind==True] = np.nan
        sqi[zind==True] = np.nan

        #Set first three range gates to NaN
        uzh[:,0:3] = np.nan
        zdr[:,0:3] = np.nan
        phidp[:,0:3] = np.nan
        rhohv[:,0:3] = np.nan
        sqi[:,0:3] = np.nan

        ind=np.all([rhohv>0.99, sqi>0.3, phidp>0, phidp<6, uzh>15, uzh<=18],axis=0)
#        ind=np.all([rhohv>0.99, phidp>0, phidp<6, uzh>18, uzh<=21],axis=0)
 #       ind=np.all([rhohv>0.99, phidp>0, phidp<6, uzh>21, uzh<=24],axis=0)
#
        if ind.sum() >10:
#           num18[file] = np.sum(ind==True)
#           stdZDR18[file] = np.nanstd(zdr[ind==True])
       	    T_arr.append(timeT)
            medZDR18.append(np.nanmedian(zdr[ind==True]))

       	del rad
        del zdr, rhohv, uzh, phidp
        gc.collect()
    print(T_arr) 
    return T_arr, medZDR18

