# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 15:22:11 2016

@author: 
Maximilian N. Guenther
Battcock Centre for Experimental Astrophysics,
Cavendish Laboratory,
JJ Thomson Avenue
Cambridge CB3 0HE
Email: mg719@cam.ac.uk
"""

import astropy.io.fits as pyfits
import fitsio
import os, sys, glob, copy, collections, datetime
import numpy as np



"""

Possible keys:


a) Nightly Summary Fits file
From 'CATALOGUE' (per object):
['OBJ_ID', 'RA', 'DEC', 'REF_FLUX', 'CLASS', 'CCD_X', 'CCD_Y', 'FLUX_MEAN', 'FLUX_RMS', 'MAG_MEAN', 'MAG_RMS', 'NPTS', 'NPTS_CLIPPED']

From 'IMAGELIST' (per image):
['ACQUMODE', 'ACTIONID', 'ACTSTART', 'ADU_DEV', 'ADU_MAX', 'ADU_MEAN', 'ADU_MED', 'AFSTATUS', 'AGREFIMG', 'AGSTATUS', 'AG_APPLY', 'AG_CORRX', 'AG_CORRY', 'AG_DELTX', 'AG_DELTY', 'AG_ERRX', 'AG_ERRY', 'AIRMASS', 'BIASMEAN', 'BIASOVER', 'BIASPRE', 'BIAS_ID', 'BKG_MEAN', 'BKG_RMS', 'CAMERAID', 'CAMPAIGN', 'CCDTEMP', 'CCDTEMPX', 'CHSTEMP', 'CMD_DEC', 'CMD_DMS', 'CMD_HMS', 'CMD_RA', 'COOLSTAT', 'CROWDED', 'CTS_DEV', 'CTS_MAX', 'CTS_MEAN', 'CTS_MED', 'DARK_ID', 'DATE-OBS', 'DATE', 'DITHER', 'EXPOSURE', 'FCSR_ENC', 'FCSR_PHY', 'FCSR_TMP', 'FIELD', 'FILTFWHM', 'FLAT_ID', 'FLDNICK', 'GAIN', 'GAINFACT', 'HSS_MHZ', 'HTMEDXF', 'HTRMSXF', 'HTXFLAGD', 'HTXNFLAG', 'HTXRAD1', 'HTXSIG1', 'HTXTHTA1', 'HTXVAL1', 'IMAGE_ID', 'IMGCLASS', 'IMGTYPE', 'LST', 'MINPIX', 'MJD', 'MOONDIST', 'MOONFRAC', 'MOONPHSE', 'MOON_ALT', 'MOON_AZ', 'MOON_DEC', 'MOON_RA', 'NBSIZE', 'NIGHT', 'NUMBRMS', 'NXOUT', 'NYOUT', 'OBJECT', 'OBSSTART', 'PROD_ID', 'PSFSHAPE', 'RCORE', 'READMODE', 'READTIME', 'ROOFSTAT', 'SATN_ADU', 'SEEING', 'SKYLEVEL', 'SKYNOISE', 'STDCRMS', 'SUNDIST', 'SUN_ALT', 'SUN_AZ', 'SUN_DEC', 'SUN_RA', 'TC3_3', 'TC3_6', 'TC6_3', 'TC6_6', 'TCRPX2', 'TCRPX5', 'TCRVL2', 'TCRVL5', 'TEL_ALT', 'TEL_AZ', 'TEL_DEC', 'TEL_HA', 'TEL_POSA', 'TEL_RA', 'THRESHOL', 'TIME-OBS', 'TV6_1', 'TV6_3', 'TV6_5', 'TV6_7', 'VI_MINUS', 'VI_PLUS', 'VSS_USEC', 'WCSPASS', 'WCS_ID', 'WXDEWPNT', 'WXHUMID', 'WXPRES', 'WXTEMP', 'WXWNDDIR', 'WXWNDSPD', 'XENCPOS0', 'XENCPOS1', 'YENCPOS0', 'YENCPOS1', 'TMID']

From image data (per object and per image):
HJD
FLUX
FLUX_ERR
FLAGS
CCDX
CCDY
CENTDX_ERR
CENTDX
CENTDY_ERR
CENTDY
SKYBKG


b) Sysrem Fits File
Sysrem flux data (per object and per image):
SYSREM_FLUX3


c) BLS Fits File
From 'CATALOGUE' (for all objects):
['OBJ_ID', 'BMAG', 'VMAG', 'RMAG', 'JMAG', 'HMAG', 'KMAG', 'MU_RA', 'MU_RA_ERR', 'MU_DEC', 'MU_DEC_ERR', 'DILUTION_V', 'DILUTION_R', 'MAG_MEAN', 'NUM_CANDS', 'NPTS_TOT', 'NPTS_USED', 'OBJ_FLAGS', 'SIGMA_XS', 'TEFF_VK', 'TEFF_JH', 'RSTAR_VK', 'RSTAR_JH', 'RPMJ', 'RPMJ_DIFF', 'GIANT_FLG', 'CAT_FLG']

