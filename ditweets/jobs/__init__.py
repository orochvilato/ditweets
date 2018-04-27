import pkgutil
import datetime

from apscheduler.schedulers.background import BackgroundScheduler

def enableLogging():
    import logging
    #log = logging.getLogger('apscheduler.executors.default')
    log = logging.getLogger()
    log.setLevel(logging.INFO)  # DEBUG

    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)


enableLogging()
jobdefinitions = dict()

scheduler = BackgroundScheduler()

from ditweets.tools import api_notify


def walk_pkg(path):
    for importer, modname, ispkg in pkgutil.walk_packages(path):
        #print "Found submodule %s (is a package: %s)" % (modname, ispkg)
        if ispkg:
            m = importer.find_module(modname).load_module(modname)
            #print "import %s" % modname
            walk_pkg(m.__path__)

def crash_listener(event):
    jdef =  jobdefinitions[event.job_id]
    if event.exception or event.retval:
        if 'notify_error' in jdef.keys():

            api_notify('Erreur job %s' % event.job_id,msg=event.retval,recipients = jdef['notify_error'])
    else:

        if 'notify_success' in jdef.keys():
            api_notify('Succes job %s' % event.job_id,recipients = jdef['notify_success'])


def job_wrapper(job):
    import sys
    def execute():
        try:
            job.job()
            result = None
        except:
            import traceback
            result = traceback.format_exc()

        return result

    return execute

def start_scheduler():
    import os
    import psutil

    try:
        pid = int(open("/tmp/scheduler_ditweets.pid").read())
    except IOError:
        pid = 0

    if psutil.pid_exists(pid):
        pass
        print("scheduler deja lance")
    else:
        open("/tmp/scheduler_ditweets.pid","w").write("%d" % os.getpid())


        walk_pkg(__path__)
        for importer, modname, ispkg in pkgutil.walk_packages(__path__):
            if not ispkg:
                m = importer.find_module(modname).load_module(modname)
                if hasattr(m,'definition'):

                    jdef = m.definition
                    jobdefinitions[modname] = jdef
                    print("Found job %s (%s)" % (modname, jdef['description']))
                    if jdef['active']:
                        print("Job %s ready to start" % modname)
                        scheduler.add_job(job_wrapper(m),jdef['type'],id=modname,**jdef['params'])

        from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
        scheduler.add_listener(crash_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        scheduler.start()
        print("scheduler started")
        #eai_notify('Scheduler lance pid %d' % os.getpid(),recipients=['informatique@chilbp.fr'])

def stop_scheduler():
    try:
        scheduler.shutdown()
    except:
        pass
    print("scheduler stopped")
