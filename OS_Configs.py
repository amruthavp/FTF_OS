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
    buff8=console.run('lsscsi | grep -i disk')
    val5=re.findall(r'ATA',buff8)
    val6=get_match(r'FC',buff8)
    val7=get_match(r'MSCC',buff8)
    b = re.findall(r'(sd[a-z]).*', buff8)
    a = console.run('lsblk')
    c = get_match(r'.*efi', a)
    d = get_match(r'sd[a-z]', c)
    script.log.info("="*15 +"Verification of OS installation" +"="*15)
    if d in b:
        script.log.info("OS installation was verified")
    else:
        script.error("OS installation error")
    if "ATA" in val5:
        script.log.info("OS is installed on the hard disk")
    elif val6 == "FC":
        script.log.info("OS is installed on FC verified")

    elif val7 == "MSCC":
        script.log.info("OS is installed on FC verified")

    else:
        script.log.info("Failure")

def system_log(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    buffer = console.run("cat /var/log/messages | grep -i 'error'")
    script.log.info( "="*15 + "System logs" +"="*15)
    if "error" in buffer:
        script.log.info("Errors exists:{}".format(buffer))
    else:
        script.log.info("no errors")

    buffer = console.run("dmesg | grep -iE 'panic|fail|work|retries|BUG'")
    if "error" in buffer:
        script.log.info("Errors exists:{}".format(buffer))
    else:
        script.log.info("no errors")


def cpu_match(script):
    buff5 = script.conn.run("show npar verbose")
    val5 = str(int(get_match(r'Cores.*\s(\d+)', buff5)) * 2)

    script.log.info("=" * 15 + "CPU" + "=" * 15)
    script.summaryReport.append("#" * 10 + " CPU Summary")
    par = script.par
    console = par.get_console_conn()
    # par.get_to_linux("Red Hat Enterprise Linux Server")
    cpu_core = console.run("cat /proc/cpuinfo | grep processor | wc -l")

    script.log.info('Total core Count:' + cpu_core)
    script.log.info("=" * 15 + "Verification of CPU claimed by OS" + "=" * 15)
    if val5 == cpu_core:
        script.log.info("Number of CPU  matches")
    else:
        script.log.info("Number of CPU mismatch")


def memory_match(script):
    a=script.conn.run("show npar verbose")
    buff7 = int(get_match(r"Volatile\sMemory.*:\s(\d.*)\sG.*",a))

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
    script.log.info('Memory Total(GB) : ' + str(buff7))
    script.summaryReport.append('Memory Total(GB) : ' + str(buff7))
    script.log.info('='*35)
    script.log.info("=" * 15 + "Verification of Memory claimed by OS" + "=" * 15)
    if memtot in range(buff7-150,buff7+150):
        script.log.info("The memory is matched")

    else:
        script.log.info("Memory mismatch")


def clear_cae(script):
    script.conn.run("clear cae")

def show_cae(script):
    script.log.info("=" * 15 + "cae logs" + "=" * 15)
    b1=script.conn.run("show cae")
    script.log.info("The cae logs are:{}".format(b1))

def firmwareinfo(script):
    buff1 = script.conn.run("show firmware verbose")
    val1 = get_match(r'Expected(.*)', buff1)
    val2 = get_match(r'[0-9].*', val1)
    script.log.info("The expected firmware version is {}".format(val2))

def  par_details(script):
    b2 = script.conn.run("show chassis info")
    script.log.info("The chassis information:{}".format(b2))
    b3 = script.conn.run("show npar")
    script.log.info("The partition information:{}".format(b3))

def kernel_version(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    buffer = console.run("uname -r")
    script.log.info("kernel version:{}".format(buffer))

def ethcard_details(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    buffer1 = console.sendex('ifconfig | grep -iE "^(eth|en)" \r')
    val3=re.findall(r'(e.*):.*',buffer1)

    for i in range(0, len(val3)):
        val3[i] = val3[i].replace('\x1b[m\x1b[K','')
        buffer2= console.run("ethtool -i {}".format(val3[i]))
        buff3=get_match(r'driver:(.*)',buffer2)
        buff4=get_match(r'version:(.*)',buffer2)
        script.log.info("driver:{}".format(buff3))
        script.log.info("version:{}".format(buff4))


def ethernet(script):
    script.conn=script.par.get_console_conn()
    get_ethernet(script)

def storage(script):
    script.conn = script.par.get_console_conn()
    get_storage(script)

def fibre(script):
    script.conn = script.par.get_console_conn()
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
    show_cae(script)
    firmwareinfo(script)
    par_details(script)
    kernel_version(script)
    ethcard_details(script)
    ethernet(script)
    storage(script)
    fibre(script)
    topology(script)

def get_os_resource(script):
        conn = script.conn
        info_option = script.args.get_info
        if str(info_option) == '-h':
             script.log.info(
                 'get_os_resources.py [--host HOST] [--user username] [--password password] [--get_info option]'
                 'Enter the required info option:[m/mem/memory] [s/storage] [f/fibre] [c/cpu] [e/eth/ethernet] [a/all] eg: for memory --get_info memory'
                  'Enter v -Verification of OS installation  ,  sy - system logs c- CPU count  ,  m- memory claimed by OS ,  cl - clear cae logs , cae - cae logs'
                 'e-eth_card verification')
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
        elif str(info_option) in ("cae", "CAE"):
            script.log.info('Calling CAE function')
            show_cae(script)
        elif str(info_option) in ("fm", "firmware info"):
            script.log.info('Calling firmware information function')
            firmwareinfo(script)
        elif str(info_option) in ("par", "par_details"):
            script.log.info('Calling get_log_sheet function')
            par_details(script)
        elif str(info_option) in ("k", "kernel version"):
             script.log.info('Calling kernel information function')
             kernel_version(script)
        elif str(info_option) in ("d", "driver"):
            script.log.info('Calling driver info function')
            ethcard_details(script)
        elif str(info_option) in ("e", "eth", "ethernet"):
            script.log.info('Calling get_ethernet function')
            ethernet(script)
        elif str(info_option) in ("s", "storage"):
             script.log.info('Calling get_storage function')
             storage(script)
        elif str(info_option) in ("f", "fibre"):
            script.log.info('Calling get_fibre function')
            fibre(script)
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
                               "help": "Enter the required info option:[m/mem/memory] [s/storage] [f/fibre] [c/cpu] [e/eth/ethernet] [a/all] eg: for memory --get_info memory",
                           },
                       },
                       conns={"conn": {"con_type": "rmc_cli"}},
                       get_partition = {"delete_existing": "as needed", "par_state": "linux_console", "conn": "conn"},
                       )
        script.summaryReport = []


if __name__ == "__main__":
    script = FtfScript(setup=my_setup)
    script.add_testcase("get_os_resource", test_code=get_os_resource)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()