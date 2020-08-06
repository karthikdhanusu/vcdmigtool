import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET
import xml.etree.cElementTree as ET
import uuid,time, sys,urllib3
from time import gmtime,strftime
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


Sessions_add = "/api/sessions"
Cat_record = "/api/query?type=catalog&amp;format=records"
gateway_query = '/vchs/query?type=edgeGateway'
vAPP_query = '/api/query?type=vApp&amp;format=references'
vAPP_queryall = '/api/query?type=vApp&pageSize=4000&page=1'
vAPPTemplate_queryall = '/api/query?type=vAppTemplate&pageSize=4000&page=1'
VM_queryall = '/api/query?type=vm&pageSize=4000&page=1'
Media_queryall = '/api/query?type=media&pageSize=4000&page=1'
orgvdc_query = '/api/query?type=orgVdc&amp;format=references'
vm_query = '/api/query?type=vm&amp;format=references'
shutdownaction = '/power/action/shutdown'
poweroffaction = '/power/action/powerOff'
undeploy = '/action/undeploy'
Catitem_append = "/api/catalog/"
adminorg_append = "/api/admin/org/"
catalog = "/catalogs"
actionupload_append = "/action/upload"
vAPPtemplate_append = "/api/vAppTemplate/"
media_append = "/api/media/"
ejectmedia_append = '/media/action/ejectMedia'
enabledownload_append = "/action/enableDownload"
disabledownload_append = "/action/disableDownload"
CatalogName = 'VCA-Migration'
description = 'vCA Templates / Media'
session_append = "/rest/com/vmware/cis/session"
listdatastore_append = "/rest/vcenter/datastore"
lib_append = "/rest/com/vmware/content/library"
locallib_append = "/rest/com/vmware/content/local-library"
libfind_append = "/rest/com/vmware/content/library?~action=find"
libitem_append = '/rest/com/vmware/content/library/item'
updatesession_append = '/rest/com/vmware/content/library/item/update-session'
updatesessionfile_append = '/rest/com/vmware/content/library/item/updatesession/file'
requestURI_append = '/rest/com/vmware/content/library/item/updatesession/file/id:'
completesession_append = '/rest/com/vmware/content/library/item/update-session/id:'
keepalivesession_append  = '/rest/com/vmware/content/library/item/update-session/id:'
libraryitem_append = '/rest/com/vmware/content/library/item/id:'
fileid_append = '/rest/com/vmware/content/library/item/file/id:'
client_token = str(uuid.uuid4())


                                                                        #### Json Data ###

jsondat1 = '{  "client_token": "'
jsondat2 = '",  "create_spec": {        "storage_backings": [      {        "datastore_id": "'
jsondat3 = '",        "type": "DATASTORE"      }    ],    "name": "'
jsondat4 = '",    "type": "LOCAL",         "description": "'
jsondat5 = '"  }}'
lijsondat1 = '{  "client_token": "'
lijsondat2 = '",  "create_spec": {    "library_id": "'
lijsondat3 = '",    "description":"'
lijsondat4 = '",    "type":"iso",        "name": "'
lijsondat6 = '",    "type":"ovf",        "name": "'
lijsondat5 = '"  }}'
'''''''''
lijsondat1 = '{  "client_token": "'
lijsondat2 = '",  "create_spec": {    "library_id": "'
lijsondat3 = '",    "description":"'
lijsondat4 = '",    "type":"iso",        "size":'
lijsondat5 = '",    "type":"ovf",        "size":'
lijsondat6 = ',        "name": "'
lijsondat7 = '"  }}'
'''
usjsondat1 = '{        "client_token": "'
usjsondat2 = '",        "create_spec": {            "library_item_id": "'
usjsondat3 = '"        }}'
rujsondat1 = '{    "file_spec": {                "name": "'
rujsondat3 = '",        "size":"'
rujsondat4 = '",        "source_type": "PUSH"    }}'
data1 = '{  "file_name": "'
data2 = '"}'
keepalivedata1 = '{  "client_progress": '
keepalivedata2 = "}'"

                                                    ###### Banner #####

def banner(text, ch='#', length=100):
    spaced_text = ' %s ' % text
    banner = spaced_text.center(length, ch)
    return banner

                                                ### Get GMT time now ###

def timenow():
    a = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    return a


                                                         ##### Login to On-Demand Environment #####
def login_ondemand(API_URL, VCAUser, VCAPasswd, VCAOrgName):
    SessionsURL = API_URL + Sessions_add
    SessionUser = VCAUser + '@' + VCAOrgName
    odlogin = requests.post( SessionsURL, headers = {'Accept': 'application/*+xml;version=5.7'}, auth=HTTPBasicAuth(SessionUser, VCAPasswd))
    odxvchsauth = odlogin.headers.get('x-vcloud-authorization')
    sessionsxml = odlogin.content
    sessioncontxml = ET.fromstring(sessionsxml)
    c = sessioncontxml.findall(".//*[@type='application/vnd.vmware.vcloud.org+xml']")
    for child in c:
        if 'rel' in child.attrib:
            href = child.attrib['href']
            orgid = href[href.find('/api/org/')+9:]
    return odxvchsauth,href


                                    ##### Login to Subscription Environment #####
def login_subscription(SubRawURL,VCAUser,VCAPasswd,VCAOrgName):
    SubsessionURL = SubRawURL + Sessions_add
    SessionUser = VCAUser + '@' + VCAOrgName
    Sublogin = requests.post(SubsessionURL, headers = {'Accept': 'application/*+xml;version=5.7'}, auth=HTTPBasicAuth(SessionUser, VCAPasswd))
    subxvchsauth = Sublogin.headers.get('x-vcloud-authorization')
    sessionssubxml = Sublogin.content
    sessionsubcontxml = ET.fromstring(sessionssubxml)
    d = sessionsubcontxml.findall(".//*[@type='application/vnd.vmware.vcloud.org+xml']")
    for child in d:
        if 'rel' in child.attrib:
            href = child.attrib['href']
            orgidsub = href[href.find('/api/org/')+9:]
    return subxvchsauth,href

                                    ##### vCenter Login ####

def PCClogin(PCCHost, PCCUser, PCCpass):
    Sessionrequest = requests.post(PCCHost + session_append, verify = True, auth=HTTPBasicAuth(PCCUser, PCCpass))
    session_ID = Sessionrequest.json()['value']
    return session_ID

                                    ###### Keep-Alive settings for vCenter and vCloud Director###

