import sys
import os
import platform
import subprocess
import re
import time
from ftflib.ftf_script import FtfScript
from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.connector import Connector
from ftflib import efi
from ftflib.toolbox import get_match
from tests.mcs.resource_check_os.get_os_resourse import *



def os_verify(script):

    # Verification of OS installation and location of OS

    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    disk_info=console.run('lsscsi | grep -i disk')
    ata_check=re.findall(r'ATA', disk_info)
    fc_check=re.findall(r'FC', disk_info)
    mscc_check=re.findall(r'MSCC', disk_info)
    disk1 = re.findall(r'(sd[a-z]).*', disk_info)
    blk_info = console.run('lsblk')
    efi = get_match(r'.*efi',  blk_info)
    disk2 = get_match(r'sd[a-z]', efi)
    script.log.info("="*15 +"Verification of OS installation" +"="*15)
    if disk2 in disk1:
        script.log.info("OS installation was verified")
    else:
        script.error("OS installation error")
    if "ATA" in ata_check:
        script.log.info("OS is installed on the hard disk")
    elif "FC" in fc_check:
        script.log.info("OS is installed on FC")

    elif "MSCC" in mscc_check:
        script.log.info("OS is installed on FC")

    else:
        script.log.info("Failure")

def system_log(script):
    
    #Displaying cae logs on RMC
        
    script.log.info("=" * 15 + "cae logs" + "=" * 15)
    cae_log=script.conn.run("show cae")
    script.log.info("The cae logs are:{}".format(cae_log))
    
    #Displaying system logs on OS
    
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    sys_log_cmd= console.run("cat /var/log/messages | grep -i 'error'")
    script.log.info( "="*15 + "System logs" +"="*15)
    if "error" in sys_log_cmd:
        script.log.info("Errors exists. The system log errors are:{}".format(sys_log_cmd))
    else:
        script.log.info("no errors")

    driver_msg = console.run("dmesg | grep -iE 'panic|fail|work|retries|BUG'")
    if "error" in dmesg_log_cmd:
        script.log.info("Errors exists. The dmseg log errors are:{}".format(driver_msg))
    else:
        script.log.info("no errors")
    


def cpu_match(script):
    npar_details= script.conn.run("show npar verbose")
    npar_cpu_cores = str(int(get_match(r'Cores.*\s(\d+)', npar_details)) * 2)

    script.log.info("=" * 15 + "CPU" + "=" * 15)
    script.summaryReport.append("#" * 10 + " CPU Summary")
    par = script.par
    console = par.get_console_conn()
    # par.get_to_linux("Red Hat Enterprise Linux Server")
    cpu_core = console.run("cat /proc/cpuinfo | grep processor | wc -l")

    script.log.info('Total core Count:' + cpu_core)
    script.log.info("=" * 15 + "Verification of CPU claimed by OS" + "=" * 15)
    if npar_cpu_cores == cpu_core:
        script.log.info("Number of CPU  matches in RMC and OS")
    else:
        script.log.info("Number of CPU mismatch in RMC and OS")