From 'CANDIDATE' data (only for candidates):
['OBJ_ID', 'RANK', 'FLAGS', 'PERIOD', 'WIDTH', 'DEPTH', 'EPOCH', 'DELTA_CHISQ', 'CHISQ', 'NPTS_TRANSIT', 'NUM_TRANSITS', 'NBOUND_IN_TRANS', 'AMP_ELLIPSE', 'SN_ELLIPSE', 'GAP_RATIO', 'SN_ANTI', 'SN_RED', 'SDE', 'MCMC_PERIOD', 'MCMC_EPOCH', 'MCMC_WIDTH', 'MCMC_DEPTH', 'MCMC_IMPACT', 'MCMC_RSTAR', 'MCMC_MSTAR', 'MCMC_RPLANET', 'MCMC_PRP', 'MCMC_PRS', 'MCMC_PRB', 'MCMC_CHISQ_CONS', 'MCMC_CHISQ_UNC', 'MCMC_DCHISQ_MR', 'MCMC_PERIOD_ERR', 'MCMC_EPOCH_ERR', 'MCMC_WIDTH_ERR', 'MCMC_DEPTH_ERR', 'MCMC_RPLANET_ERR', 'MCMC_RSTAR_ERR', 'MCMC_MSTAR_ERR', 'MCMC_CHSMIN', 'CLUMP_INDX', 'CAT_IDX', 'PG_IDX', 'LC_IDX']

