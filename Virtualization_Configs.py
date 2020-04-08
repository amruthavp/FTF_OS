import re
import sys
from exllib.setup_teardown import standard_cleanup, standard_setup
from ftflib.ftf_script import FtfScript
from ftflib.toolbox import get_match
from tests.demo.OSOS import cpu_match,memory_match,system_log,clear_cae,kernel_version,topology
from tests.mcs.resource_check_os.get_os_resourse import *

def clearcae(script):
    clear_cae(script)

def systemlog(script):
    system_log(script)

def kernelversion(script):
    kernel_version(script)

def virsh(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    virsh_cmd=console.run("virsh list --all")
    #console.run('y')
    #console.run('y')
    script.log.info("Guests created are {}".format(virsh_cmd))

def stat_commands(script):
    par = script.par
    console = par.get_console_conn()
    #par.get_to_linux("Red Hat Enterprise Linux Server")
    iostat_cmd = console.run("iostat")
    script.log.info("iostat information {}".format(iostat_cmd))
    vmstat_cmd = console.run("vmstat")
    script.log.info("vmstat information {}".format(vmstat_cmd))
    mpstat_cmd = console.run("mpstat")
    script.log.info("mpstat information {}".format(mpstat_cmd))

def cpu_memory_match(script):
    cpu_match(script)
    memory_match(script)

def ethernet(script):
    script.conn = script.par.get_console_conn()
    get_ethernet(script)

def topology_info(script):
   topology(script)

def get_os_resource(script):
    conn = script.conn
    info_option = script.args.get_info
    if str(info_option) == '-h':
        script.log.info(
            'get_os_resources.py [--host HOST] [--user username] [--password password] [--get_info option]')
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
        virsh(script)
    elif str(info_option) in ("i", "iostat, mpstat, vmstat informations"):
        script.log.info('Calling iostat, mpstat, vmstat function')
        statcommands(script)
    elif str(info_option) in ("cpu", "get cpu"):
        script.log.info('Calling cpu information function')
        cpu_memory_match(script)
    elif str(info_option) in ("io", "get IO"):
        script.log.info('Calling ethernet information function')
        ethernet(script)
    elif str(info_option) in ("t", "topology"):
        script.log.info('Calling topology function')
        topology_info(script)
    else:
        script.log.info('Calling get_all function')
        get_all(script)


def get_all(script):
    #clearcae(script)
    #showcae(script)
    systemlog(script)
    kernelversion(script)
    stat_commands(script)
    cpu_memory_match(script) 
    ethernet(script)
    virsh(script)
    topology_info(script)

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
    script_obj = FtfScript(setup=my_setup, cleanup=standard_cleanup)
    script_obj.setup()
    script_obj.add_testcase(
        "configurations for Sles",
        test_code=get_os_resource,
    )
    script_obj.run()
    script_obj.exit()
