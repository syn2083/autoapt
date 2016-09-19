__metaclass__ = type
import socket

LogManager.writeLogAddTimeStamp('APT Python - Automated Demo - Complete Socket Connection', 2)

new_job = JobTool.findJobInfo(jobIndex, "")

t = '["Complete", "{}"]'.format(new_job.jobID)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 8091))
sock.sendall(t.encode('utf-8'))
sock.close()

LogManager.writeLogAddTimeStamp('APT Python - complete socket connection for Job, JobID: {}'.format(new_job.jobID), 2)