"""



###############################################################################
# Getter (Main Program)
###############################################################################

def get(fieldname, keys, obj_id=None, obj_row=None, time_index=None, time_date=None, time_hjd=None, time_actionid=None, indexing='fits', fitsreader='fitsio', simplify=True, fnames=[], ngts_version='TEST10'):
    
    print 'Field name:', fieldname      

    #::: filenames
    if len(fnames)==0: fnames = standard_fnames(fieldname)
    
    if check_files(fnames):
        
        #::: objects    
        ind_objs, obj_ids = get_obj_inds(fnames, obj_id, obj_row, indexing, obj_sortby = 'obj_ids')
        print 'Object IDs:', obj_ids
        
        #::: time
        ind_time = get_time_inds(fnames, time_index, time_date, time_hjd, time_actionid)
        
        #::: get dictionary
        dic, keys = get_data(fnames, obj_ids, ind_objs, keys, ind_time, fitsreader)
        
        #::: simplify output if only for 1 object
        if simplify==True: dic = simplify_dic(dic)
            
        #::: check if all keys were retrieved
        check_dic(dic, keys)
    
        return dic
        
    else:
        
        return None


 
###############################################################################
# Fielnames Formatting
###############################################################################
   
def standard_fnames(fieldname, ngts_version='TEST10'):
    
    #::: on laptop (OS X)
    if sys.platform == "darwin":
    #    from fitsiochunked import ChunkedAdapter
        root = '/Users/mx/Big_Data/BIG_DATA_NGTS/2016/'
    
    #::: on ngtshead (LINUX)
    elif sys.platform == "linux" or sys.platform == "linux2":
    #    import sys
    #    sys.path.append('/home/sw/dev/fitsiochunked')
    #    from fitsiochunked import ChunkedAdapter
        root = '/ngts/pipeline/output/'+ngts_version+'/'
         
    try: 
        fnames = {}   
        fnames['nights'] = glob.glob(root + fieldname+'*.fits')[0]
        fnames['sysrem'] = glob.glob(root + 'sysrem/*' + fieldname + '*/*' + fieldname + '*_FLUX3.fits')[0]
        fnames['bls'] = glob.glob(root + 'bls/' + '*' + fieldname + '*')[0]
    except:
        fnames = None
        print '>>> '+fieldname+': Fits files do not exist.'

    return fnames
   
 

def check_files(fnames):
    
    if fnames!=None and os.path.isfile(fnames['nights']) and os.path.isfile(fnames['sysrem']) and os.path.isfile(fnames['bls']):
        return True
    else:
        return False         
 
 
 
###############################################################################
# Object Input Formatting
###############################################################################        
    
def get_obj_inds(fnames, obj_ids, obj_rows, indexing, obj_sortby = 'obj_ids'):
    
    inputtype = None
    
    #::: if no input is given, use all objects
    if obj_ids is None and obj_rows is None:
        
        inputtype = None
        ind_objs = slice(None)
        obj_ids = get_objids_from_indobjs(fnames, ind_objs)
        
    
    #::: if obj_id is given    
    elif obj_ids is not None and obj_rows is None:    
            
        inputtype = 'obj_ids'
        
        # b) test if non-empty list
        if isinstance(obj_ids, (collections.Sequence, np.ndarray)) and not isinstance(obj_ids, (str, unicode)) and len(obj_ids) > 0:
            # if list of integer or float -> convert to list of str            
            if not isinstance(obj_ids[0], str):
                obj_ids = map(int, obj_ids)
                obj_ids = map(str, obj_ids)
            # give all strings 6 digits
            obj_ids = objid_6digit(obj_ids)
            # connect obj_ids to ind_objs
            ind_objs = get_indobjs_from_objids(fnames, obj_ids)
            
        #c) test if file
        elif isinstance(obj_ids, str) and os.path.isfile(obj_ids):
            # load the file
            obj_ids = np.loadtxt(obj_ids, dtype='S6').tolist()
            # cast to list
            if isinstance(obj_ids, str):
                obj_ids = [obj_ids]
            # give all strings 6 digits
            obj_ids = objid_6digit(obj_ids)
            # connect obj_ids to ind_objs
            ind_objs = get_indobjs_from_objids(fnames, obj_ids)
            
        # d) test if str
        elif isinstance(obj_ids, str) and not os.path.isfile(obj_ids):
            # cast to list
            obj_ids = [obj_ids]
            # give all strings 6 digits
            obj_ids = objid_6digit(obj_ids)
            # connect obj_ids to ind_objs
            ind_objs = get_indobjs_from_objids(fnames, obj_ids)
            
        # e) test if int/float
        elif isinstance(obj_ids, (int, float)):
            # cast to list of type str
            obj_ids = [ str(int(obj_ids)) ]
            # give all strings 6 digits
            obj_ids = objid_6digit(obj_ids)
            # connect obj_ids to ind_objs
            ind_objs = get_indobjs_from_objids(fnames, obj_ids)
        
        # problems:
        else:
            print '--- Warning: "obj_id" data type not understood. ---'
            sys.exit()
            
            
    #::: if obj_row is given
    elif obj_ids is None and obj_rows is not None:
        
        inputtype = 'ind_objs'
        
        ind_objs = obj_rows
        
        # a) test if non-empty list
        if isinstance(ind_objs, (collections.Sequence, np.ndarray)) and not isinstance(ind_objs, (str, unicode)) and len(ind_objs) > 0:
            # if list of str or float -> convert to list of int           
            if isinstance(ind_objs[0], (str,float)):
                ind_objs = map(int, ind_objs)
            # count from 0 (python) or from 1 (fits)?
            if (indexing=='fits'):
                ind_objs = [x-1 for x in ind_objs]
            # connect obj_ids to ind_objs
            obj_ids = get_objids_from_indobjs(fnames, ind_objs)
            
        # b) test if file
        elif isinstance(ind_objs, str) and os.path.isfile(ind_objs):
            # load the file
            ind_objs = np.loadtxt(obj_rows, dtype='int').tolist()
            # count from 0 (python) or from 1 (fits)?
            if (indexing=='fits'):
                ind_objs = [x-1 for x in ind_objs]
            # connect obj_ids to ind_objs
            obj_ids = get_objids_from_indobjs(fnames, ind_objs)
            
        # c) test if str
        elif isinstance(ind_objs, str) and not os.path.isfile(ind_objs):
            # cast to list of type int
            ind_objs = [ int(ind_objs) ]
            # count from 0 (python) or from 1 (fits)?
            if (indexing=='fits'):
                ind_objs = [x-1 for x in ind_objs]
            # connect obj_ids to ind_objs
            obj_ids = get_objids_from_indobjs(fnames, ind_objs)
            
        # d) test if int/float 
        elif isinstance(ind_objs, (int, float)):
            # cast to list of type int
            ind_objs = [ int(ind_objs) ]
            # count from 0 (python) or from 1 (fits)?
            if (indexing=='fits'):
                ind_objs = [x-1 for x in ind_objs]
            # connect obj_ids to ind_objs
            obj_ids = get_objids_from_indobjs(fnames, ind_objs)

        
        # problems:
        else:
#            print '--- Warning: "obj_row" data type not understood. ---'
            warning = '"obj_row" data type not understood.'
            sys.exit(warning)
            
            
    #::: if obj_id and obj_row are both given        
    else: 
#        print '--- Warning: Only use either "obj_id" or "obj_row". ---'
        warning = 'Only use either "obj_id" or "obj_row".'
        sys.exit(warning)
        
       
        
    if inputtype is not None:
        
        #::: typecast to numpy arrays        
        obj_ids = np.array(obj_ids) 
        ind_objs = np.array(ind_objs)        
        
        #::: sort
        #TODO: UNCLEAN!!! This currently assumes the object IDs in the fits files are sorted like the row number!!!
        
        ind_objs = np.sort(ind_objs)
        obj_ids = np.sort(obj_ids)
        
#        if obj_sortby == 'obj_ids':
#            ind_sort = np.argsort( obj_ids )
#            obj_ids = obj_ids[ind_sort]
#            ind_objs = ind_objs[ind_sort]
#            
#        elif obj_sortby == 'ind_objs':
#            ind_sort = np.argsort( ind_objs )
#            obj_ids = obj_ids[ind_sort]
#            ind_objs = ind_objs[ind_sort]
#            
#        elif obj_sortby == 'original':
#            if inputtype == 'obj_ids':
#                pass
                #TODO: allow to keep the sorting of the input, e.g.  OBJ_IDs ['001337','000001'] corresponding to IND_OBJS [100, 1]
        
        
    #::: return     
    return ind_objs, obj_ids
        
        
        
def get_indobjs_from_objids(fnames, obj_list):
    with pyfits.open(fnames['nights'], mode='denywrite') as hdulist:
        ind_objs = np.in1d(hdulist['CATALOGUE'].data['OBJ_ID'].strip(), obj_list, assume_unique=True).nonzero()[0]
        obj_ids = hdulist['CATALOGUE'].data['OBJ_ID'][ind_objs].strip() #copy.deepcopy( hdulist['CATALOGUE'].data['OBJ_ID'][ind_objs].strip() )
        del hdulist['CATALOGUE'].data
        
        for obj_id in obj_list:
            if obj_id not in obj_ids:
#                print '--- Warning: obj_id',obj_id,'not found in fits file. ---'  
                warning = ' --- Warning: obj_id '+str(obj_id)+' not found in fits file. --- '
                print warning
#                sys.exit(warning)
                #TODO raise proper warning/error
        
    return ind_objs
    
    
    
def get_objids_from_indobjs(fnames, ind_objs):
    with pyfits.open(fnames['nights'], mode='denywrite') as hdulist:
        obj_ids = hdulist['CATALOGUE'].data['OBJ_ID'][ind_objs].strip() #copy.deepcopy( hdulist['CATALOGUE'].data['OBJ_ID'][ind_objs].strip() )
        del hdulist['CATALOGUE'].data
        
    obj_ids = objid_6digit(obj_ids)
    
    return obj_ids
    

    
def objid_6digit(obj_list):
    for i, obj_id in enumerate(obj_list):
        while len(obj_id)<6: 
            obj_id = '0'+obj_id
        obj_list[i] = obj_id

    return obj_list




###############################################################################
# Time Input Formatting
###############################################################################

def get_time_inds(fnames, time_index, time_date, time_hjd, time_actionid):
    
    if time_index is None and time_date is None and time_hjd is None and time_actionid is None:
        ind_time = slice(None)
        
        
        
    elif time_index is not None and time_date is None and time_hjd is None and time_actionid is None:
        # A) test if file 
        if isinstance(time_index, str) and os.path.isfile(time_index):
            # load the file
            time_index = np.loadtxt(time_index, dtype='int').tolist()
            # cast to list
            if isinstance(time_index, str):
                time_index = [time_index]

        # B) work with the data

        # if not list, make list
        if not isinstance(time_hjd, (tuple, list, np.ndarray)):
            ind_time = [time_index]
        else:
            ind_time = time_index
        
        
        
    elif time_index is None and time_date is not None and time_hjd is None and time_actionid is None:
        
        # A) test if file 
        if isinstance(time_date, str) and os.path.isfile(time_date):
            # load the file
            time_date = np.loadtxt(time_date, dtype='S22').tolist()
            # cast to list
            if isinstance(time_date, str):
                time_date = [time_date]

        # B) work with the data
        # a) test if non-empty list
        if isinstance(time_date, (collections.Sequence, np.ndarray)) and not isinstance(time_date, (str, unicode)) and len(time_date) > 0:
            # if list of int or float -> convert to list of str         
            if isinstance(time_date[0], (int,float)):
                time_date = map(str, time_date)
            # format if necessary
            if len(time_date[0]) == 8:
                time_date = [ x[0:4]+'-'+x[4:6]+'-'+x[6:] for x in time_date ]
            elif len(time_date[0]) == 10:
                time_date = [ x.replace('/','-') for x in time_date ]
            elif len(time_date[0]) > 10:        
                warning = '"time_date" format not understood.'
                sys.exit(warning)
            # connect to ind_time
            ind_time = get_indtime_from_timedate(fnames, time_date)
        
        # c) test if int/float 
        elif isinstance(time_date, (int, float)):
            # convert to str
            time_date = str(time_date)
            # format
            time_date = time_date[0:4]+'-'+time_date[4:6]+'-'+time_date[6:]
            # connect to ind_time
            ind_time = get_indtime_from_timedate(fnames, time_date)
            
        # d) test if str
        elif isinstance(time_date, str):
            
            # if single date, format if necessary
            if len(time_date) == 8:
                time_date = time_date[0:4]+'-'+time_date[4:6]+'-'+time_date[6:]
                
            # if single date, format if necessary
            elif len(time_date) == 10:
                time_date = [ x.replace('/','-') for x in time_date ]
                
            # if dates are given in a range ('20151104:20160101' or '2015-11-04:2016-01-01')
            elif len(time_date) > 10:
                time_date = get_time_date_from_range(time_date)
                
            else:
                sys.exit('Invalid format of value "time_date". Use e.g. 20151104, "20151104", "2015-11-04" or a textfile name like "dates.txt".')
                
            # connect to ind_time
            ind_time = get_indtime_from_timedate(fnames, time_date)
            
            
    
    elif time_index is None and time_date is None and time_hjd is not None and time_actionid is None:
        
        # A) test if file 
        if isinstance(time_hjd, str) and os.path.isfile(time_hjd):
            # load the file
            time_hjd = np.loadtxt(time_hjd, dtype='int').tolist()
            # cast to list
            if isinstance(time_hjd, str):
                time_hjd = [time_hjd]

        # B) work with the data
        # a) test if non-empty list
        if isinstance(time_hjd, (collections.Sequence, np.ndarray)) and not isinstance(time_hjd, (str, unicode)) and len(time_hjd) > 0:
            # if list of str or float -> convert to list of int           
            if isinstance(time_hjd[0], (str,float)):
                time_hjd = map(int, time_hjd)
            # connect obj_ids to ind_objs
            ind_time = get_indtime_from_timehjd(fnames, time_hjd)        
  
       # b) test if str/int/float 
        if isinstance(time_hjd, (str, int, float)):
            time_hjd = int(time_hjd)
            ind_time = get_indtime_from_timehjd(fnames, time_hjd)
            
            
            
    elif time_index is None and time_date is None and time_hjd is None and time_actionid is not None:
       
       # A) test if file 
        if isinstance(time_actionid, str) and os.path.isfile(time_actionid):
            # load the file
            time_actionid = np.loadtxt(time_actionid, dtype='S13').tolist()

        # B) work with the data
        # a) test if non-empty list
        if isinstance(time_actionid, (collections.Sequence, np.ndarray)) and not isinstance(time_actionid, (str, unicode)) and len(time_actionid) > 0:
            # if list of str or float -> convert to list of int         
            if isinstance(time_actionid[0], (str,float)):
                time_actionid = map(int, time_actionid)
            # connect to ind_time
            ind_time = get_indtime_from_timeactionid(fnames, time_actionid)
        
        # c) test if int/float
        elif isinstance(time_actionid, (int, float)):
            # convert to int
            time_actionid = int(time_actionid)
            # connect to ind_time
            ind_time = get_indtime_from_timeactionid(fnames, time_actionid)
            
        # d) test if str
        elif isinstance(time_actionid, str):
            
            # if single actioniod, convert to int
            if len(time_actionid) == 6:
                time_actionid = int(time_actionid)
                
            # if actionids are given in a range ('108583:108600')
            if len(time_actionid) > 6:
                time_actionid = get_time_actionid_from_range(time_actionid)
                
            # connect to ind_time
            ind_time = get_indtime_from_timeactionid(fnames, time_actionid)     
                
    else: 
        warning = 'Only use either "time_index" or "time_date" or "time_hjd" or "time_actionid".'
        sys.exit(warning)        
        
    return ind_time



def get_indtime_from_timedate(fnames, time_date):
    with pyfits.open(fnames['nights'], mode='denywrite') as hdulist:
        ind_time = np.in1d(hdulist['IMAGELIST'].data['DATE-OBS'].strip(), time_date).nonzero()[0]
        
        # if not list, make list
        if not isinstance(time_date, (tuple, list, np.ndarray)):
            time_date = [time_date]
            
        for date in time_date:
            if date not in hdulist['IMAGELIST'].data['DATE-OBS'][ind_time].strip():
                warning = 'Date '+ date +' not found in fits file.'
                print warning
#                sys.exit(warning)
                #TODO raise proper warning/error      
        del hdulist['IMAGELIST'].data
        
    return ind_time
    
    
    
def get_indtime_from_timehjd(fnames, time_hjd):
    with pyfits.open(fnames['nights'], mode='denywrite') as hdulist:
        ind_time = np.in1d(np.int64(hdulist['HJD'].data[0]/3600./24.), time_hjd).nonzero()[0]

        # if not list, make list
        if not isinstance(time_hjd, (tuple, list, np.ndarray)):
            time_hjd = [time_hjd]
            
        for hjd in time_hjd:
            if hjd not in np.int64(hdulist['HJD'].data[0][ind_time]/3600./24.):
                warning = 'Date-HJD '+ hjd +' not found in fits file.'
                sys.exit(warning)
                #TODO raise proper warning/error      
        del hdulist['IMAGELIST'].data
        
    return ind_time



def get_indtime_from_timeactionid(fnames, time_actionid):
    with pyfits.open(fnames['nights'], mode='denywrite') as hdulist:
        ind_time = np.in1d(hdulist['IMAGELIST'].data['ACTIONID'], time_actionid).nonzero()[0]
        
        # if not list, make list
        if not isinstance(time_actionid, (tuple, list, np.ndarray)):
            time_actionid = [time_actionid]
            
        for actionid in time_actionid:
            if actionid not in hdulist['IMAGELIST'].data['ACTIONID'][ind_time]:
                warning = 'Action-ID '+ str(actionid) +' not found in fits file.'
                print warning
#                sys.exit(warning)
                #TODO raise proper warning/error      
        del hdulist['IMAGELIST'].data
        
    return ind_time
    
    

# mother   
def get_time_date_from_range(date_range):    
    start_date, end_date = solve_range(date_range)
    
    time_date = []
    start_date, end_date = format_date(start_date, end_date)
    for bufdate in perdelta(start_date, end_date, datetime.timedelta(days=1)):
        time_date.append(bufdate.strftime("%Y-%m-%d"))
    
    return time_date
    

    
# daughter of get_time_date_from_range(date_range)
def format_date(start_date, end_date):
    if isinstance(start_date, int):
        start_date = str(start_date)
        
    if isinstance(start_date, str):
        if len(start_date) == 8:       
            start_date = datetime.datetime.strptime(str(start_date), '%Y%m%d')
        elif len(start_date) == 10:  
            start_date.replace('/','-')
            start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
            
    if isinstance(end_date, int):
        end_date = str(end_date)
        
    if isinstance(end_date, str):
        if len(end_date) == 8:       
            end_date = datetime.datetime.strptime(str(end_date), '%Y%m%d')
        elif len(end_date) == 10: 
            end_date = end_date.replace('/','-')
            end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d')

    return start_date, end_date



# daughter of get_time_date_from_range(date_range)
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta



# daughter of 
# 1) get_time_date_from_range(date_range) 
# 2) get_time_actionid_from_range(actionid_range)
def solve_range(date_range):
    # input: 
    # 1) '20151104:20160101' or '2015-11-04:2016-01-01'
    # 2) '108583:108600'
    try:
        start_date, end_date = date_range.split(':')
    except:
        sys.exit('"time_date" data type not understood.')
    return start_date, end_date
    


# mother    
def get_time_actionid_from_range(actionid_range):    
    start_actionid, end_actionid = solve_range(actionid_range)
    start_actionid = int(start_actionid)
    end_actionid = int(end_actionid)
    
    time_actionid = range(start_actionid, end_actionid+1)
    
    return time_actionid      
    
    

###############################################################################
# get dictionary with fitsio/pyfits getters 
###############################################################################
def get_data(fnames, obj_ids, ind_objs, keys, ind_time, fitsreader):

    #::: check keys
    if isinstance (keys, str): keys = [keys]
        
    #::: check ind_objs
    if not isinstance(ind_objs, slice) and len(ind_objs) == 0:
        print ' --- Warning: None of the given objects found in the fits files. Return empty dictionary. --- '
        dic = {}
        
    elif not isinstance(ind_time, slice) and len(ind_time) == 0:
        print ' --- Warning: None of the given times found in the fits files. Return empty dictionary. --- '
        dic = {}
        
    else:
            
        # in case OBJ_IDs was not part of the keys, add it to have array sizes/indices that are always confirm with the nightly fits files
#        dont_save_obj_id = False
        if 'OBJ_ID' not in keys: 
#            dont_save_obj_id = True
            keys.append('OBJ_ID')   
    
            
        if fitsreader=='astropy' or fitsreader=='pyfits': dic = pyfits_get_data(fnames, obj_ids, ind_objs, keys, ind_time=ind_time) 
        elif fitsreader=='fitsio' or fitsreader=='cfitsio': dic = fitsio_get_data(fnames, obj_ids, ind_objs, keys, ind_time=ind_time) 
        else: sys.exit('"fitsreader" can only be "astropy"/"pyfits" or "fitsio"/"cfitsio".')    
        
        #TODO: make clear that from now on OBJ_IDs is always part of the dictionary!
        # in case OBJ_IDs was not part of the keys, remove it again
#        if dont_save_obj_id == True:
#            del dic['OBJ_ID']
#            keys.remove('OBJ_ID')
        
        
        #TODO: read out dimensions
#        if not isinstance(ind_objs, slice):
#            dic['N_objects'] = np.array( [len(ind_objs)] )
#        else:
#            dic['N_objects'] = np.array( [np.nan] )
#            
#        if not isinstance(ind_time, slice): 
#            dic['N_times'] = np.array( [len(ind_time)] )
#        else:
#            dic['N_times'] = np.array( [np.nan] )
            
        
    return dic, keys



###############################################################################
# pyfits getter 
###############################################################################


def pyfits_get_data(fnames, obj_ids, ind_objs, keys, ind_time=slice(None), CCD_bzero=0., CCD_precision=32., CENTD_bzero=0., CENTD_precision=1024.):
     
    #::: dictionary
    dic = {}
    
    #, memmap=True, do_not_scale_image_data=True
    with pyfits.open(fnames['nights'], mode='denywrite') as hdulist:
        
        #::: CATALOGUE
        hdukey = 'CATALOGUE'
        hdu = hdulist[hdukey].data
        for key in np.intersect1d(hdu.names, keys):
            dic[key] = hdu[key][ind_objs] #copy.deepcopy( hdu[key][ind_objs] )
        del hdu, hdulist[hdukey].data
            
        #::: IMAGELIST
        hdukey = 'IMAGELIST'
        hdu = hdulist[hdukey].data
        for key in np.intersect1d(hdu.names, keys):
            dic[key] = hdu[key][ind_time] #copy.deepcopy( hdu[key][ind_time] )
        del hdu, hdulist[hdukey].data
        
        #::: DATA HDUs
        for _, hdukeyinfo in enumerate(hdulist.info(output=False)):
            hdukey = hdukeyinfo[1]
            if hdukey in keys:
                key = hdukey
                dic[key] = hdulist[key].data[ind_objs][:,ind_time] #copy.deepcopy( hdulist[key].data[ind_objs][:,ind_time] )
                if key in ['CCDX','CCDY']:
                    dic[key] = (dic[key] + CCD_bzero) / CCD_precision
                if key in ['CENTDX','CENTDX_ERR','CENTDY','CENTDY_ERR']:
                    dic[key] = (dic[key] + CENTD_bzero) / CENTD_precision
                del hdulist[key].data
        
        del hdulist
            


    with pyfits.open(fnames['sysrem'], mode='denywrite') as hdulist_sysrem:
        for i, hdukey in enumerate(hdulist_sysrem.info(output=False)):
            if hdukey[1] in keys:
                key = hdukey[1]
                dic[key] = hdulist_sysrem[key].data[ind_objs][:,ind_time] #copy.deepcopy( hdulist_sysrem[key].data[ind_objs][:,ind_time] )#in s
                del hdulist_sysrem[key].data
                
        del hdulist_sysrem
        
        
    
    with pyfits.open(fnames['bls'], mode='denywrite') as hdulist_bls:
        
        #first little hack: transform from S26 into S6 dtype with .astype('|S6') or .strip()!
        #second little hack: only choose rank 1 output (5 ranks output by orion into the fits files, in 5 subsequent rows)
        ind_objs_bls = np.in1d(hdulist_bls['CANDIDATES'].data['OBJ_ID'].strip(), obj_ids).nonzero()[0] #indices of the candidates
        ind_rank1 = np.where( hdulist_bls['CANDIDATES'].data['RANK'] == 1 )[0]
        ind_objs_bls = np.intersect1d( ind_objs_bls, ind_rank1 )
        
        
        #::: CATALOGUE
        hdukey = 'CATALOGUE'
        hdu = hdulist_bls[hdukey].data
        for key in np.intersect1d(hdu.names, keys):
            if key!='OBJ_ID':
                dic[key] = hdu[key][ind_objs] #copy.deepcopy( hdu[key][ind_objs] )
        del hdu, hdulist_bls[hdukey].data
        

        #::: CANDIDATES (different indices!)
        hdukey = 'CANDIDATES'    
        hdu = hdulist_bls[hdukey].data
        subkeys = np.intersect1d(hdu.names, keys)
        # EXCLUDE OBJ_IDs from subkeys
        if 'OBJ_ID' in subkeys: subkeys = np.delete(subkeys, np.where(subkeys=='OBJ_ID'))
            
        if subkeys.size!=0:            
            # see if any BLS candidates are in the list
            if len(ind_objs_bls)!=0:
                bls_data_objid = np.char.strip( hdu['OBJ_ID'][ind_objs_bls] )
                
                # go through all subkeys
                for key in subkeys:
                    # read out data for this key
                    bls_data = hdu[key][ind_objs_bls]
                    
                    # write them at the right place into the dictionary
                    # initialize empty dictionary entry, size of all requested ind_objs
                    dic[key] = np.zeros( len(ind_objs) )
                    # go through all requested obj_ids
                    for i, singleobj_id in enumerate(obj_ids):
                        if singleobj_id in bls_data_objid:
                            i_bls = np.where( bls_data_objid == singleobj_id )[0]
                            dic[key][i] = bls_data[i_bls]
            else:
                # go through all subkeys
                for key in subkeys:
                    # initialize empty dictionary entry, size of all requested ind_objs
                    dic[key] = np.zeros( len(ind_objs) )
     


    #::: output as numpy ndarrays
    for key, value in dic.iteritems():
        dic[key] = np.array(value)
            
    
    return dic




###############################################################################
# fitsio getter 
###############################################################################
def fitsio_get_data(fnames, obj_ids, ind_objs, keys, ind_time=slice(None), CCD_bzero=0., CCD_precision=32., CENTD_bzero=0., CENTD_precision=1024.):
        
    #::: dictionary
    dic = {}
        
        
    ##################### fnames['nights'] #####################
    
    with fitsio.FITS(fnames['nights'], vstorage='object') as hdulist:
        
        allobjects = False
        if isinstance (ind_objs, slice):
            N_objs = int( hdulist['CATALOGUE'].get_nrows() )
            ind_objs = range(N_objs)
            allobjects = True
            
        if isinstance (ind_time, slice):
            N_time = int( hdulist['IMAGELIST'].get_nrows() )
            ind_time = range(N_time)
            
            
        #::: CATALOGUE
        hdukey = 'CATALOGUE'
        hdunames = hdulist[hdukey].get_colnames()
        subkeys = np.intersect1d(hdunames, keys)
        if subkeys.size!=0:
            data = hdulist[hdukey].read(columns=subkeys, rows=ind_objs)
            if isinstance(subkeys, str): subkeys = [subkeys]
            for key in subkeys:
                dic[key] = data[key] #copy.deepcopy( data[key] )
            del data
        
        #::: IMAGELIST
        hdukey = 'IMAGELIST'
        hdunames = hdulist[hdukey].get_colnames()
        subkeys = np.intersect1d(hdunames, keys)
        if subkeys.size!=0:
            data = hdulist[hdukey].read(columns=subkeys, rows=ind_time)
            if isinstance(subkeys, str): subkeys = [subkeys]
            for key in subkeys:
                dic[key] = data[key] #copy.deepcopy( data[key] )
            del data
            
        # TODO: very inefficient - reads out entire image first, then cuts
        # TODO: can only give ind_time in a slice, not just respective dates
        #::: DATA HDUs
        j = 0
        while j!=-1:
            try:
                hdukey = hdulist[j].get_extname()
                if hdukey in keys:
                    key = hdukey
                    
                    #::: read out individual objects (more memory efficient)
                    if allobjects == False:
                        dic[key] = np.zeros(( len(ind_objs), len(ind_time) ))
                        for i, ind_singleobj in enumerate(ind_objs):
                            buf = hdulist[hdukey][slice(ind_singleobj,ind_singleobj+1), slice( ind_time[0], ind_time[-1]+1)]
                            #::: select the wished times only (if some times within the slice are not wished for)
                            if buf.shape[1] != len(ind_time):
                                ind_timeX = [x - ind_time[0] for x in ind_time]
                                buf = buf[:,ind_timeX]
                            dic[key][i,:] = buf
                        del buf
                        
                    #::: read out all objects at once
                    else:
                        buf = hdulist[hdukey][:, slice( ind_time[0], ind_time[-1]+1)]
                        if buf.shape[1] != len(ind_time):
                            ind_timeX = [x - ind_time[0] for x in ind_time]
                            buf = buf[:,ind_timeX]
                        dic[key] = buf
                        del buf                        
                        
                    if key in ['CCDX','CCDY']:
                        dic[key] = (dic[key] + CCD_bzero) / CCD_precision
                    if key in ['CENTDX','CENTDX_ERR','CENTDY','CENTDY_ERR']:
                        dic[key] = (dic[key] + CENTD_bzero) / CENTD_precision
                j += 1
            except:
                break
                
            

    ##################### fnames['sysrem'] #####################
                
    with fitsio.FITS(fnames['sysrem'], vstorage='object') as hdulist_sysrem:
        j = 0
        while j!=-1:
            try:
                hdukey = hdulist_sysrem[j].get_extname()
                if hdukey in keys:
                    key = hdukey
                    
                    #::: read out individual objects (more memory efficient)
                    if allobjects == False:
                        dic[key] = np.zeros(( len(ind_objs), len(ind_time) ))
                        for i, ind_singleobj in enumerate(ind_objs):
                            buf = hdulist_sysrem[hdukey][slice(ind_singleobj,ind_singleobj+1), slice( ind_time[0], ind_time[-1]+1)]
                            #::: select the wished times only (if some times within the slice are not wished for)
                            if buf.shape[1] != len(ind_time):
                                ind_timeX = [x - ind_time[0] for x in ind_time]
                                buf = buf[:,ind_timeX]
                            dic[key][i,:] = buf
                        del buf
                        
                    #::: read out all objects at once
                    else:
                        buf = hdulist_sysrem[hdukey][:, slice( ind_time[0], ind_time[-1]+1)]
                        if buf.shape[1] != len(ind_time):
                            ind_timeX = [x - ind_time[0] for x in ind_time]
                            buf = buf[:,ind_timeX]
                        dic[key] = buf
                        del buf
                j += 1
            except:
                break
            
            
            
    ##################### fnames['bls'] #####################
                        
    with fitsio.FITS(fnames['bls'], vstorage='object') as hdulist_bls:
        
        #first little hack: transform from S26 into S6 dtype with .astype('|S6') or .strip()!
        #second little hack: only choose rank 1 output (5 ranks output by orion into the fits files, in 5 subsequent rows)
        ind_objs_bls = np.in1d( np.char.strip(hdulist_bls['CANDIDATES'].read(columns='OBJ_ID')), obj_ids).nonzero()[0] #indices of the candidates
        ind_rank1 = np.where( hdulist_bls['CANDIDATES'].read(columns='RANK') == 1 )[0]
        ind_objs_bls = np.intersect1d( ind_objs_bls, ind_rank1 )
        
        
        #::: CATALOGUE
        hdukey = 'CATALOGUE'
        hdunames = hdulist_bls[hdukey].get_colnames()
        subkeys = np.intersect1d(hdunames, keys)
        # EXCLUDE OBJ_IDs from subkeys
        if 'OBJ_ID' in subkeys: subkeys = np.delete(subkeys, np.where(subkeys=='OBJ_ID'))
        if subkeys.size!=0:
            data = hdulist_bls[hdukey].read(columns=subkeys, rows=ind_objs)
            if isinstance(subkeys, str): subkeys = [subkeys]
            for key in subkeys:
                dic[key] = data[key] #copy.deepcopy( data[key] )
            del data
        
        
        #::: CANDIDATES (different indices!)
        hdukey = 'CANDIDATES'        
        hdunames = hdulist_bls[hdukey].get_colnames()
        subkeys = np.intersect1d(hdunames, keys)
        # EXCLUDE OBJ_IDs from subkeys
        if 'OBJ_ID' in subkeys: subkeys = np.delete(subkeys, np.where(subkeys=='OBJ_ID'))
            
        if subkeys.size!=0:
                
            # see if any BLS candidates are in the list
            if len(ind_objs_bls)!=0:
                
                # Now, for this one, again INCLUDE OBJ_IDs in subkeys (as last subkey)
                if 'OBJ_ID' not in subkeys: subkeys = np.append(subkeys, 'OBJ_ID')
                
                bls_data = hdulist_bls[hdukey].read(columns=subkeys, rows=ind_objs_bls)
            # write them at the right place into the dictionary
                # EXCLUDE OBJ_IDs from subkeys
                if 'OBJ_ID' in subkeys: subkeys = np.delete(subkeys, np.where(subkeys=='OBJ_ID'))
                #typecast to list if needed
                if isinstance(subkeys, str): subkeys = [subkeys]
                # go through all subkeys
                for key in subkeys:
                    # initialize empty dictionary entry, size of all requested ind_objs
                    dic[key] = np.zeros( len(ind_objs) )
                    # go through all requested obj_ids
                    for i, singleobj_id in enumerate(obj_ids):
                        if singleobj_id in np.char.strip(bls_data['OBJ_ID']):
                            i_bls = np.where( np.char.strip(bls_data['OBJ_ID']) == singleobj_id )
                            dic[key][i] = bls_data[key][i_bls]
            else:
                # go through all subkeys
                for key in subkeys:
                    # initialize empty dictionary entry, size of all requested ind_objs
                    dic[key] = np.zeros( len(ind_objs) )
                    
    return dic



###############################################################################
# Simplify output if only one object is retrieved
###############################################################################  
def simplify_dic(dic):
    
    for key, value in dic.iteritems():
        if value.shape[0] == 1:
            dic[key] = value[0]
        elif (len(value.shape) > 1) and (value.shape[1] == 1):
            dic[key] = value[:,0]
        
    return dic
    
    
    
###############################################################################
# Check if all keys are retrieved
###############################################################################  
def check_dic(dic, keys):
    
    print '###############################################################################'
            
    fail = False
    for key in keys:
        if key not in dic:
            print 'Failure: key',key,'not read into dictionary.'
            fail = True
    
    if fail == False:
        print 'Success: All keys successfully read into dictionary.'
        
    print '###############################################################################'
        
        
    return
    


###############################################################################
# MAIN
###############################################################################    
if __name__ == '__main__':
    pass
#    dic = get( 'NG0304-1115', ['OBJ_ID','SYSREM_FLUX3','RA','DEC','HJD','FLUX','PERIOD','WIDTH'], obj_row=range(0,10), time_date='20151104', indexing='python', fitsreader='pyfits', simplify=False )
#    for key in dic:
#        print '------------'
#        print type(dic[key])
#        print key, dic[key].shape
#        print dic[key]
#        print '------------'
