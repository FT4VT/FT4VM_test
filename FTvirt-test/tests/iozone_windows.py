import logging
import os
from autotest.client import utils
from virttest import postprocess_iozone
from virttest import utils_misc


def run_iozone_windows(test, params, env):
    """
    Run IOzone for windows on a windows guest:
    1) Log into a guest
    2) Execute the IOzone test contained in the winutils.iso
    3) Get results
    4) Postprocess it with the IOzone postprocessing module

    :param test: kvm test object
    :param params: Dictionary with the test parameters
    :param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=timeout)
    results_path = os.path.join(test.resultsdir,
                                'raw_output_%s' % test.iteration)
    analysisdir = os.path.join(test.resultsdir, 'analysis_%s' % test.iteration)

    # Run IOzone and record its results
    drive_letter = utils_misc.get_winutils_vol(session)
    c = params["iozone_cmd"] % drive_letter
    t = int(params.get("iozone_timeout"))
    logging.info("Running IOzone command on guest, timeout %ss", t)
    results = session.cmd_output(cmd=c, timeout=t)
    utils.open_write_close(results_path, results)

    # Postprocess the results using the IOzone postprocessing module
    logging.info("Iteration succeed, postprocessing")
    a = postprocess_iozone.IOzoneAnalyzer(list_files=[results_path],
                                          output_dir=analysisdir)
    a.analyze()
    p = postprocess_iozone.IOzonePlotter(results_file=results_path,
                                         output_dir=analysisdir)
    p.plot_all()
