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
    'expand': r'XXEXPANDXX',
    'url1': r'XXURL1XX',
    'package1': r'XXPACKAGE1XX',
    'build_file1': r'XXBUILD_FILE1XX',
    'machine1': r'XXMACHINE1XX',
    'arch1': r'XXARCH1XX',
    'url2': r'XXURL2XX',
    'package2': r'XXPACKAGE2XX',
    'build_file2': r'XXBUILD_FILE2XX',
    'machine2': r'XXMACHINE2XX',
    'arch2': r'XXARCH2XX',
    'triggers': r'XXTRIGGERSXX',
    'slave': r'XXSLAVEXX'
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
        parser = argparse.ArgumentParser(description='Script for generating Jenkins jobs for WebRTC testing')
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
            return 'win64'
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
                jobname = 'webrtc-%s-%s' % (row['Release1'], row['PlatformJobLabel1'])
                if row['Release1'] != row['Release2']:
                    jobname = '%s-%s' % (jobname, row['Release2'])
                jobname = '%s-%s' % (jobname, row['PlatformJobLabel2'])
                if row['Networking']:
                    jobname = '%s-%s' % (jobname, row['Networking'])

                print 'jobname = %s' % jobname

                triggers = 'trigger-firefox-%s-%s' % (row['Release1'], row['Platform1'])
                if row['Release1'] != row['Release2'] or row['Platform1'] != row['Platform2']:
                    triggers = '%s,trigger-firefox-%s-%s' % (triggers, row['Release2'], row['Platform2'])

                tests = self.get_lowest_release(row['Release1'], row['Release2'])

                expand = 'expand-tests-%s-linux64' % tests
                if row['Networking']:
                    expand = '%s-network' % expand

                url1 = '%s/job/firefox-%s-%s/ws/releases' % (self.config['host'], row['Release1'], row['Platform1'])
                url2 = '%s/job/firefox-%s-%s/ws/releases' % (self.config['host'], row['Release2'], row['Platform2'])

                artifact_platform1 = self.get_artifact_platform(row['Platform1'])
                artifact_platform2 = self.get_artifact_platform(row['Platform2'])

                package1 = 'firefox-latest-%s.en-US.%s.%s' % (row['Release1'], artifact_platform1, self.get_platform_extension(row['Platform1']))
                package2 = 'firefox-latest-%s.en-US.%s.%s' % (row['Release2'], artifact_platform2, self.get_platform_extension(row['Platform2']))

                build_file1 = 'firefox-latest-%s.en-US.%s.txt' % (row['Release1'], artifact_platform1)
                build_file2 = 'firefox-latest-%s.en-US.%s.txt' % (row['Release2'], artifact_platform2)

                template = self.get_template()

                template = re.sub(REGEXPS['triggers'], triggers, template)
                template = re.sub(REGEXPS['expand'], expand, template)
                template = re.sub(REGEXPS['url1'], url1, template)
                template = re.sub(REGEXPS['url2'], url2, template)
                template = re.sub(REGEXPS['package1'], package1, template)
                template = re.sub(REGEXPS['package2'], package2, template)
                template = re.sub(REGEXPS['build_file1'], build_file1, template)
                template = re.sub(REGEXPS['build_file2'], build_file2, template)
                template = re.sub(REGEXPS['machine1'], row['Host1'], template)
                template = re.sub(REGEXPS['machine2'], row['Host2'], template)
                template = re.sub(REGEXPS['arch1'], row['Arch1'], template)
                template = re.sub(REGEXPS['arch2'], row['Arch2'], template)
                template = re.sub(REGEXPS['slave'], row['Slave'], template)

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
