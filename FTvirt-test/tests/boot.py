import time
import logging
import sys
from autotest.client.shared import error
from virttest import utils_test


@error.context_aware
def run_boot(test, params, env):
    """
    Qemu reboot test:
    1) Log into a guest
    3) Send a reboot command or a system_reset monitor command (optional)
    4) Wait until the guest is up again
    5) Log into the guest to verify it's up again

    :param test: QEMU test object
    :param params: Dictionary with the test parameters
    :param env: Dictionary with test environment.
    """
    

    timeout = float(params.get("login_timeout", 240))
    #ting test
    #sys.stdout.restore()
    #print "\n\nparams :    ",params,"\n\n\n"
    #end test

    vms = env.get_all_vms()
    #ting test
    sys.stdout.restore()
    print "vms : ",vms,"\n\n\n"
    #end test
    for vm in vms:
        #ting test
        sys.stdout.restore()
        print "vm : ",vm,"\n"
        #end test
        error.context("Try to log into guest '%s'." % vm.name, logging.info)
        session = vm.wait_for_login(timeout=timeout)
        print "after wait\n\n"
        session.close()

    #ting test
    sys.stdout.restore()
    print "after for\n\n\n"
    #end test

    
    if params.get("rh_perf_envsetup_script"):
        for vm in vms:
            session = vm.wait_for_login(timeout=timeout)
            utils_test.service_setup(vm, session, test.virtdir)
            session.close()
    #ting test
    sys.stdout.restore()
    print "params.get reboot_method:  ",params.get("reboot_method"),"\n\n\n"
    #end test
    if params.get("reboot_method"):
        for vm in vms:
            error.context("Reboot guest '%s'." % vm.name, logging.info)
            if params["reboot_method"] == "system_reset":
                time.sleep(int(params.get("sleep_before_reset", 10)))
            # Reboot the VM
            session = vm.wait_for_login(timeout=timeout)
            for i in range(int(params.get("reboot_count", 1))):
                session = vm.reboot(session,
                                    params["reboot_method"],
                                    0,
                                    timeout)
            session.close()
