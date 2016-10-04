__metaclass__ = type
import socket

LogManager.writeLogAddTimeStamp('APT Python - Automated Demo - New Job Socket Connection', 2)

new_job = JobTool.findJobInfo(jobIndex, "")

t = '["Accepted", "{}"]'.format(new_job.jobID)
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
    LogManager.writeLogAddTimeStamp('APT Python - new job socket connection for Job, JobID: {}'.format(new_job.jobID), 2)
