__metaclass__ = type
import socket

LogManager.writeLogAddTimeStamp('APT Python - Automated Demo - Proc Change Socket Connection', 2)

new_job = JobTool.findJobInfo(jobIndex, "")

if new_job.jobID[:2] == 'A1':
    if new_job.JobStatus == 1026 or new_job.JobStatus == 1030:
        t = '["Proc", "{}"]'.format(new_job.jobID)
        sent = False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', 8091))
            sock.sendall(t.encode('utf-8'))
            sock.close()
            sent = True
        except Exception as e:
            LogManager.writeLogAddTimeStamp('APT Python - exception while trying to create socket: {}'.format(e), 2)

        if sent:
            LogManager.writeLogAddTimeStamp('APT Python - Job Status Change socket connection for Job, JobID: {}'.format(new_job.jobID), 2)
