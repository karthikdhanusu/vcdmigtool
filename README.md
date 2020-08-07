   <H1> vCD to vCenter VM cold migration tool </H1>
   
   <H2> Description: </H2>
   
   The purpose of this script is to migrate vAPPs, vAPP templates and Media/ISO images from vCloud director to the vCenter server's  Content Library. Once the objects are migrated to the destination content library user shall deploy the VMs from the templates.
    
   
  <H2> Installation :</H2>
   1. Use git clone https://github.com/karthikdhanusu/vcdmigtool.git to download the scripts main.py (user interface) migtool.py (migrate object script).
   2. Use requirements.txt file to install the dependencies
      
  <H2> Supported / Tested platform: </H2>
  
OS: Windows
Language : Python 3.x

<H2> Usage: </H2>

The script contains the code to migrate the workloads from vCloud Air (Legacy cloud platform by VMware - Depreciated) and from the On-Prem vCloud Director to vCenter server.

1. Execute the script main.py

         python main.py
   
Select the environment type:
1.vCloud Air (Legacy-depreciated)
2.On-premise vCloud director
Enter your choice [1-2]:

2. Select 2 for the On-premise vCloud Director.
3. Enter the user credentials for source and destination.
4. Select the Object type vAPP, vAPP template and Media/ ISO files 
5. The script will drive you till the end of migration.

Note: When a migration is initiated a Keep-alive window will open and it should be active till the migration task is complete. Please do NOT close it till the task is completed






      
  
  
      

