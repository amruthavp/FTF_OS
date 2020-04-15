
"""This performs the CustomISO Configuration steps on a Linux OS:
   Displaying system logs.
   Firmware version.
   Driver and firmware version of ethernet cards.
   
   
        
usage: osinstallation_configs.py [-h] [--proto] [--get_info] [--partition]
Ex:post_install.py --proto ah-010-rmc --partition 0
Required Arguments:
  --proto                Name or IP address of System Under Test/proto
  --partition            partition number (0 if running on p0)
  --get_info             [c/clear_cae] [s/system_logs] [f/firmware] [d/ethcard_details] [a/all]
                         
                 
Optional Arguments:
  -h, -?, --help        show this help message and exit
"""





import sys
import re
from ftflib.ftf_script import FtfScript
from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.toolbox import get_match
from tests.mcs.resource_check_os.OSinstall import *

def clearcae(script):
    clear_cae(script)

def systemlog(script):
    system_log(script)

def ethcarddetails(script):
    """Driver and firmware version of ethernet cards"""
    ethcard_details(script)

def firmware_info(script):
    firmware_details = script.conn.run("show firmware verbose")
    buff= get_match(r'Expected(.*)', firmware_details)
    firmware_version_rmc = get_match(r'[0-9].*', buff)
    firmware_version_rmc=firmware_version_rmc.strip()
    script.log.info("The expected firmware version is {}".format(firmware_version_rmc))
    par = script.par
    console = par.get_console_conn()
    firmware_vcmd = console.sendex('dmidecode -s bios-version\r')
    firmware_version_os= get_match(r'Bundle:(.*)\s[A-Z].*',firmware_vcmd)
    firmware_version_os=firmware_version_os.strip()
    if firmware_version_rmc==firmware_version_os:
        script.log.info("The firmware versions match in the RMC and OS console")
    else:
        script.log.info("The firmware versions do not match")


def CustomISO_resource(script):
    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'get_os_resources.py [--host HOST] [--user username] [--password password] [--get_info option]')
        sys.exit()
    elif str(info_option) in ("c", "clear_cae"):
        script.log.info('Calling clear logs function')
        clearcae(script)
    elif str(info_option) in ("s", "system_logs"):
        script.log.info('Calling system logs function')
        systemlog(script)
    elif str(info_option) in ("d", "ethcard_details"):
        script.log.info('Calling ethcard details info function')
        ethcarddetails(script)
    elif str(info_option) in ("f", "firmware"):
        script.log.info('Calling firmware info function')
        firmware_info(script)

    else:
        script.log.info('Calling get_all function')
        get_all(script)

def get_all(script):
    systemlog(script)
    firmware_info(script)
    ethcarddetails((script))

def my_setup(script):
    standard_setup(script,
                   required=["proto"],
                   optional=["conn_args", "log_level"],
                   custom={
                       "get_info": {
                           "flags": ["--get_info"],
                           "help": "Enter the required info option:[c/clear_cae] [s/system_logs] [f/firmware] [d/ethcard_details] [a/all] eg: for system logs --get_info s",
                       },
                   },
                   conns={"conn": {"con_type": "rmc_cli"}},
                   get_partition={"delete_existing": "as needed", "par_state": "linux_console", "conn": "conn"},
                   )
    script.summaryReport = []


if __name__ == "__main__":
    script = FtfScript(setup=my_setup)
    script.add_testcase("CustomISO_resource", test_code=CustomISO_resource)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()
