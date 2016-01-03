#!/usr/bin/env kross
# -*- coding: utf-8 -*-
import KTorrent
import KTScriptingPlugin
import Kross

from KTorrent import log, torrents, torrent
from KTScriptingPlugin import createTimer, scriptDir
from KTScriptingPlugin import readConfigEntryInt, writeConfigEntryBool, writeConfigEntryInt, readConfigEntryBool, syncConfig
from urllib2 import urlopen

t = Kross.module("kdetranslation")

TRACKERS_URL = 'https://raw.githubusercontent.com/ohadcn/torrentTrackersList/master/lists/good.txt'

class trackerListUpdater:
	def __init__(self):
		log('loading trackerListUpdater')
		self.autoRetry = False
		self.hours = 0
		self.minutes = 5
		self.seconds = 0
		self.updateBack = False


	def load(self):
		self.autoRetry = readConfigEntryBool('trackerListUpdaterScript', 'autoRetry', self.autoRetry)
		self.hours = readConfigEntryInt('trackerListUpdaterScript', 'hours', self.hours)
		self.minutes = readConfigEntryInt('trackerListUpdaterScript', 'minutes', self.minutes)
		self.seconds = readConfigEntryInt('trackerListUpdaterScript', 'seconds', self.seconds)
		self.updateBack = readConfigEntryBool('trackerListUpdaterScript', 'sendBack', self.updateBack)
		self.updateTrackers()


	def save(self):
		writeConfigEntryBool('trackerListUpdaterScript', 'autoRetry', self.autoRetry)
		writeConfigEntryInt('trackerListUpdaterScript', 'hours', self.hours)
		writeConfigEntryInt('trackerListUpdaterScript', 'minutes', self.minutes)
		writeConfigEntryInt('trackerListUpdaterScript', 'seconds', self.seconds)
		writeConfigEntryBool('trackerListUpdaterScript', 'sendBack', self.updateBack)
		syncConfig('trackerListUpdaterScript')


	def startTimer(self):
		self.timer = createTimer(True)
		self.timer.connect('timeout()',self.updateTrackers)
		self.timer.start((self.hours * 3600 + self.minutes * 60 + self.seconds)*1000)


	def updateTrackers(self):
		try:
			self.rawls = urlopen(TRACKERS_URL).read()
		except:
			self.rawls=''
		if len(self.rawls) < 20:
			log('failed to get trackers list' + ('; retrying in ' +
										' and '.join([str(getattr(self, t)) + ' ' + t for t in ('hours', 'minutes', 'seconds') if getattr(self, t) != 0])
										if self.autoRetry else ''))
			if self.autoRetry:
				self.startTimer()
			return
		if self.updateBack:
			try:
				self.deadTrackers = dict.fromKeys(urlopen(TRACKERS_URL).read().split('\n'))
			except:
				log('can\'t get dead trackers list: unenabeling update back')
				self.deadTrackers = {}
		self.trackers=self.rawls.split('\n')
		log('found ' + str(len(self.trackers)) + ' trackers; adding them to every found torrent...')		
		self.updateTorrents()


	def updateTorrents(self):
		for ih in torrents():
			tor=torrent(ih)
			for tracker in self.trackers:
				tor.addTracker(tracker)	
			tor.announce()


	def configure(self):
		forms = Kross.module("forms")
		dialog = forms.createDialog(t.i18n("Trackers Lists Updater Settings"))
		dialog.setButtons("Ok|Cancel")
		page = dialog.addPage(t.i18n("Trackers Lists Updater"),t.i18n("Trackers Lists Updater"),"kt-bandwidth-scheduler")
		widget = forms.createWidgetFromUIFile(page,KTScriptingPlugin.scriptDir("trackers_lists_updater") + "trackers_lists_updater.ui")
		widget["autoRetry"].checked = self.autoRetry
		widget["hours"].value = self.hours
		widget["minutes"].value = self.minutes
		widget["seconds"].value = self.seconds
		widget["hours"].enabled = self.autoRetry
		widget["minutes"].enabled = self.autoRetry
		widget["seconds"].enabled = self.autoRetry
		widget["updateBack"].checked = self.updateBack
		if dialog.exec_loop():
			self.autoRetry = widget["autoRetry"].checked
			self.hours = widget["hours"].value
			self.minutes = widget["minutes"].value
			self.seconds = widget["seconds"].value
			self.updateBack = widget["updateBack"].checked
			self.save()
			self.updateTrackers()
  

tlu = trackerListUpdater()
tlu.load()


def configure():
	global tlu
	tlu.configure()


def unload():
	global tlu
	del tlu
