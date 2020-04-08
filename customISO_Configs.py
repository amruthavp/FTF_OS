import sys
import re
from ftflib.ftf_script import FtfScript
from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.toolbox import get_match
from tests.demo.OSOS import system_log, clear_cae,show_cae, ethcard_details

def clearcae(script):
    clear_cae(script)

def showcae(script):
    show_cae(script)

def systemlog(script):
    system_log(script)

def ethcarddetails(script):
    ethcard_details(script)

def firmwareinfo(script):
    buff6 = script.conn.run("show firmware verbose")
    val2 = get_match(r'Expected(.*)', buff6)
    val3 = get_match(r'[0-9].*', val2)
    val3=val3.strip()
    script.log.info("The expected firmware version is {}".format(val3))
    par = script.par
    console = par.get_console_conn()
    buff6 = console.sendex('dmidecode -s bios-version\r')
    val4= get_match(r'Bundle:(.*)\s[A-Z].*',buff6)
    val4=val4.strip()
    if val3==val4:
        script.log.info("The firmware versions match in the RMC and OS console")
    else:
        script.log.info("The firmware versions do not match")


def get_os_resource(script):
    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'get_os_resources.py [--host HOST] [--user username] [--password password] [--get_info option]')
        sys.exit()
    elif str(info_option) in ("c", "clear cae"):
        script.log.info('Calling clear logs function')
        clearcae(script)
    elif str(info_option) in ("cae", "show cae"):
        script.log.info('Calling cae logs function')
        showcae(script)
    elif str(info_option) in ("s", "system logs"):
        script.log.info('Calling system logs function')
        systemlog(script)
    elif str(info_option) in ("d", "ethcard details"):
        script.log.info('Calling ethcard details info function')
        ethcarddetails(script)
    elif str(info_option) in ("f", "firmware"):
        script.log.info('Calling firmware info function')
        firmwareinfo(script)

    else:
        script.log.info('Calling get_all function')
        get_all(script)

def get_all(script):
    #clearcae(script)
    #showcae(script)
    systemlog(script)
    firmwareinfo(script)
    ethcarddetails((script))

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
    script.add_testcase("get_os_resource", test_code=get_os_resource)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()