#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Generate jobs for jenkins based on a .csv file describing the parameters."""

import argparse
import sys
import csv
import os
import os.path
import re

REGEXPS = {
    'url1': r'XXURL1XX',
    'package': r'XXPACKAGEXX',
    'url2': r'XXURL2XX',
    'tests': r'XXTESTSXX',
    'triggers': r'XXTRIGGERSXX',
    'expand': r'XXEXPANDXX',
    'slave': r'XXSLAVEXX',
    'platform': r'XXPLATFORMXX',
    'python': r'XXPYTHONXX',
    'bash': r'XXBASHXX',
}

for key in REGEXPS:
    REGEXPS[key] = re.compile(REGEXPS[key])

class JobGenerator():
    def __init__(self):
        pass

class GenerateJobs():
    def __init__(self, argv):
        self.argv = argv
        self.template = None

    def get_config(self):
        parser = argparse.ArgumentParser(description='Script for generating Jenkins jobs for MSE testing')
        parser.add_argument('--template', required=True)
        parser.add_argument('--table-csv', required=True, dest='csv')
        parser.add_argument('--jenkins-host', required=True, dest='host')
        args = parser.parse_args(self.argv)

        self.config = {}
        self.config['template'] = args.template
        self.config['csv'] = args.csv
        self.config['host'] = args.host

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
        elif platform == 'win64':
            return 'win64-x86_64'
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

    def generate(self):
        self.get_config()

        if not os.path.exists('jobs'):
            os.makedirs('jobs')

        with open(self.config['csv'], 'rU') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                jobname = 'mse-web-platform-%s-%s' % (row['Release'], row['PlatformJobLabel'])

                print 'jobname = %s' % jobname

                triggers = 'trigger-firefox-%s-%s, trigger-tests-%s-%s' % (row['Release'], row['Platform'], row['Release'], row['Platform'])

                url1 = '%s/job/firefox-%s-%s/ws/releases' % (self.config['host'], row['Release'], row['Platform'])
                url2 = '%s/job/tests-%s-%s/ws/releases' % (self.config['host'], row['Release'], row['Platform'])

                artifact_platform = self.get_artifact_platform(row['Platform'])

                package = 'firefox-latest-%s.en-US.%s.%s' % (row['Release'], artifact_platform, self.get_platform_extension(row['Platform']))
                tests = 'firefox-latest-%s.en-US.%s.tests.zip' % (row['Release'], artifact_platform)

                # We will need build_file for reporting results to treeherder
                # build_file = 'firefox-latest-%s.en-US.%s.txt' % (row['Release'], artifact_platform1)

                template = self.get_template()

                template = re.sub(REGEXPS['triggers'], triggers, template)
                template = re.sub(REGEXPS['url1'], url1, template)
                template = re.sub(REGEXPS['url2'], url2, template)
                template = re.sub(REGEXPS['package'], package, template)
                template = re.sub(REGEXPS['tests'], tests, template)
                template = re.sub(REGEXPS['slave'], row['Slave'], template)
                template = re.sub(REGEXPS['platform'], row['Platform'], template)
                template = re.sub(REGEXPS['python'], row['Python'], template)
                template = re.sub(REGEXPS['bash'], row['Bash'], template)

                # We will need build_file for reporting results to treeherder
                #template = re.sub(REGEXPS['build_file'], build_file, template)

                # Generate directory
                dir = os.path.join('jobs', jobname)
                if not os.path.exists(dir):
                    os.makedirs(dir)

                # Write it out
                config_path = os.path.join('jobs', jobname, 'config.xml')
                config_file = open(config_path, 'w')
                config_file.write(template)
                config_file.close()

            csvfile.close()

            print "Finished processing."
            return 0


def generate_jobs(argv):
    generator = GenerateJobs(argv)
    return generator.generate()

if __name__ == '__main__':
    result = generate_jobs(sys.argv[1:])
    if result == 0:
        os._exit(0)
    else:
        sys.exit(1)
