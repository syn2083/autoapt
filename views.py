import django.http
import threading
from watchdog.observers import Observer
from automated_APTDemo import logging_setup
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from .controller import DemoController
from .models import DemoConfig, JIFTemplate
from .forms import DemoConfigForm, JIFTemplateForm
from .controller import DemoController
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from .folder_monitor import folder_monitor_handler as fmh

logger = logging_setup.init_logging()

demo_conf = get_object_or_404(DemoConfig, pk=1)
icd_folders = [demo_conf.idc_1_path, demo_conf.idc_2_path, demo_conf.idc_3_path,
               demo_conf.idc_4_path, demo_conf.td_multi_path]
control = DemoController(demo_conf.jdf_input_path, icd_folders)


class Dispatcher(threading.Thread):
    def __init__(self, command_queue, lock):
        super().__init__()
        self.command_queue = command_queue
        self.lock = lock

    def run(self):
        while True:
            try:
                #self.lock.acquire()
                #logger.debug('Dispatcher acquired a lock..')
                payload = self.command_queue.popleft()
                if payload[0] in ['Accepted', 'Failed']:
                    logger.debug('Calling new job controller')
                    control.new_job(payload)
                if payload[0] in ['Reprint', 'Complete']:
                    control.reprint_job(payload)
                if payload[0] in 'Proc':
                    control.proc_phase(payload)
                #self.lock.release()
            except IndexError:
                pass


def demo_central(request):
    # demo = get_object_or_404(DemoConfig, pk=1)
    # s = DemoController()
    # s.create_workers(jif_acks_path=demo.jif_acks_path, reprint_path=demo.reprint_path, proc_path=demo.proc_phase_path)
    return render(request, 'APTDemo/demo_central.html', {})


def demo_controls(request):
    if request.method == "GET":
        context = RequestContext(request)
        context_dict = {'demo_status': control.demo_status}
        return render_to_response('APTDemo/demo_controller.html', context_dict, context)
    elif request.method == "POST":
        return render(request, 'APTDemo/demo_controller.html', {'controller': control})


def start_demo(request):
    demo_conf = get_object_or_404(DemoConfig, pk=1)
    logger.debug('Start demo request.')
    control.lock = threading.Lock()
    control.dispatcher = Dispatcher(control.command_queue, control.lock)
    control.dispatcher.start()

    logger.debug('Starting jif monitor.')
    jifack = Observer()
    jifack.schedule(fmh.JIFAckHandler(control.command_queue, control.lock), path=demo_conf.jif_acks_path)
    jifack.start()
    control.observers.append(jifack)
    logger.debug('Starting reprint monitor.')
    reprintmon = Observer()
    reprintmon.schedule(fmh.ReprintHandler(control.command_queue, control.lock), path=demo_conf.reprint_path)
    reprintmon.start()
    control.observers.append(reprintmon)
    logger.debug('Starting proc change monitor.')
    proc_mon = Observer()
    proc_mon.schedule(fmh.ProcChangeManager(control.command_queue, control.lock), path=demo_conf.proc_phase_path)
    proc_mon.start()
    control.observers.append(proc_mon)
    logger.debug('Monitors initialized.')
    reply = control.start_demo()
    control.demo_status = 1
    #control.dispatcher.join()
    return django.http.HttpResponse(reply)


def stop_demo(request):
    logger.debug('Stop demo request.')
    reply = control.stop_demo()
    return django.http.HttpResponse(reply)


def demo_config(request):
    demo = get_object_or_404(DemoConfig, pk=1)
    if request.method == "POST":
        form = DemoConfigForm(request.POST, instance=demo)
        if form.is_valid():
            logger.debug(form.data)
            demo = form.save(commit=False)
            demo.save()
    else:
        form = DemoConfigForm(instance=demo)
    return render(request, 'APTDemo/demo_config.html', {'form': form})


def jif_config(request):
    jif = get_object_or_404(JIFTemplate, pk=1)
    if request.method == "POST":
        form = JIFTemplateForm(request.POST, instance=jif)
        if form.is_valid():
            jif = form.save(commit=False)
            jif.save()
    else:
        form = JIFTemplateForm(instance=jif)
    return render(request, 'APTDemo/jif_config.html', {'form': form, 'jif': jif})


@csrf_exempt
def job_accepted(request):
    if request.method == "POST":
        x = request.readlines()
        logger.debug(x[0].decode('utf-8'))
        t = x[0].decode('utf-8')
        control.new_job(t)
    return render(request, 'APTDemo/job_accepted.html', {})


@csrf_exempt
def reprint_sent(request):
    if request.method == "POST":
        x = request.readlines()
        logger.debug(x[0].decode('utf-8'))
        t = x[0].decode('utf-8')
        control.reprint_job(t)
    return render(request, 'APTDemo/reprint_sent.html', {})


@csrf_exempt
def proc_phase(request):
    if request.method == "POST":
        x = request.readlines()
        logger.debug(x[0].decode('utf-8'))
        t = x[0].decode('utf-8')
        control.proc_phase(t)
    return render(request, 'APTDemo/proc_phase.html', {})


@csrf_exempt
def job_complete(request):
    if request.method == "POST":
        x = request.readlines()
        logger.debug(x[0].decode('utf-8'))
        t = x[0].decode('utf-8')
        control.complete_job(t)
    return render(request, 'APTDemo/job_complete.html', {})
