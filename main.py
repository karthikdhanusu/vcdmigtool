from migtoolPCC import *
import subprocess,os
import multiprocessing
import getpass


def userinput():


    global VCAUser, VCAPasswd, enttype, API_URL, VCAOrgName, PCCHost, PCCUser, PCCpass, SubRawURL
    pullbanner = banner(text='vCloud Director to vCenter VM Cold Migration Tool')
    endbanner = banner(text='***')
    print("")
    print(pullbanner)
    print("")
    print("Disclaimer:")
    print("===========")
    print("  1. This application is developed to cold migrate vCloud director VMs to vCenter content Library")
    print("  2. Supported vCenters 6.0, 6.5, 6.7")
    print("  3. Input validation is performed after the last step, ensure all the information is entered correctly")
    print("  4. Don't close the Keep-alive/Migration window till all the migrations are complete")
    print("")
    print(endbanner)
    print("")
    print("Select the vCloud Director Environment type:")
    print("1.vCloud Air (Legacy-depreciated)")
    print("2.On-premise vCloud director")
    enttype = int(input('Enter your choice [1-2]:'))
    VCAUser = input('vCloud Director Username:')
    VCAPasswd = getpass.getpass(prompt='vCloud Director Password:')
    API_URL = input('vCloud Director API / GVR login URL:')
    SubRawURL = API_URL[:API_URL.find('.com') + 4]
    VCAOrgName = input('vCloud Director OrgName:')
    PCCHost = input("vCenter Host_Name/IP,format(https://pcc-xxx-xxx-xxx-xxx.ovh.xx):")
    PCCUser = input("vCenter UserName:")
    PCCpass = getpass.getpass(prompt='vCenter Password:')
    login()




def login():
    global odxvchsauth,session_ID
    if enttype == 1:
        loginreq = login_ondemand(API_URL, VCAUser, VCAPasswd, VCAOrgName)
        odxvchsauth = loginreq[0]
        orgurl = loginreq[1]
        session_ID = PCClogin(PCCHost, PCCUser, PCCpass)
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.keepalive('%s','%s','%s','%s')"%(PCCHost,session_ID,odxvchsauth,orgurl)], shell=True)
        transferopt()

    elif enttype == 2:
        loginreq = login_subscription(SubRawURL,VCAUser,VCAPasswd,VCAOrgName)
        odxvchsauth = loginreq[0]
        orgurl = loginreq[1]
        session_ID = PCClogin(PCCHost, PCCUser, PCCpass)
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.keepalive('%s','%s','%s','%s')"%(PCCHost,session_ID,odxvchsauth,orgurl)], shell=True)
        transferopt()


def transferopt():
    global objtype
    print("")
    print("Select the type of object to be transferred:")
    print("1.vAPP (Cold Migration)")
    print("2.vAPP Template")
    print("3.Media / ISO")
    objtype = int(input("Enter your choice [1-3]:"))
    core()


def core():
    if enttype == 1 and objtype == 1:
        catalogid = PCCcreatecatalog(PCCHost,session_ID)
        time.sleep(4)
        source_item = vappmigrate_OD(API_URL, odxvchsauth)
        time.sleep(4)
        postURL = source_item[0]
        vappname = source_item[1]
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.enabledownloadvapp('%s','%s','%s','%s','%s','%s')"%(postURL,PCCHost,odxvchsauth,vappname,session_ID,catalogid)], shell=True)
        time.sleep(4)
        transferopt()

    elif enttype == 1 and objtype == 2:
        catalogid = PCCcreatecatalog(PCCHost,session_ID)
        time.sleep(4)
        source_item = vapptempmigrate_OD(API_URL,odxvchsauth)
        time.sleep(4)
        postURL = source_item[0]
        vappname = source_item[1]
        catalogname = source_item[2]
        CatName = source_item[3]
        ObjName = source_item[4]
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.enabledownloadvapptemp('%s','%s','%s','%s','%s','%s')"%(postURL,PCCHost,vappname,odxvchsauth,session_ID,catalogid)], shell=True)
        time.sleep(4)
        transferopt()

    elif enttype == 1 and objtype == 3:
        catalogid = PCCcreatecatalog(PCCHost,session_ID)
        sourceiso_size = Media_OD(API_URL, odxvchsauth)
        download_iso_URL = sourceiso_size[1]
        ObjNam = sourceiso_size[2]
        source_size = sourceiso_size[0]
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.endownloadiso('%s','%s','%s','%s','%s','%s','%s')"%(odxvchsauth,session_ID,download_iso_URL,ObjNam,catalogid,PCCHost,source_size)], shell=True)
        time.sleep(4)
        transferopt()

    elif enttype == 2 and objtype == 1:
        catalogid = PCCcreatecatalog(PCCHost,session_ID)
        time.sleep(4)
        source_item = vappmigrate_OD(SubRawURL, odxvchsauth)
        time.sleep(4)
        postURL = source_item[0]
        vappname = source_item[1]
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.enabledownloadvapp('%s','%s','%s','%s','%s','%s')"%(postURL,PCCHost,odxvchsauth,vappname,session_ID,catalogid)], shell=True)
        time.sleep(5)
        transferopt()

    elif enttype == 2 and objtype == 2:
        catalogid = PCCcreatecatalog(PCCHost,session_ID)
        time.sleep(4)
        source_item = vapptempmigrate_OD(SubRawURL, odxvchsauth)
        time.sleep(4)
        postURL = source_item[0]
        vappname = source_item[1]
        catalogname = source_item[2]
        CatName = source_item[3]
        ObjName = source_item[4]
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.enabledownloadvapptemp('%s','%s','%s','%s','%s','%s')"%(postURL,PCCHost,vappname,odxvchsauth,session_ID,catalogid)], shell=True)
        time.sleep(4)
        transferopt()

    elif enttype == 2 and objtype == 3:
        catalogid = PCCcreatecatalog(PCCHost,session_ID)
        sourceiso_size = Media_OD(SubRawURL, odxvchsauth)
        download_iso_URL = sourceiso_size[1]
        ObjNam = sourceiso_size[2]
        source_size = sourceiso_size[0]
        subprocess.Popen(["start", "cmd", "/k", "python", "-c", "import migtoolPCC; migtoolPCC.endownloadiso('%s','%s','%s','%s','%s','%s','%s')"%(odxvchsauth,session_ID,download_iso_URL,ObjNam,catalogid,PCCHost,source_size)], shell=True)
        time.sleep(4)
        transferopt()


if __name__ == '__main__':
    userinput()