def keepalive(PCCHost,session_ID,odxvchsauth,orgurl):
    keepalivebanner = banner(text="Keep Alive Window, Don't close this window till all the migrations are completed")
    print(keepalivebanner)
    time.sleep(600)
    requests.get(orgurl,headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    getliurl = PCCHost+lib_append
    libget = requests.get(getliurl, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    lolibjson = libget.json()['value']
    for lolibds in lolibjson:
        getliurli = PCCHost+libitem_append+'?library_id='+lolibds
        liget = requests.get(getliurli, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
        lolidjsoni = liget.json()['value']
        for lolid in lolidjsoni:
            libitemurl = PCCHost+libraryitem_append+lolid
            libitemget = requests.get(libitemurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
            try:
                filename = libitemget.json()['value']['name']
            except KeyError:
                filename = 'null'
            if filename:
                data12 = data1+filename+data2
                getusidurl  = PCCHost+updatesession_append
                getusreq = requests.get(getusidurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                getusjson = getusreq.json()
                getusis = getusjson['value']
                for usids in getusis:
                    getstaturl = PCCHost+requestURI_append+usids+'?~action=get'
                    getpst = requests.post(getstaturl, data=data12, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type' : 'application/json'})
                    try:
                        bytestransfer = getpst.json()['value']['bytes_transferred']
                    except KeyError:
                        bytestransfer = 'null'
                    cpdata = keepalivedata1+"25"+keepalivedata2
                    keepaliveurl = PCCHost+completesession_append+usids+'?~action=keep-alive'
                    keepalivepst = requests.post(keepaliveurl, data=cpdata, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json',  'Content-Type' : 'application/json'})
    keepalive(PCCHost,session_ID,odxvchsauth,orgurl)


                                  ##### vCenter check vCloud Director-migration catalog existance else create one ###


def PCCcreatecatalog(PCCHost, session_ID):
    getcaturl = PCCHost+libfind_append
    json = '{  "spec": {    "type": "LOCAL",    "name": "VCA-Migration"  }}'
    getcatreq = requests.post(getcaturl,verify = True, data=json,  headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})  ### Query the Existence of VCA-Migration
    getcatjson = getcatreq.json()
    try:
        catalogid = getcatjson['value'][0]
    except IndexError:
        catalogid = 'null'
    if catalogid is 'null':
        listdsget = requests.get(PCCHost + listdatastore_append,  verify = True, headers = {'vmware-api-session-id': session_ID})
        res = listdsget.json()
        #print(res)
        res2 = res.keys()
        for res3 in res2:
            if res3 == 'value':
                res4 = res[res3]
                n = 0
                for res5 in res4:
                    res6 = res[res3][n]
                    #print(res6)
                    print("DSNAME:", res6['name'],"DSType:", res6['type'], "DSfreeSpace:", int((((res6['free_space'])/1024)/1024)/1024), "GB", "DSCapacity:", int((((res6['capacity'])/1024)/1024)/1024), "GB")
                    n += 1
        DS = input("Please select a Datastore Name to create a catalog from the list:")
        for res3 in res2:
            if res3 == 'value':
                res4 = res[res3]
                r = 0
                for res5 in res4:
                    res6 = res[res3][r]
                    #print(res6)
                    DSNAME = res6['name']
                    DSID =  res6['datastore']
                    r +=1
                    if DSNAME in DS == DSNAME:
                        createcatURL = PCCHost + locallib_append
                        jsondat = jsondat1+ client_token+jsondat2+DSID+jsondat3+CatalogName+jsondat4+description+jsondat5
                        createcatpst = requests.post(createcatURL, data=jsondat, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        LibIDjson = createcatpst.json()
                        catalogid = LibIDjson['value']
    return catalogid


                                    ##### Media Transfer VCA side #####

def Media_OD(API_URL, odxvchsauth):
    vDCURL = API_URL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    print(" ")
    print("List of Active vDCs:")
    print("====================")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "Media/ISO:", child.attrib['numberOfMedia'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB') #, "Status:", child.attrib['status'], "vAPPS:",child.attrib['numberOfVApps'], "vAPPTemplates:", child.attrib['numberOfVAppTemplates']
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            mediaquerypostURL = API_URL + Media_queryall
            mediaquryallget = requests.get(mediaquerypostURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            mediaquryallxml = mediaquryallget.content
            mediaqurycontxml = ET.fromstring(mediaquryallxml)
            mediaquryallkeys = mediaqurycontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}MediaRecord")
            print(" ")
            print("List of Media / ISO:")
            print("====================")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.media+xml' in child2.attrib['type']:
                    print(" ",child2.attrib['name'])
            global ObjNam
            ObjNam = input("Enter the Source Media Name:")
            print(" ")
            print("List of catalogs having",ObjNam,':')
            print("====================================")
            for child7 in mediaquryallkeys:
                Medianame = child7.attrib['name']
                if ObjNam in Medianame == ObjNam:
                    print(" ",child7.attrib['catalogName'])
    CatName = input("Select the Catalog Name:")
    for child8 in mediaquryallkeys:
        Medianame = child8.attrib['catalogName']
        if CatName in Medianame == CatName:
            mediaget = requests.get(child8.attrib['catalogItem'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            mediagetxml = mediaget.content
            mediagetcontxml = ET.fromstring(mediagetxml)
            mediakeyresor = mediagetcontxml.findall("{http://www.vmware.com/vcloud/v1.5}Entity")
            for child10 in mediakeyresor:
                if 'application/vnd.vmware.vcloud.media+xml' in child10.attrib['type'] and ObjNam == child10.attrib['name']:
                    download_iso_URL = child10.attrib['href']
                    download_iso_get = requests.get(download_iso_URL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
                    download_iso_raw = ET.fromstring(download_iso_get.content)
                    sourcexml = download_iso_raw.find(".")
                    sourceiso_size = sourcexml.attrib['size']
                    return sourceiso_size, download_iso_URL, ObjNam



                            #### Enable download for the catalog Item ISO and transfer the file to vCenter ######

def endownloadiso(odxvchsauth,session_ID,download_iso_URL,ObjNam,catalogid,PCCHost,source_size):
    isoEnabledownldURL = download_iso_URL + enabledownload_append
    enabledownload_iso_post = requests.post(isoEnabledownldURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    print(timenow(),":","Enabling Download for the Media",ObjNam)
    getenable = requests.get(download_iso_URL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    enbleprog = getenable.content
    enbleprogxml = ET.fromstring(enbleprog)
    enbleprogkeys = enbleprogxml.findall(".//{http://www.vmware.com/vcloud/v1.5}Tasks/{http://www.vmware.com/vcloud/v1.5}Task")
    for child10 in enbleprogkeys:
        runtask = child10.attrib['href']
        gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
        getcont = gettask.content
        getcontxml = ET.fromstring(getcont)
        getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
        progress = int(getcontkeys.text)
        while progress < 100:
            time.sleep(30)
            gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            getcont = gettask.content
            getcontxml = ET.fromstring(getcont)
            getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
            progress = int(getcontkeys.text)
            print(timenow(),":","Enable download vCD task progress is",progress,'%')
    lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat4+ObjNam+lijsondat5   #lijsondat = lijsondat1+client_token+lijsondat2+str(catalogid)+lijsondat3+description+lijsondat4+str(sourceiso_size)+lijsondat6+ObjNam+lijsondat7
    licreatepsturl = PCCHost + libitem_append
    licreatepstpost = requests.post(licreatepsturl, data=lijsondat,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    licreatejson = licreatepstpost.json()
    LiID = licreatejson['value']
    usjsondat = usjsondat1+client_token+usjsondat2+str(LiID)+usjsondat3
    usurl = PCCHost + updatesession_append
    updatesessionpst = requests.post(usurl, data=usjsondat, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    usjson = updatesessionpst.json()
    usid = usjson['value']
    rujsondat = rujsondat1+ObjNam+rujsondat3+str(source_size)+rujsondat4
    ruurl = PCCHost + requestURI_append + str(usid) + "?~action=add"
    rupst = requests.post(ruurl, data=rujsondat, verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    requrljson = rupst.json()
    requrl = requrljson['value']['upload_endpoint']['uri']
    download_iso_get = requests.get(download_iso_URL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    download_iso_raw = ET.fromstring(download_iso_get.content)
    download_iso_XML = download_iso_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Files/{http://www.vmware.com/vcloud/v1.5}File/")
    #print(download_iso_XML)
    for child9 in download_iso_XML:
        if 'download:default' in child9.attrib['rel']:
            mediadownload = child9.attrib['href']
            #mediaurl = mediadownload[:mediadownload.find('file')]
            print(timenow(),":","Media / ISO file transfer in progress")
            downloaddata = requests.get(mediadownload, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'application/octet-stream'}, stream=True)
            uploadiso = requests.put(requrl, data=downloaddata.iter_content(chunk_size=10240), verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
            getstaturl = PCCHost+completesession_append+str(usid)
            getstatus = requests.get (getstaturl, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
            print(timenow(),":","Validating the uploaded files")
            time.sleep(7)
            validateurl = PCCHost+requestURI_append+usid+"?~action=validate"
            validatepst = requests.post(validateurl, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
            time.sleep(7)
            completeurl = PCCHost+completesession_append+usid+"?~action=complete"
            completepst = requests.post(completeurl, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
            time.sleep(7)
            print(timenow(),":","File transfer is complete, Please verify whether the task in vCenter is completed ")



                                    ##### vAPP migrate cold migration On-demand vCA - Side - Depreciated #######

def vappmigrate_OD(API_URL, odxvchsauth):
    vDCURL = API_URL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    print(" ")
    print("List of Active vDCs:")
    print("====================")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "vAPPS:",child.attrib['numberOfVApps'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB') #"Status:", child.attrib['status'],, "vAPPTemplates:", child.attrib['numberOfVAppTemplates'], "Media/ISO:", child.attrib['numberOfMedia']
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            print(" ")
            print("List of vAPPs:")
            print("==============")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.vApp+xml' in child2.attrib['type']:
                    print(" ",child2.attrib['name'])
            ObjName = input("Enter the vAPP Name:")
            for child3 in Resourceslistkeys:
                if ObjName in child3.attrib['name'] == ObjName:
                    if child3.attrib['type'] == 'application/vnd.vmware.vcloud.vApp+xml':
                        vappallURL = API_URL + vAPP_queryall
                        vappallget= requests.get(vappallURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
                        vAPPqueryxml = vappallget.content
                        vappquerykeysxml = ET.fromstring(vAPPqueryxml)
                        vappquerykeys = vappquerykeysxml.findall(".//{http://www.vmware.com/vcloud/v1.5}VAppRecord")
                        for child4 in vappquerykeys:
                            if ObjName in child4.attrib['name'] == ObjName:
                                if int(child4.attrib['numberOfVMs']) > 0:
                                    if child4.attrib['status'] == 'POWERED_OFF':
                                        vappsizeGB = ((int(child4.attrib['storageKB'])/1024)/1024)
                                        postURL = child4.attrib['href']
                                        vappname = child4.attrib['name']
                                        return postURL,vappname
                                    elif child4.attrib['status'] == 'POWERED_ON':
                                        print(timenow(),":","vAPP is in running state")
                                elif int(child4.attrib['numberOfVMs']) == 0:
                                    print(timenow(),":","There are no VMs in this vAPP")

                                    #### Enable Download for vAPP and Migrate it to vCenter ####

def enabledownloadvapp(postURL,PCCHost,odxvchsauth,vappname,session_ID,catalogid):
    enabledownload_TempURL = postURL + enabledownload_append
    print(timenow(),":","Enabling download for the vAPP"+' '+vappname)
    enabledownload_Temppost = requests.post(enabledownload_TempURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    getenable = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    enbleprog = getenable.content
    enbleprogxml = ET.fromstring(enbleprog)
    enbleprogkeys = enbleprogxml.findall(".//{http://www.vmware.com/vcloud/v1.5}Tasks/{http://www.vmware.com/vcloud/v1.5}Task")
    for child10 in enbleprogkeys:
        runtask = child10.attrib['href']
        gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
        getcont = gettask.content
        getcontxml = ET.fromstring(getcont)
        getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
        progress = int(getcontkeys.text)
        while progress < 100:
            time.sleep(180)
            gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            getcont = gettask.content
            getcontxml = ET.fromstring(getcont)
            getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
            progress = int(getcontkeys.text)
            print(timenow(),":","Enable download vCD task progress is",progress,'%')
    lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat6+vappname+lijsondat5
    licreatepsturl = PCCHost + libitem_append
    licreatepstpost = requests.post(licreatepsturl, data=lijsondat, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    licreatejson = licreatepstpost.json()
    LiID = str(licreatejson['value'])
    usjsondat = usjsondat1+client_token+usjsondat2+LiID+usjsondat3
    usurl = PCCHost + updatesession_append
    updatesessionpst = requests.post(usurl, data=usjsondat, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    usjson = updatesessionpst.json()
    usid = str(usjson['value'])
    download_temp_get = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    download_temp_raw = ET.fromstring(download_temp_get.content)
    download_temp_XML = download_temp_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Link")
    for child in download_temp_XML:
        if 'download:default' in child.attrib['rel']:
            ovfdesc_download = child.attrib['href']
            referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
            downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
            ovfdesc = downloaddesc.content
            dessize = sys.getsizeof(ovfdesc)
            Filenames = ET.fromstring(ovfdesc)
            files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
            rujsondat = rujsondat1+"descriptor.ovf"+rujsondat3+str(dessize)+rujsondat4
            ruurl = PCCHost + requestURI_append + usid + "?~action=add"
            rupst = requests.post(ruurl, data=rujsondat,verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
            requrljson = rupst.json()
            #print(requrljson)
            requrl = requrljson['value']['upload_endpoint']['uri']
            transferovf = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
            uploaddes = requests.put(requrl, data=transferovf.iter_content(chunk_size=10240),verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
            print(timenow(),":","Descriptor file has been transferred to PCC proceeding to migrate VMDK files")
            for filechild in files_XML:
                if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                    filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                    filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                    reffile = referfile_Base+filesubname
                    rujsondat = rujsondat1+filesubname+rujsondat3+str(filesubsize)+rujsondat4
                    ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                    rupst = requests.post(ruurl, data=rujsondat,verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                    requrljson = rupst.json()
                    requrl = requrljson['value']['upload_endpoint']['uri']
                    downloaddata = requests.get(reffile, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'application/octet-stream'}, stream=True)
                    uploadref = requests.put(requrl, data=downloaddata.iter_content(chunk_size=10240), verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
    getstaturl = PCCHost+completesession_append+usid
    getstatus = requests.get (getstaturl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    print(timenow(),":","Validating the uploaded files")
    time.sleep(7)
    validateurl = PCCHost+requestURI_append+usid+"?~action=validate"
    validatepst = requests.post(validateurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    time.sleep(7)
    completeurl = PCCHost+completesession_append+usid+"?~action=complete"
    completepst = requests.post(completeurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    time.sleep(7)
    disable_downloadURL = postURL + disabledownload_append
    disable_downloadpost = requests.post(disable_downloadURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    print(timenow(),":","File transfer is complete, Please verify whether the task in PCC is completed")
    time.sleep(5)


                                    ###### vAPP Template Migration On-Demand from vCA side  - Depreciated ######

def vapptempmigrate_OD(API_URL,odxvchsauth):
    vDCURL = API_URL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    print(" ")
    print("List of Active vDCs:")
    print("====================")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "vAPPTemplates:", child.attrib['numberOfVAppTemplates'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB') #, "Status:", child.attrib['status'], "vAPPS:",child.attrib['numberOfVApps'], "Media/ISO:", child.attrib['numberOfMedia']
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            vapptempquerypostURL = API_URL + vAPPTemplate_queryall
            vapptempquryallget = requests.get(vapptempquerypostURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            vapptempquryallxml = vapptempquryallget.content
            vapptempqurycontxml = ET.fromstring(vapptempquryallxml)
            vapptempquryallkeys = vapptempqurycontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}VAppTemplateRecord")
            print(" ")
            print("List of vAPP Templates:")
            print("=======================")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.vAppTemplate+xml' in child2.attrib['type']:
                    print(" ",child2.attrib['name'])
            ObjName = input("Enter the vAPPTemplate Name:")
            print(" ")
            print("List of catalogs having",ObjName,':')
            print("====================================")
            for child7 in vapptempquryallkeys:
                vapptempname = child7.attrib['name']
                if ObjName in vapptempname == ObjName:
                    print(" ",child7.attrib['catalogName'])
    CatName = input("Select the Catalog Name from the list:")
    for child8 in vapptempquryallkeys:
        catalogname = child8.attrib['catalogName']
        vappname = child8.attrib['name']
        postURL = child8.attrib['href']
        #vappsizeGB = ((int(child8.attrib['storageKB'])/1024)/1024)
        if CatName in catalogname == CatName and ObjName in vappname == ObjName:
            #print(postURL,vappname,catalogname,CatName,ObjName)
            return postURL,vappname,catalogname,CatName,ObjName

                                    ### Enable download for the template and Migrate to vCenter ###

def enabledownloadvapptemp(postURL, PCCHost, vappname, odxvchsauth, session_ID, catalogid):
    enabledownload_TempURL = postURL + enabledownload_append
    #print(enabledownload_TempURL)
    print(timenow(),":","Enabling download for the vAPPTemplate"+' '+vappname)
    enabledownload_Temppost = requests.post(enabledownload_TempURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    getenable = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    enbleprog = getenable.content
    enbleprogxml = ET.fromstring(enbleprog)
    enbleprogkeys = enbleprogxml.findall(".//{http://www.vmware.com/vcloud/v1.5}Tasks/{http://www.vmware.com/vcloud/v1.5}Task")
    for child10 in enbleprogkeys:
        runtask = child10.attrib['href']
        gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
        getcont = gettask.content
        getcontxml = ET.fromstring(getcont)
        getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
        progress = int(getcontkeys.text)
        while progress < 100:
            time.sleep(120)
            gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            getcont = gettask.content
            getcontxml = ET.fromstring(getcont)
            getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
            progress = int(getcontkeys.text)
            print(timenow(),":","Enable download vCD task progress is",progress,'%')
    lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat6+vappname+lijsondat5
    licreatepsturl = PCCHost + libitem_append
    licreatepstpost = requests.post(licreatepsturl, data=lijsondat, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    licreatejson = licreatepstpost.json()
    LiID = str(licreatejson['value'])
    usjsondat = usjsondat1+client_token+usjsondat2+LiID+usjsondat3
    usurl = PCCHost + updatesession_append
    updatesessionpst = requests.post(usurl, data=usjsondat, verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    usjson = updatesessionpst.json()
    usid = str(usjson['value'])
    download_temp_get = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    download_temp_raw = ET.fromstring(download_temp_get.content)
    download_temp_XML = download_temp_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Link")
    for child in download_temp_XML:
        if 'download:default' in child.attrib['rel']:
            ovfdesc_download = child.attrib['href']
            referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
            downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
            ovfdesc = downloaddesc.content
            dessize = sys.getsizeof(ovfdesc)
            Filenames = ET.fromstring(ovfdesc)
            files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
            rujsondat = rujsondat1+"descriptor.ovf"+rujsondat3+str(dessize)+rujsondat4
            ruurl = PCCHost + requestURI_append + usid + "?~action=add"
            rupst = requests.post(ruurl, data=rujsondat,verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
            requrljson = rupst.json()
            #print(requrljson)
            requrl = requrljson['value']['upload_endpoint']['uri']
            transferovf = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
            uploaddes = requests.put(requrl, data=transferovf.iter_content(chunk_size=10240),verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
            print(timenow(),":","Descriptor file has been transferred to vCenter proceeding to migrate VMDK files")
            for filechild in files_XML:
                if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                    filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                    filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                    reffile = referfile_Base+filesubname
                    rujsondat = rujsondat1+filesubname+rujsondat3+str(filesubsize)+rujsondat4
                    ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                    rupst = requests.post(ruurl, data=rujsondat,verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                    requrljson = rupst.json()
                    requrl = requrljson['value']['upload_endpoint']['uri']
                    keepaliveurl = PCCHost + keepalivesession_append  + usid + '?~action=keep-alive'
                    downloaddata = requests.get(reffile, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'application/octet-stream'}, stream=True)
                    keepalivepst = requests.post(keepaliveurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                    uploadref = requests.put(requrl, data=downloaddata.iter_content(chunk_size=10240), verify=True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
    getstaturl = PCCHost+completesession_append+usid
    getstatus = requests.get (getstaturl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    print(timenow(),":","Validating the uploaded files")
    time.sleep(7)
    validateurl = PCCHost+requestURI_append+usid+"?~action=validate"
    validatepst = requests.post(validateurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    time.sleep(7)
    completeurl = PCCHost+completesession_append+usid+"?~action=complete"
    completepst = requests.post(completeurl,verify = True, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
    time.sleep(7)
    disable_downloadURL = postURL + disabledownload_append
    disable_downloadpost = requests.post(disable_downloadURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    print(timenow(),":","File transfer is complete, Please verify whether the task in vCenter is completed")
    time.sleep(5)




'''''''''''


 ##### Subscription or Dedicated Media Transfer (VCA Side) ######


def Media_Sub(SubRawURL,subxvchsauth):
    vDCURL = SubRawURL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "Status:", child.attrib['status'], "vAPPS:",child.attrib['numberOfVApps'], "vAPPTemplates:", child.attrib['numberOfVAppTemplates'], "Media/ISO:", child.attrib['numberOfMedia'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB')
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            mediaquerypostURL = SubRawURL + Media_queryall
            mediaquryallget = requests.get(mediaquerypostURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            mediaquryallxml = mediaquryallget.content
            mediaqurycontxml = ET.fromstring(mediaquryallxml)
            mediaquryallkeys = mediaqurycontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}MediaRecord")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.media+xml' in child2.attrib['type']:
                    print("Media/ISO Name:", child2.attrib['name'])
            global ObjNam
            ObjNam = input("Enter the Source Media Name:")
            for child7 in mediaquryallkeys:
                Medianame = child7.attrib['name']
                if ObjNam in Medianame == ObjNam:
                    print("Catalog Name:", child7.attrib['catalogName'])
    CatName = input("Select the Catalog Name:")
    for child8 in mediaquryallkeys:
        Medianame = child8.attrib['catalogName']
        if CatName in Medianame == CatName:
            mediaget = requests.get(child8.attrib['catalogItem'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            mediagetxml = mediaget.content
            #print(mediagetxml)
            mediagetcontxml = ET.fromstring(mediagetxml)
            mediakeyresor = mediagetcontxml.findall("{http://www.vmware.com/vcloud/v1.5}Entity")
            #print(mediakeyresor)
            for child10 in mediakeyresor:
                if 'application/vnd.vmware.vcloud.media+xml' in child10.attrib['type'] and ObjNam == child10.attrib['name']:
                    download_iso_URL = child10.attrib['href']
                    download_iso_get = requests.get(download_iso_URL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                    download_iso_raw = ET.fromstring(download_iso_get.content)
                    sourcexml = download_iso_raw.find(".")
                    sourceiso_size = sourcexml.attrib['size']
                    return sourceiso_size, download_iso_URL, ObjNam
                    
                      ##### On-demand Media Transfer (vCA Side) ####
                    
def Media_OD():
    vDCURL = API_URL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "Status:", child.attrib['status'], "vAPPS:",child.attrib['numberOfVApps'], "vAPPTemplates:", child.attrib['numberOfVAppTemplates'], "Media/ISO:", child.attrib['numberOfMedia'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB')
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            mediaquerypostURL = API_URL + Media_queryall
            mediaquryallget = requests.get(mediaquerypostURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            mediaquryallxml = mediaquryallget.content
            mediaqurycontxml = ET.fromstring(mediaquryallxml)
            mediaquryallkeys = mediaqurycontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}MediaRecord")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.media+xml' in child2.attrib['type']:
                    print("Media/ISO Name:", child2.attrib['name'])
            ObjName = input("Enter the Name of the Source Media Name:")
            for child7 in mediaquryallkeys:
                Medianame = child7.attrib['name']
                if ObjName in Medianame == ObjName:
                    print("Catalog Name:", child7.attrib['catalogName'])
    CatName = input("Select the Catalog Name from the list:")
    for child8 in mediaquryallkeys:
        Medianame = child8.attrib['catalogName']
        if CatName in Medianame == CatName:
            mediaget = requests.get(child8.attrib['catalogItem'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
            mediagetxml = mediaget.content
            #print(mediagetxml)
            mediagetcontxml = ET.fromstring(mediagetxml)
            mediakeyresor = mediagetcontxml.findall("{http://www.vmware.com/vcloud/v1.5}Entity")
            #print(mediakeyresor)
            for child10 in mediakeyresor:
                if 'application/vnd.vmware.vcloud.media+xml' in child10.attrib['type'] and ObjName == child10.attrib['name']:
                    download_iso_URL = child10.attrib['href']
                    isoEnabledownldURL = download_iso_URL + enabledownload_append
                    enabledownload_iso_post = requests.post(isoEnabledownldURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
                    print("Enabling Download for",ObjName)
                    time.sleep(90)
                    download_iso_get = requests.get(download_iso_URL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
                    download_iso_raw = ET.fromstring(download_iso_get.content)
                    sourcexml = download_iso_raw.find(".")
                    global sourceiso_size
                    sourceiso_size = sourcexml.attrib['size']
                    download_iso_XML = download_iso_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Files/{http://www.vmware.com/vcloud/v1.5}File/")
                    #print(download_iso_XML)
                    for child9 in download_iso_XML:
                        if 'download:default' in child9.attrib['rel']:
                            mediadownload = child9.attrib['href']
                            print(mediadownload)
                            #mediaurl = mediadownload[:mediadownload.find('file')]
                            #print(mediaurl)
                            PCC(mediadownload, sourceiso_size, ObjName)
                            
                            
 ###### vAPP migration from Subscription / Dedicated - vCA Side #####

def vappmigrate_sub():
    vDCURL = SubRawURL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "Status:", child.attrib['status'], "vAPPS:",child.attrib['numberOfVApps'], "vAPPTemplates:", child.attrib['numberOfVAppTemplates'], "Media/ISO:", child.attrib['numberOfMedia'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB')
        elif 'false' in child.attrib['isEnabled']:
            print("No Active vDCs in the environment")
            time.sleep(6)
            sys.exit(1)
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.vApp+xml' in child2.attrib['type']:
                    print("vAPP Name:", child2.attrib['name'])
            ObjName = input("Enter the Name of the vAPP:")
            for child3 in Resourceslistkeys:
                if ObjName in child3.attrib['name'] == ObjName:
                    if child3.attrib['type'] == 'application/vnd.vmware.vcloud.vApp+xml':
                        vappallURL = SubRawURL + vAPP_queryall
                        vappallget= requests.get(vappallURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                        vAPPqueryxml = vappallget.content
                        vappquerykeysxml = ET.fromstring(vAPPqueryxml)
                        vappquerykeys = vappquerykeysxml.findall(".//{http://www.vmware.com/vcloud/v1.5}VAppRecord")
                        for child4 in vappquerykeys:
                            if ObjName in child4.attrib['name'] == ObjName:
                                if int(child4.attrib['numberOfVMs']) > 0:
                                    if child4.attrib['status'] == 'POWERED_OFF':
                                        vappsizeGB = ((int(child4.attrib['storageKB'])/1024)/1024)
                                        postURL = child4.attrib['href']
                                        vappname = child4.attrib['name']
                                        enabledownload_TempURL = postURL + enabledownload_append
                                        print(enabledownload_TempURL)
                                        print("Enabling download for the vAPP"+' '+vappname)
                                        enabledownload_Temppost = requests.post(enabledownload_TempURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                                        getenable = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                                        enbleprog = getenable.content
                                        enbleprogxml = ET.fromstring(enbleprog)
                                        enbleprogkeys = enbleprogxml.findall(".//{http://www.vmware.com/vcloud/v1.5}Tasks/{http://www.vmware.com/vcloud/v1.5}Task")
                                        for child10 in enbleprogkeys:
                                            runtask = child10.attrib['href']
                                            gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                                            getcont = gettask.content
                                            getcontxml = ET.fromstring(getcont)
                                            getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
                                            progress = int(getcontkeys.text)
                                            while progress < 100:
                                                time.sleep(300)
                                                gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                                                getcont = gettask.content
                                                getcontxml = ET.fromstring(getcont)
                                                getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
                                                progress = int(getcontkeys.text)
                                                print("Enable download vCD task progress is",progress,'%')
                                        download_temp_get = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                                        download_temp_raw = ET.fromstring(download_temp_get.content)
                                        download_temp_XML = download_temp_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Link")
                                        for child in download_temp_XML:
                                            if 'download:default' in child.attrib['rel']:
                                                ovfdesc_download = child.attrib['href']
                                                print(ovfdesc_download)
                                                referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
                                                downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                                                ovfdesc = downloaddesc.content
                                                Filenames = ET.fromstring(ovfdesc)
                                                files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
                                                for filechild in files_XML:
                                                    if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                                                        filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                                                        filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                                                        print(filesubname, filesubsize)
                                                PCCsub_vapp(ObjName,download_temp_XML, postURL)
                                    elif child4.attrib['status'] == 'POWERED_ON':
                                        print("vAPP is in running state")
                                elif int(child4.attrib['numberOfVMs']) == 0:
                                    print("There are no VMs in this vAPP")       
                                    
                                    
                                     ###### vAPP Template migration MT / Dedicated from vCA side ######


def vapptempmigrate_sub():
    vDCURL = SubRawURL + orgvdc_query
    vDCURLget = requests.get(vDCURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
    vDCURLXML = vDCURLget.content
    vDCquerycont = ET.fromstring(vDCURLXML)
    vDCquerykeys = vDCquerycont.findall(".//{http://www.vmware.com/vcloud/v1.5}OrgVdcRecord")
    for child in vDCquerykeys:
        if 'true' in child.attrib['isEnabled']:
            print("vDCName:", child.attrib['name'], "Status:", child.attrib['status'], "vAPPS:",child.attrib['numberOfVApps'], "vAPPTemplates:", child.attrib['numberOfVAppTemplates'], "Media/ISO:", child.attrib['numberOfMedia'], "StorageUsed in GB:", (int(child.attrib['storageUsedMB'])/1024), 'GB')
    vDCName = input('Enter the vDCName:')
    for child1 in vDCquerykeys:
        if vDCName in child1.attrib['name'] == vDCName:
            vDCadminURL = requests.get(child1.attrib['href'], headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            vDCadminxml = vDCadminURL.content
            vDCadmincontxml = ET.fromstring(vDCadminxml)
            Resourceslistkeys = vDCadmincontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}ResourceEntity")
            vapptempquerypostURL = SubRawURL + vAPPTemplate_queryall
            vapptempquryallget = requests.get(vapptempquerypostURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            vapptempquryallxml = vapptempquryallget.content
            vapptempqurycontxml = ET.fromstring(vapptempquryallxml)
            vapptempquryallkeys = vapptempqurycontxml.findall(".//{http://www.vmware.com/vcloud/v1.5}VAppTemplateRecord")
            for child2 in Resourceslistkeys:
                if 'application/vnd.vmware.vcloud.vAppTemplate+xml' in child2.attrib['type']:
                    print("vAPPTemplate:", child2.attrib['name'])
            ObjName = input("Enter the Name of the vAPPTemplate:")
            for child7 in vapptempquryallkeys:
                vapptempname = child7.attrib['name']
                if ObjName in vapptempname == ObjName:
                    print("Catalog Name:", child7.attrib['catalogName'])
    CatName = input("Select the Catalog Name from the list:")
    for child8 in vapptempquryallkeys:
        catalogname = child8.attrib['catalogName']
        vappname = child8.attrib['name']
        postURL = child8.attrib['href']
        vappsizeGB = ((int(child8.attrib['storageKB'])/1024)/1024)
        if CatName in catalogname == CatName and ObjName in vappname == ObjName:
            enabledownload_TempURL = postURL + enabledownload_append
            #print(enabledownload_TempURL)
            print("Enabling download for the vAPPTemplate"+' '+vappname)
            enabledownload_Temppost = requests.post(enabledownload_TempURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            getenable = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            enbleprog = getenable.content
            enbleprogxml = ET.fromstring(enbleprog)
            enbleprogkeys = enbleprogxml.findall(".//{http://www.vmware.com/vcloud/v1.5}Tasks/{http://www.vmware.com/vcloud/v1.5}Task")
            for child10 in enbleprogkeys:
                runtask = child10.attrib['href']
                gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                getcont = gettask.content
                getcontxml = ET.fromstring(getcont)
                getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
                progress = int(getcontkeys.text)
                while progress < 100:
                    time.sleep(300)
                    gettask = requests.get(runtask, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                    getcont = gettask.content
                    getcontxml = ET.fromstring(getcont)
                    getcontkeys = getcontxml.find(".//{http://www.vmware.com/vcloud/v1.5}Progress")
                    progress = int(getcontkeys.text)
                    print("Enable download vCD task progress is",progress,'%')
            download_temp_get = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
            download_temp_raw = ET.fromstring(download_temp_get.content)
            download_temp_XML = download_temp_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Link")
            for child in download_temp_XML:
                if 'download:default' in child.attrib['rel']:
                    ovfdesc_download = child.attrib['href']
                    print(ovfdesc_download)
                    referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
                    downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                    ovfdesc = downloaddesc.content
                    Filenames = ET.fromstring(ovfdesc)
                    files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
                    for filechild in files_XML:
                        if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                            filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                            filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                            print(filesubname, filesubsize)
                    PCCsub_vapp(ObjName, download_temp_XML, postURL)        
                    
                    
                    
                                        ####### vAPP / vAPP Template Migration from Subcription / Dedicated - PCC side #######

def PCCsub_vapp(ObjName, download_temp_XML, postURL):
    Sessionrequest = requests.post(PCCHost + session_append, verify = False,auth=HTTPBasicAuth(PCCUser, PCCpass))   ## login to PCC ##
    session_ID = Sessionrequest.json()['value']
    print(session_ID)
    getcaturl = PCCHost+libfind_append
    json = '{  "spec": {    "type": "LOCAL",    "name": "VCA-Migration"  }}'
    getcatreq = requests.post(getcaturl,verify = False, data=json, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})  ### Query the Existence of VCA-Migration
    getcatjson = getcatreq.json()
    try:
        catalogid = str(getcatjson['value'][0])
    except IndexError:
        catalogid = 'null'
    if catalogid is 'null':
        listdsget = requests.get(PCCHost + listdatastore_append,verify = False, headers = {'vmware-api-session-id': session_ID})
        res = listdsget.json()
        #print(res)
        res2 = res.keys()
        for res3 in res2:
            if res3 == 'value':
                res4 = res[res3]
                n = 0
                for res5 in res4:
                    res6 = res[res3][n]
                    #print(res6)
                    print("DSNAME:", res6['name'],"DSType:", res6['type'], "DSfreeSpace:", int((((res6['free_space'])/1024)/1024)/1024), "GB", "DSCapacity:", int((((res6['capacity'])/1024)/1024)/1024), "GB")
                    n += 1
        DS = input("Please select a Datastore Name to create a catalog from the list:")
        for res3 in res2:
            if res3 == 'value':
                res4 = res[res3]
                r = 0
                for res5 in res4:
                    res6 = res[res3][r]
                    #print(res6)
                    DSNAME = res6['name']
                    DSID =  res6['datastore']
                    r +=1
                    if DSNAME in DS == DSNAME:
                        createcatURL = PCCHost + locallib_append
                        jsondat = jsondat1+ client_token+jsondat2+DSID+jsondat3+CatalogName+jsondat4+description+jsondat5
                        createcatpst = requests.post(createcatURL, data=jsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        LibIDjson = createcatpst.json()
                        catalogid = str(LibIDjson['value'])
                        lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat6+ObjName+lijsondat5
                        licreatepsturl = PCCHost + libitem_append
                        licreatepstpost = requests.post(licreatepsturl, data=lijsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        licreatejson = licreatepstpost.json()
                        LiID = str(licreatejson['value'])
                        usjsondat = usjsondat1+client_token+usjsondat2+LiID+usjsondat3
                        usurl = PCCHost + updatesession_append
                        updatesessionpst = requests.post(usurl, data=usjsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        usjson = updatesessionpst.json()
                        usid = str(usjson['value'])
                        for child in download_temp_XML:
                            if 'download:default' in child.attrib['rel']:
                                ovfdesc_download = child.attrib['href']
                                referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
                                downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                                ovfdesc = downloaddesc.content
                                dessize = sys.getsizeof(ovfdesc)
                                Filenames = ET.fromstring(ovfdesc)
                                files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
                                rujsondat = rujsondat1+"descriptor.ovf"+rujsondat3+str(dessize)+rujsondat4
                                ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                                rupst = requests.post(ruurl, data=rujsondat,verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                                requrljson = rupst.json()
                                #print(requrljson)
                                requrl = requrljson['value']['upload_endpoint']['uri']
                                transferovf = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                                uploaddes = requests.put(requrl, data=transferovf.iter_content(chunk_size=10240),verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
                                print("transferred descriptor")
                                for filechild in files_XML:
                                    if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                                        filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                                        filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                                        reffile = referfile_Base+filesubname
                                        print(reffile)
                                        rujsondat = rujsondat1+filesubname+rujsondat3+str(filesubsize)+rujsondat4
                                        ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                                        rupst = requests.post(ruurl, data=rujsondat,verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                                        requrljson = rupst.json()
                                        print(requrljson)
                                        requrl = requrljson['value']['upload_endpoint']['uri']
                                        keepaliveurl = PCCHost + keepalivesession_append  + usid + '?~action=keep-alive'
                                        downloaddata = requests.get(reffile, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'application/octet-stream'}, stream=True)
                                        keepalivepst = requests.post(keepaliveurl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                                        uploadref = requests.put(requrl, data=downloaddata.iter_content(chunk_size=10240),verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
                        getstaturl = PCCHost+completesession_append+usid
                        getstatus = requests.get (getstaturl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                        print("Validating the uploaded files")
                        time.sleep(7)
                        validateurl = PCCHost+requestURI_append+usid+"?~action=validate"
                        validatepst = requests.post(validateurl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                        time.sleep(7)
                        completeurl = PCCHost+completesession_append+usid+"?~action=complete"
                        completepst = requests.post(completeurl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                        time.sleep(7)
                        disable_downloadURL = postURL + disabledownload_append
                        disable_downloadpost = requests.post(disable_downloadURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
                        print("Migration is completed")
                        time.sleep(5)

    else:
        lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat6+ObjName+lijsondat5
        licreatepsturl = PCCHost + libitem_append
        licreatepstpost = requests.post(licreatepsturl, data=lijsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
        licreatejson = licreatepstpost.json()
        LiID = str(licreatejson['value'])
        usjsondat = usjsondat1+client_token+usjsondat2+LiID+usjsondat3
        usurl = PCCHost + updatesession_append
        updatesessionpst = requests.post(usurl, data=usjsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
        usjson = updatesessionpst.json()
        usid = str(usjson['value'])
        for child in download_temp_XML:
            if 'download:default' in child.attrib['rel']:
                ovfdesc_download = child.attrib['href']
                referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
                downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                ovfdesc = downloaddesc.content
                dessize = sys.getsizeof(ovfdesc)
                Filenames = ET.fromstring(ovfdesc)
                files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
                rujsondat = rujsondat1+"descriptor.ovf"+rujsondat3+str(dessize)+rujsondat4
                ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                rupst = requests.post(ruurl, data=rujsondat, verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                requrljson = rupst.json()
                #print(requrljson)
                requrl = requrljson['value']['upload_endpoint']['uri']
                transferovf = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                uploaddes = requests.put(requrl, data=transferovf.iter_content(chunk_size=10240), verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
                print("transferred descriptor")
                for filechild in files_XML:
                    if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                        filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                        filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                        reffile = referfile_Base+filesubname
                        print(reffile)
                        rujsondat = rujsondat1+filesubname+rujsondat3+str(filesubsize)+rujsondat4
                        ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                        rupst = requests.post(ruurl, data=rujsondat, verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        requrljson = rupst.json()
                        print(requrljson)
                        requrl = requrljson['value']['upload_endpoint']['uri']
                        downloaddata = requests.get(reffile, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth, 'Content-Type': 'application/octet-stream'}, stream=True)
                        uploadref = requests.put(requrl, data=downloaddata.iter_content(chunk_size=10240), verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
        getstaturl = PCCHost+completesession_append+usid
        getstatus = requests.get (getstaturl, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
        print("Validating the uploaded files")
        time.sleep(7)
        validateurl = PCCHost+requestURI_append+usid+"?~action=validate"
        validatepst = requests.post(validateurl, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
        time.sleep(7)
        completeurl = PCCHost+completesession_append+usid+"?~action=complete"
        completepst = requests.post(completeurl, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
        time.sleep(7)
        disable_downloadURL = postURL + disabledownload_append
        disable_downloadpost = requests.post(disable_downloadURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': subxvchsauth})
        print("Migration is completed")
        time.sleep(5)
                                 
                                                                 ##### vAPP / vAPP Template cold migration On-Demand PCC side ######


def PCC_vapp(ObjName, postURL):
    Sessionrequest = requests.post(PCCHost + session_append, verify = False,auth=HTTPBasicAuth(PCCUser, PCCpass))   ## login to PCC ##
    session_ID = Sessionrequest.json()['value']
    print(session_ID)
    getcaturl = PCCHost+libfind_append
    json = '{  "spec": {    "type": "LOCAL",    "name": "VCA-Migration"  }}'
    getcatreq = requests.post(getcaturl, verify = False, data=json, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})  ### Query the Existence of VCA-Migration
    getcatjson = getcatreq.json()
    try:
        catalogid = str(getcatjson['value'][0])
    except IndexError:
        catalogid = 'null'
    if catalogid is 'null':
        listdsget = requests.get(PCCHost + listdatastore_append, verify = False, headers = {'vmware-api-session-id': session_ID})
        res = listdsget.json()
        #print(res)
        res2 = res.keys()
        for res3 in res2:
            if res3 == 'value':
                res4 = res[res3]
                n = 0
                for res5 in res4:
                    res6 = res[res3][n]
                    #print(res6)
                    print("DSNAME:", res6['name'],"DSType:", res6['type'], "DSfreeSpace:", int((((res6['free_space'])/1024)/1024)/1024), "GB", "DSCapacity:", int((((res6['capacity'])/1024)/1024)/1024), "GB")
                    n += 1
        DS = input("Please select a Datastore Name to create a catalog from the list:")
        for res3 in res2:
            if res3 == 'value':
                res4 = res[res3]
                r = 0
                for res5 in res4:
                    res6 = res[res3][r]
                    #print(res6)
                    DSNAME = res6['name']
                    DSID =  res6['datastore']
                    r +=1
                    if DSNAME in DS == DSNAME:
                        createcatURL = PCCHost + locallib_append
                        jsondat = jsondat1+ client_token+jsondat2+DSID+jsondat3+CatalogName+jsondat4+description+jsondat5
                        createcatpst = requests.post(createcatURL, data=jsondat, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        LibIDjson = createcatpst.json()
                        catalogid = str(LibIDjson['value'])
                        lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat6+ObjName+lijsondat5
                        licreatepsturl = PCCHost + libitem_append
                        licreatepstpost = requests.post(licreatepsturl, data=lijsondat, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        licreatejson = licreatepstpost.json()
                        LiID = str(licreatejson['value'])
                        usjsondat = usjsondat1+client_token+usjsondat2+LiID+usjsondat3
                        usurl = PCCHost + updatesession_append
                        updatesessionpst = requests.post(usurl, data=usjsondat, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                        usjson = updatesessionpst.json()
                        usid = str(usjson['value'])
                        download_temp_get = requests.get(postURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
                        download_temp_raw = ET.fromstring(download_temp_get.content)
                        download_temp_XML = download_temp_raw.findall(".//{http://www.vmware.com/vcloud/v1.5}Link")
                        for child in download_temp_XML:
                            if 'download:default' in child.attrib['rel']:
                                ovfdesc_download = child.attrib['href']
                                referfile_Base = ovfdesc_download[:ovfdesc_download.find('descriptor.ovf')]
                                downloaddesc = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                                ovfdesc = downloaddesc.content
                                dessize = sys.getsizeof(ovfdesc)
                                Filenames = ET.fromstring(ovfdesc)
                                files_XML = Filenames.findall(".//{http://schemas.dmtf.org/ovf/envelope/1}File")
                                rujsondat = rujsondat1+"descriptor.ovf"+rujsondat3+str(dessize)+rujsondat4
                                ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                                rupst = requests.post(ruurl, data=rujsondat,verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                                requrljson = rupst.json()
                                #print(requrljson)
                                requrl = requrljson['value']['upload_endpoint']['uri']
                                transferovf = requests.get(ovfdesc_download, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'text/xml'}, stream=True)
                                uploaddes = requests.put(requrl, data=transferovf.iter_content(chunk_size=10240),verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
                                print("transferred descriptor")
                                for filechild in files_XML:
                                    if "{http://schemas.dmtf.org/ovf/envelope/1}href" in filechild.attrib:
                                        filesubname = str(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}href"])
                                        filesubsize = int(filechild.attrib["{http://schemas.dmtf.org/ovf/envelope/1}size"])
                                        reffile = referfile_Base+filesubname
                                        print(reffile)
                                        rujsondat = rujsondat1+filesubname+rujsondat3+str(filesubsize)+rujsondat4
                                        ruurl = PCCHost + requestURI_append + usid + "?~action=add"
                                        rupst = requests.post(ruurl, data=rujsondat,verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                                        requrljson = rupst.json()
                                        print(requrljson)
                                        requrl = requrljson['value']['upload_endpoint']['uri']
                                        keepaliveurl = PCCHost + keepalivesession_append  + usid + '?~action=keep-alive'
                                        downloaddata = requests.get(reffile, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth, 'Content-Type': 'application/octet-stream'}, stream=True)
                                        keepalivepst = requests.post(keepaliveurl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
                                        uploadref = requests.put(requrl, data=downloaddata.iter_content(chunk_size=10240), verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/octet-stream'})
                        getstaturl = PCCHost+completesession_append+usid
                        getstatus = requests.get (getstaturl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                        print("Validating the uploaded files")
                        time.sleep(7)
                        validateurl = PCCHost+requestURI_append+usid+"?~action=validate"
                        validatepst = requests.post(validateurl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                        time.sleep(7)
                        completeurl = PCCHost+completesession_append+usid+"?~action=complete"
                        completepst = requests.post(completeurl,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json'})
                        time.sleep(7)
                        disable_downloadURL = postURL + disabledownload_append
                        disable_downloadpost = requests.post(disable_downloadURL, headers = {'Accept': 'application/*+xml;version=5.7', 'x-vcloud-authorization': odxvchsauth})
                        print("Migration is completed")
                        time.sleep(5)

                                 
                              
                            #### PCC create a Library Item for ISO ###


def createLibraryItemISO(PCCHost,catalogid, session_ID):
    lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat4+ObjNam+lijsondat5
    #lijsondat = lijsondat1+client_token+lijsondat2+str(catalogid)+lijsondat3+description+lijsondat4+str(sourceiso_size)+lijsondat6+ObjNam+lijsondat7
    licreatepsturl = PCCHost + libitem_append
    licreatepstpost = requests.post(licreatepsturl, data=lijsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    licreatejson = licreatepstpost.json()
    LiID = licreatejson['value']
    return LiID

                                #### PCC create a Library Item for ovf ###


def createLibraryItemOVF(catalogid, session_ID):
    lijsondat = lijsondat1+client_token+lijsondat2+catalogid+lijsondat3+description+lijsondat6+ObjName+lijsondat5
    #lijsondat = lijsondat1+client_token+lijsondat2+str(catalogid)+lijsondat3+description+lijsondat4+str(sourceiso_size)+lijsondat6+ObjNam+lijsondat7
    licreatepsturl = PCCHost + libitem_append
    licreatepstpost = requests.post(licreatepsturl, data=lijsondat,verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    licreatejson = licreatepstpost.json()
    LiID = licreatejson['value']
    return LiID




                        #### PCC create an update session for the Library Item###

def createUpdateSession(PCCHost, LiID, session_ID):
    usjsondat = usjsondat1+client_token+usjsondat2+str(LiID)+usjsondat3
    usurl = PCCHost + updatesession_append
    updatesessionpst = requests.post(usurl, data=usjsondat, verify = False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    usjson = updatesessionpst.json()
    usid = usjson['value']
    return usid

                        #### PCC request URL for uploading the actual file ###

def requesturl(PCCHost, usid, sourceiso_size, session_ID):
    rujsondat = rujsondat1+ObjNam+rujsondat3+str(sourceiso_size)+rujsondat4
    ruurl = PCCHost + requestURI_append + str(usid) + "?~action=add"
    rupst = requests.post(ruurl, data=rujsondat, verify=False, headers = {'vmware-api-session-id': session_ID, 'Accept': 'application/json', 'Content-Type': 'application/json'})
    requrljson = rupst.json()
    requrl = requrljson['value']['upload_endpoint']['uri']
    return requrl   
                            
'''

