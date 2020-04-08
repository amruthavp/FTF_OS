from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.ftf_script import FtfScript
from ftflib.toolbox import get_match
import re
from tests.demo.OSOS import system_log,kernel_version,clear_cae,show_cae
import sys


def kernelversion(script):
    kernel_version(script)

def boot_status_os(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    buffer3 = console.run("mokutil --sb-state")
    buffer4 = get_match(r'disabled',buffer3)
    if buffer4== "disabled":
        script.log.info("Secure boot is disabled in OS")
    else:
        script.log.info("Secure boot is enabled in OS")

def boot_status_rmc(script):
    conn = script.conn
    script.partitions_obj
    buff5 = conn.run("show npar verbose")
    val1 = get_match(r'.*Secure\sBoot.*:\s(.*)', buff5)
    val2= get_match(r'.*Secure\sBoot\sNext\s.*:\s(.*)', buff5)
    if val1 == "Off":
        script.log.info("The Secure Boot is Off in rmc")
    else:
        script.log.info("The Secure Boot is On in rmc")
    if val2 == "Off":
        script.log.info("The Secure Boot Next is Off in rmc")
    else:
        script.log.info("The Secure Boot Next is On in rmc")

def showcae(script):
    show_cae(script)

def systemlog(script):
    system_log(script)

def get_os_resource(script):
    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'get_os_resources.py [--host HOST] [--user username] [--password password] [--get_info option]')
        sys.exit()

    elif str(info_option) in ("k", "kernel version"):
        script.log.info('Calling kernel information function')
        kernelversion(script)
    elif str(info_option) in ("bo", "boot os"):
        script.log.info('Calling kernel information function')
        boot_status_os(script)
    elif str(info_option) in ("br", "boot rmc"):
        script.log.info('Calling kernel information function')
        boot_status_rmc(script)
    elif str(info_option) in ("cae", "CAE"):
        script.log.info('Calling CAE function')
        showcae(script)
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
    script.add_testcase("get_os_resource", test_code=get_os_resource)
    script.setup()
    script.run()
script.log.info('=' * 30)
script.log.info(" " * 10 + "Summary")
script.log.info("\n".join(script.summaryReport))
script.log.info("Report Complete")
script.exit()