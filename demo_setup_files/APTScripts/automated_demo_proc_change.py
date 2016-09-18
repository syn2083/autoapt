__metaclass__ = type
import socket

new_job = JobTool.findJobInfo(jobIndex, "")
if new_job.jobID[:2] == 'A1':
	if new_job.JobStatus == 1026 or new_job.JobStatus == 1030:
		t = '["Proc", "{}"]'.format(new_job.jobID)

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('127.0.0.1', 8091))
		sock.sendall(t.encode('utf-8'))
		sock.close()

		LogManager.writeLogAddTimeStamp('APT Python - Job Status Change socket connection for Job, JobID: {}'.format(new_job.jobID), 2)
