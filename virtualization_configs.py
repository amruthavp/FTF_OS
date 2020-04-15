"""Script to get information on system logs, kernel version, guests created, cpu, memory, ethernet and device statistics

usage : virtualization.py [--proto PROTO] [--partition PARTITION] [--get_info option]

Required Arguments:

        --proto PROTO             Name of System Under Test
        --get_info                s/system logs
                                  k/kernel build version
                                  cpu/get memory and cpu information
                                  v/virsh
                                  i/iostat, mpstat, vmstat informations
                                  eth/get ethernet info
Optional Arguments:

        -h, -?, --help            show this help message and exit
"""

import re
import sys
from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.ftf_script import FtfScript
from ftflib.toolbox import get_match
from tests.mcs.resource_check_os.osinstallation_configs import *
from tests.mcs.resource_check_os.get_os_resourse import *

def clearcae(script):

    """Clearing the cae logs on RMC console"""
    clear_cae(script)

def systemlog(script):

    """Displaying cae logs from RMC console, syslog and dmesg from OS console"""
    system_log(script)

def kernelversion(script):

    """Displaying the kernel version"""
    kernel_version(script)

def guests_created(script):

    """ Console logs showing all the guest installed and running"""

    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    guests_info=console.run("virsh list --all")
    script.log.info("Guests created are {}".format(guests_info))

def device_stats(script):

    """Displays the output of iostat, vmstat, mpstat commands"""

    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    io_stat = console.run("iostat")
    script.log.info("iostat information {}".format(io_stat))
    vm_stat = console.run("vmstat")
    script.log.info("vmstat information {}".format(vm_stat))
    mp_stat = console.run("mpstat")
    script.log.info("mpstat information {}".format(mp_stat))

def cpu_memory_match(script):

    """Checks  and verifies the cpu and memory information gathered from RMC and OS console"""

    cpu_match(script)
    memory_match(script)

def ethernet_info(script):

    """ Displays PCI Ethernet Controller information"""

    script.conn = script.par.get_console_conn()
    get_ethernet(script)

def topology_info(script):

    """Fetching Topology output"""
    topology(script)

def virtualization_resource(script):

    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'virtualization_configs.py [--proto PROTO] [--partition PARTITION] [--get_info option]')
        sys.exit()
    elif str(info_option) in ("s", "system logs"):
        script.log.info('Calling system logs function')
        systemlog(script)
    elif str(info_option) in ("c", "clear cae"):
        script.log.info('Calling clear logs function')
        clearcae(script)
    elif str(info_option) in ("k", "kernel build version"):
        script.log.info('Calling kernel version function')
        kernelversion(script)
    elif str(info_option) in ("v", "virsh"):
        script.log.info('Calling virsh function')
        guests_created(script)
    elif str(info_option) in ("i", "iostat, mpstat, vmstat informations"):
        script.log.info('Calling iostat, mpstat, vmstat function')
        device_stats(script)
    elif str(info_option) in ("cpu", "get memory and cpu information"):
        script.log.info('Calling cpu information function')
        cpu_memory_match(script)
    elif str(info_option) in ("eth", "get ethernet info"):
        script.log.info('Calling ethernet information function')
        ethernet_info(script)
    elif str(info_option) in ("t", "topology"):
        script.log.info('Calling topology function')
        topology_info(script)
    else:
        script.log.info('Calling get_all function')
        get_all(script)


def get_all(script):
    systemlog(script)
    kernelversion(script)
    device_stats(script)
    cpu_memory_match(script)
    ethernet_info(script)
    guests_created(script)
    topology_info(script)

def my_setup(script):
    standard_setup(script,
            required=["proto"],
                       optional=["conn_args", "log_level"],
                       custom={
                           "get_info": {
                               "flags": ["--get_info"],
                               "help": "Enter the required info option:[s/system logs] [k/kernel build version] [cpu/get memory and cpu information] [v/virsh]  eg: for kernel version --get_info k",
                           },
                       },
                       conns={"conn": {"con_type": "rmc_cli"}},
                       get_partition={"delete_existing": "as needed", "par_state": "linux_console", "conn": "conn"},
                       )
    script.summaryReport = []


if __name__ == "__main__":
    script_obj = FtfScript(setup=my_setup, cleanup=standard_cleanup)
    script_obj.setup()
    script_obj.add_testcase(
        "Virtualization configs",
        test_code=virtualization_resource,
    )
    script_obj.run()
    script_obj.exit()
