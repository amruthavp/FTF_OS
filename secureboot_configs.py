"""Script to get information on system logs, kernel version and Secureboot and Secureboot Next status from RMC and OS console
usage : Secureboot_Configs.py [--proto PROTO] [--partition PARTITION] [--get_info option]

Required Arguments:

        --proto PROTO             Name of System Under Test
        --get_info                s/system logs
                                  k/kernel build version
                                  cpu/get memory and cpu information
                                  v/virsh
                                  i/iostat, mpstat, vmstat informations
                                  eth/get ethernet info
Optional Arguments:

        -h, -?, --help              show this help message and exit"""


from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.ftf_script import FtfScript
from ftflib.toolbox import get_match
import re
from tests.mcs.resource_check_os.osinstallation_configs import *
import sys


def kernelversion(script):
    kernel_version(script)

def boot_status_os(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    boot_state = console.run("mokutil --sb-state")
    boot_state_os = get_match(r'disabled',boot_state)
    if boot_state_os== "disabled":
        script.log.info("Secure boot is disabled in OS")
    else:
        script.log.info("Secure boot is enabled in OS")

def boot_status_rmc(script):
    conn = script.conn
    script.partitions_obj
    npar_details = conn.run("show npar verbose")
    secureboot_state = get_match(r'.*Secure\sBoot.*:\s(.*)', npar_details)
    securebootnext_state= get_match(r'.*Secure\sBoot\sNext\s.*:\s(.*)', npar_details)
    if secureboot_state == "Off":
        script.log.info("The Secure Boot is Off in rmc")
    else:
        script.log.info("The Secure Boot is On in rmc")
    if securebootnext_state == "Off":
        script.log.info("The Secure Boot Next is Off in rmc")
    else:
        script.log.info("The Secure Boot Next is On in rmc")
                                 
def systemlog(script):
    system_log(script)

def secureboot_resource(script):
    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'get_os_resources.py [--host HOST] [--user username] [--password password] [--get_info option]')
        sys.exit()

    elif str(info_option) in ("k", "kernel version"):
        script.log.info('Calling kernel information function')
        kernelversion(script)
    elif str(info_option) in ("bo", "secureboot status in os"):
        script.log.info('Calling kernel information function')
        boot_status_os(script)
    elif str(info_option) in ("br", "secureboot status in rmc"):
        script.log.info('Calling kernel information function')
        boot_status_rmc(script)
    elif str(info_option) in ("sy", "sys_logs"):
        script.log.info('Calling sys_log function')
        systemlog(script)
    else:
        script.log.info('Calling get_all function')
        get_all(script)

def get_all(script):
    kernelversion(script)
    boot_status_rmc(script)
    boot_status_os(script)
    #showcae(script)
    systemlog(script)

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
                   get_partition={"delete_existing": "as needed", "par_state": "linux_console", "conn": "conn"},
                   )
    script.summaryReport = []


if __name__ == "__main__":
    script = FtfScript(setup=my_setup)
    script.add_testcase("secureboot_resource", secureboot_resource)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()