def memory_match(script):
    npar_details=script.conn.run("show npar verbose")
    npar_memory = int(get_match(r"Volatile\sMemory.*:\s(\d.*)\sG.*",npar_details))

    par = script.par
    console = par.get_console_conn()
    # par.get_to_linux("Red Hat Enterprise Linux Server")
    script.summaryReport.append("#" * 10 + " Memory Summary")
    meminfo = console.run("cat /proc/meminfo")
    start = meminfo.index('MemTotal:') + len('MemTotal:')
    end = meminfo.index('kB', start)
    memtot = meminfo[start:end]
    memtot = memtot.lstrip()
    memtot = int(memtot)
    memtot = (memtot // 1024) // 1024
    start = meminfo.index('MemAvailable:') + len('MemAvailable:')
    end = meminfo.index('kB', start)
    memavi = meminfo[start:end]
    memavi = memavi.lstrip()
    memavi = int(memavi)
    memavi = (memavi // 1024) // 1024
    script.log.info("="*15 + "Memory in OS" +"="*15)
    script.log.info('Memory Total(GB) : ' + str(memtot))
    script.log.info('Memory  Available(GB) : ' + str(memavi))
    script.summaryReport.append('Memory Total(GB) : ' + str(memtot))
    script.summaryReport.append('Memory  Available(GB) : ' + str(memavi))
    script.log.info('='*35)
    script.log.info("=" * 15 + "Memory in RMC" + "=" * 15)
    script.log.info('Memory Total(GB) : ' + str(npar_memory))
    script.summaryReport.append('Memory Total(GB) : ' + str(npar_memory))
    script.log.info('='*35)
    script.log.info("=" * 15 + "Verification of Memory claimed by OS" + "=" * 15)
    if memtot in range(npar_memory-150,npar_memory+150):
        script.log.info("The memory matches in the RMC and OS")

    else:
        script.log.info("Memory mismatch between RMC and OS")


def clear_cae(script):
    script.conn.run("clear cae")

def firmware_info(script):
    firmware_info = script.conn.run("show firmware verbose")
    expected_firmware = get_match(r'Expected(.*)', firmware_info)
    expected_firmware_version = get_match(r'[0-9].*', expected_firmware)
    script.log.info("The expected firmware version is {}".format(expected_firmware_version))

def par_details(script):
    chassis_info_cmd = script.conn.run("show chassis info")
    script.log.info("The chassis information:{}".format(chassis_info_cmd))
    npar_cmd= script.conn.run("show npar")
    script.log.info("The partition information:{}".format(npar_cmd))

def kernel_version(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    kernel_info_cmd = console.run("uname -r")
    script.log.info("kernel version:{}".format(kernel_info_cmd))

def ethcard_details(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    ethcard_cmd = console.sendex('ifconfig | grep -iE "^(eth|en)" \r')
    ethcards=re.findall(r'(e.*):.*',ethcard_cmd)

    for i in range(0, len(ethcards)):
        ethcards[i] = ethcards[i].replace('\x1b[m\x1b[K','')
        ethtool_cmd= console.run("ethtool -i {}".format(ethcards[i]))
        driver_val=get_match(r'driver:(.*)',ethtool_cmd)
        version_val=get_match(r'version:(.*)',ethtool_cmd)
        script.log.info("driver:{}".format(driver_val))
        script.log.info("version:{}".format(version_val))


def fibre_ethernet_storage_details(script):
    script.conn=script.par.get_console_conn()
    get_ethernet(script)
    get_storage(script)
    get_fibre(script)


def topology(script):
    """Fetching Topology output"""

    global topology_op
    topology_op = {'cpu': 0, 'memory': 0, 'fibre': 0, 'network': 0}
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    script.log.info("=" * 15 + "Topology" + "=" * 15)
    output = console.run("topology")
    script.summaryReport.append("#" * 10 + " Topology output")
    cpu = console.run("topology | grep CPUs | awk -F\" \" ' {print $1}'")
    topology_op["cpu"] = cpu
    script.summaryReport.append("Total Number of CPU cores = " + cpu)
    memory = console.run("topology | grep Memory | awk -F\"GB\" ' {print $1}'")
    topology_op["memory"] = memory
    script.summaryReport.append("Total System Memory = " + memory)
    fibre = console.run("topology | grep Fibre | awk -F\" \" ' {print $1}'")
    topology_op["fibre"] = fibre
    script.summaryReport.append("Total Number of FC ports = " + fibre)
    network = console.run("topology | grep Network | awk -F\" \" ' {print $1}'")
    topology_op["network"] = network
    script.summaryReport.append("Total Number of Network Controllers = " + network)

def get_all(script):
    os_verify(script)
    system_log(script)
    cpu_match(script)
    memory_match(script)
    #clear_cae(sript)
    firmware_info(script)
    par_details(script)
    kernel_version(script)
    ethcard_details(script)
    fibre_ethernet_storage_details(script)
    topology(script)

def OS_configs(script):
        conn = script.conn
        info_option = script.args.get_info
        if str(info_option) == '-h':
             script.log.info(
                 'get_os_resources.py [--proto PROTO] [--get_info option]'
                 'Enter the required info option:[m/mem/memory]  [c/cpu] [e/eth/ethernet] [a/all] eg: for memory --get_info memory'
                 'Enter v -Verification of OS installation  ,  sy - system logs c- CPU count  ,  m- memory claimed by OS ,' 
                 'cl - clear cae logs , cae - cae logs e-eth_card verification')
           
             sys.exit()
        elif str(info_option) in ("v", "osverify"):
            script.log.info('Calling os verification function')
            os_verify(script)
        elif str(info_option) in ("sy", "sys_logs"):
            script.log.info('Calling sys_log function')
            system_log(script)
        elif str(info_option) in ("c", "cpu"):
            script.log.info ('Calling get_cpu function')
            cpu_match(script)
        elif str(info_option) in ("m", "memory"):
            script.log.info('Calling get_memory function')
            memory_match(script)
        elif str(info_option) in ("cl", "clear log"):
            script.log.info('Calling clear log function')
            clear_cae(script)
        elif str(info_option) in ("fm", "firmware info"):
            script.log.info('Calling firmware information function')
            firmware_info(script)
        elif str(info_option) in ("par", "par_details"):
            script.log.info('Calling get_log_sheet function')
            par_details(script)
        elif str(info_option) in ("k", "kernel version"):
             script.log.info('Calling kernel information function')
             kernel_version(script)
        elif str(info_option) in ("d", "driver"):
            script.log.info('Calling driver info function')
            ethcard_details(script)
        elif str(info_option) in ("e", "eth", "ethernet storage fibre details"):
            script.log.info('Calling fibre_ethernet_storage_details function')
            fibre_ethernet_storage_details(script)
        elif str(info_option) in ("t", "topology"):
            script.log.info('Calling topology function')
            topology(script)

        else:
             script.log.info('Calling get_all function')
             get_all(script)



def my_setup(script):
        standard_setup(script,
                       required=["proto"],
                       optional=["conn_args", "log_level"],
                       custom={
                           "get_info": {
                               "flags": ["--get_info"],
                               "help": "Enter the required info option:[m/mem/memory] [c/cpu] [e/eth/ethernet] [a/all] eg: for memory --get_info memory",
                           },
                       },
                       conns={"conn": {"con_type": "rmc_cli"}},
                       get_partition = {"delete_existing": "as needed", "par_state": "linux_console", "conn": "conn"},
                       )
        script.summaryReport = []


if __name__ == "__main__":
    script = FtfScript(setup=my_setup)
    script.add_testcase("OS_configs", test_code=OS_configs)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()
