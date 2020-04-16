"""Script to get information on Secureboot configurations:
  system logs
  kernel version
  Secureboot status from OS
  Secureboot and Secureboot Next status from RMC .
usage : secureboot_configs.py [--proto PROTO] [--partition PARTITION] [--get_info option]

Required Arguments:

        --proto PROTO             Name of System Under Test
        --get_info                s/system_logs
                                  k/kernel_build_version
                                  bo/secureboot_status_in_os
                                  br/secureboot_status_in_rmc
                                  eth/get_ethernet_info
Optional Arguments:

        -h, -?, --help            show this help message and exit"""


from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.ftf_script import FtfScript
from ftflib.toolbox import get_match
import re
from tests.mcs.resource_check_os.osinstallation_configs import *
import sys


def kernelversion(script):

    """ Displaying kernel version """
    kernel_version(script)

def boot_status_os(script):

    """ Checking secureboot status on the OS console"""

    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    boot_state = console.run("mokutil --sb-state")
    boot_state_os = get_match(r'disabled',boot_state)
    if boot_state_os== "disabled":
        script.log.info("Secure boot is disabled in OS")
        script.summaryReport.append("#" * 10 + " Secureboot status on OS")
        script.summaryReport.append("The secureboot is disabled on the OS")
    else:
        script.log.info("Secure boot is enabled in OS")
        script.summaryReport.append("#" * 10 + " Secureboot status on OS")
        script.summaryReport.append("The secureboot is enabled on the OS")

def boot_status_rmc(script):

    """Checking the secureboot and secureboot next status on the RMC console """

    conn = script.conn
    script.partitions_obj
    npar_details = conn.run("show npar verbose")
    secureboot_state = get_match(r'.*Secure\sBoot.*:\s(.*)', npar_details)
    securebootnext_state= get_match(r'.*Secure\sBoot\sNext\s.*:\s(.*)', npar_details)
    if secureboot_state == "Off":
        script.log.info("The Secure Boot is Off in rmc")
        script.summaryReport.append("#" * 10 + " Secureboot status in RMC")
        script.summaryReport.append("The secureboot is disabled on RMC")
    else:
        script.log.info("The Secure Boot is On in rmc")
        script.summaryReport.append("#" * 10 + " Secureboot status in RMC")
        script.summaryReport.append("The secureboot is enabled on RMC")

    if securebootnext_state == "Off":
        script.log.info("The Secure Boot Next is Off in rmc")
        script.summaryReport.append("The secureboot next is disabled on RMC")
    else:
        script.log.info("The Secure Boot Next is On in rmc")
        script.summaryReport.append("The secureboot next is enabled on RMC")

def systemlog(script):

    """Displaying cae logs from RMC console, syslog and dmesg from OS console"""
    system_log(script)


def secureboot_resource(script):

    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'secureboot_configs.py [--proto PROTO] [--partition PARTITION] [--get_info option]')
        sys.exit()

    elif str(info_option) in ("k", "kernel_version"):
        script.log.info('Calling kernel information function')
        kernelversion(script)
    elif str(info_option) in ("bo", "secureboot_status_in_os"):
        script.log.info('Calling kernel information function')
        boot_status_os(script)
    elif str(info_option) in ("br", "secureboot_status_in_rmc"):
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
                           "help": "Enter the required info option:[s/system logs] [k/kernel build version] [bo/secureboot_status_in_os] [br/secureboot_status_in_rmc] eg: for eg: for kernel version --get_info k",
                       },
                   },
                   conns={"conn": {"con_type": "rmc_cli"}},
                   get_partition={"delete_existing": "as needed", "par_state": "linux_console", "conn": "conn"},
                   )
    script.summaryReport = []


if __name__ == "__main__":
    script = FtfScript(setup=my_setup)
    script.add_testcase("secureboot_resource", test_code=secureboot_resource)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()
