#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Generate jobs for jenkins based on a .csv file describing the parameters."""

import argparse
import csv
import os
import os.path
import re
import jenkins

from time import sleep

class JobGenerator(object):
    def __init__(self, argv):
        self.argv = argv
        self.template = None
        self.jenkins_instance = None
        self.REGEXPS = {}

    @property
    def jenkins(self):
        if not self.jenkins_instance:
            # We will have to do work when we require authentication for
            # our Jenkins instances. Need to either pass in user/password
            # or read from a config file of some kind.
            self.jenkins_instance = jenkins.Jenkins(self.config['host'])
        return self.jenkins_instance

    def initialize_regexps(self):
        for key in self.REGEXPS:
            self.REGEXPS[key] = re.compile(self.REGEXPS[key])

    def get_config(self):
        parser = argparse.ArgumentParser(description='Script for generating Jenkins jobs for MSE testing')
        parser.add_argument('--template', required=True)
        parser.add_argument('--table-csv', required=True, dest='csv')
        parser.add_argument('--jenkins-host', required=True, dest='host')
        parser.add_argument('--generate-files', action='store_true')
        args = parser.parse_args(self.argv)

        self.config = {}
        self.config['template'] = args.template
        self.config['csv'] = args.csv
        self.config['host'] = args.host
        if args.generate_files:
            self.config['generate_files'] = True
        else:
            self.config['generate_files'] = False

    '''Return a copy of the template so that it can be reused over and over again.'''
    def get_template(self):
        if not self.template:
            with open(self.config['template']) as myfile:
                self.template=myfile.read()
        data = self.template
        return data

    def get_platform_extension(self, platform):
        if platform == 'linux64' or platform == 'linux32' or platform == 'linux':
            return 'tar.bz2'
        elif platform == 'win32' or platform == 'win64':
            return 'zip'
        elif platform == 'mac' or platform == 'mac64':
            return 'dmg'
        raise 'Unknown platform %s' % platform

    def get_artifact_platform(self, platform):
        if platform == 'linux64':
            return 'linux-x86_64'
        elif platform == 'linux32':
            return 'linux-i686'
        else:
            return platform

    def get_lowest_release(self, release1, release2):
        if release1 == 'esr' or release2 == 'esr':
            return 'esr'
        elif release1 == 'release' or release2 == 'release':
            return 'release'
        elif release1 == 'beta' or release2 == 'beta':
            return 'beta'
        elif release1 == 'aurora' or release2 == 'aurora':
            return 'aurora'
        else:
            return 'nightly'

    def process_row(self, row, template):
        return template

    def generate(self):
        self.get_config()
        self.initialize_regexps()

        with open(self.config['csv'], 'rU') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                template = self.get_template()
                jobname, template = self.process_row(row, template)

                # Generate directory
                if self.config['generate_files']:
                    if not os.path.exists('jobs'):
                        os.makedirs('jobs')

                    dir = os.path.join('jobs', jobname)
                    if not os.path.exists(dir):
                        os.makedirs(dir)

                    # Write it out
                    config_path = os.path.join('jobs', jobname, 'config.xml')
                    config_file = open(config_path, 'w')
                    config_file.write(template)
                    config_file.close()
                else:
                    # Tell Jenkins about it.
                    if self.jenkins.job_exists(jobname):
                        self.jenkins.reconfig_job(jobname, template)
                    else:
                        self.jenkins.create_job(jobname, template)
                        # Inundating the jenkins server causes it to raise
                        sleep(1)

            csvfile.close()

            print "Finished processing."
            return 0
