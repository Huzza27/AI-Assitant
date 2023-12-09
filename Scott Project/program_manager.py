import win32com.client

def get_installed_programs():
    objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    objSWbemServices = objWMIService.ConnectServer(".", "root\cimv2")
    colItems = objSWbemServices.ExecQuery("Select * from Win32_Product")
    programs = []
    for objItem in colItems:
        programs.append(objItem.Name)
    return programs

installed_programs = get_installed_programs()
for program in installed_programs:
    print(program)
