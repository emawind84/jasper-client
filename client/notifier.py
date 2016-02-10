# -*- coding: utf-8-*-
import Queue
import atexit
from modules import Gmail, SSHAuthLog
from apscheduler.schedulers.background import BackgroundScheduler
import logging


class Notifier(object):

    class NotificationClient(object):

        def __init__(self, gather, timestamp):
            self.gather = gather
            self.timestamp = timestamp

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, profile):
        self._logger = logging.getLogger(__name__)
        self.q = Queue.Queue()
        self.profile = profile
        self.notifiers = []
        
        self._logger.debug('Initializing Notifier...')

        if 'gmail_address' in profile and 'gmail_password' in profile:
            self.notifiers.append(self.NotificationClient(
                self.handleEmailNotifications, None))
        else:
            self._logger.warning('gmail_address or gmail_password not set ' +
                                 'in profile, Gmail notifier will not be used')

        if 'ssh_auth_log' in profile:
            self.notifiers.append(self.NotificationClient(
                    self.handleSSHAuthNotifications, None))
        else:
            self._logger.warning('ssh_auth_log not set,' +
                                 'SSH login notifier will not be used')

        job_defaults = {
            'coalesce': True,
            'max_instances': 1
        }
        sched = BackgroundScheduler(timezone="UTC", job_defaults=job_defaults)
        sched.start()
        sched.add_job(self.gather, 'interval', seconds=30)
        atexit.register(lambda: sched.shutdown(wait=False))
        
        # put the scheduler in Notifier object for reference
        self._sched = sched

    def gather(self):
        [client.run() for client in self.notifiers]

    def handleEmailNotifications(self, lastDate):
        """Places new Gmail notifications in the Notifier's queue."""
        emails = Gmail.fetchUnreadEmails(self.profile, since=lastDate)
        if emails:
            lastDate = Gmail.getMostRecentDate(emails)

        def styleEmail(e):
            return "New email from %s." % Gmail.getSender(e)

        for e in emails:
            self.q.put(styleEmail(e))

        return lastDate
    
    def handleSSHAuthNotifications(self, lastpos):
        """Places new ssh login attempts in the Notifier's queue."""
        auths, lastpos = SSHAuthLog.checkInvalidAuthentication(self.profile, lastpos)

        def styleMsg(auth):
            return "Login attempt by user %s from %s" % (auth['user'], auth['ip'])

        for a in auths:
            self._logger.debug('New notification received: %s' % a)
            self.q.put(styleMsg(a))

        return lastpos
    
    def getNotification(self):
        """Returns a notification. Note that this function is consuming."""
        try:
            notif = self.q.get(block=False)
            return notif
        except Queue.Empty:
            return None

    def getAllNotifications(self):
        """
            Return a list of notifications in chronological order.
            Note that this function is consuming, so consecutive calls
            will yield different results.
        """
        notifs = []

        self._logger.debug('Retrieving notifications...')
        notif = self.getNotification()
        while notif:
            notifs.append(notif)
            notif = self.getNotification()

        self._logger.debug('Number of notifications: %s' % len(notifs))
        return notifs
