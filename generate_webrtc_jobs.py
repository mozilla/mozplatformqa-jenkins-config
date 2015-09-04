#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Generate jobs for jenkins based on a .csv file describing the parameters."""

import os
import re
import sys

from job_generator import JobGenerator

platform_host_data = {
    'linux32': {
        'arch': 'i686' ,
        'platform': 'linux32',
        'os': 'linux-32',
        'extension': 'tar.bz2',
        'artifact_platform': 'linux-i686',
    },
    'linux64': {
        'arch': 'x86_64',
        'platform': 'linux64',
        'os': 'linux-64',
        'extension': 'tar.bz2',
        'artifact_platform': 'linux-x86_64',
    },
    'mac': {
        'arch': 'x86_64',
        'platform': 'mac',
        'os': 'mac-10.10',
        'extension': 'dmg',
        'artifact_platform': 'mac',
    },
    'mac10_6_32': {
        'arch': 'i686',
        'platform': 'mac',
        'os': 'mac-10.6',
        'extension': 'dmg',
        'artifact_platform': 'mac',
    },
    'mac10_7_64': {
        'arch': 'x86_64',
        'platform': 'mac',
        'os': 'mac-10.7',
        'extension': 'dmg',
        'artifact_platform': 'mac',
    },
    'mac10_8': {
        'arch': 'x86_64',
        'platform': 'mac',
        'os': 'mac-10.8',
        'extension': 'dmg',
        'artifact_platform': 'mac',
    },
    'mac10_9': {
        'arch': 'x86_64',
        'platform': 'mac',
        'os': 'mac-10.9',
        'extension': 'dmg',
        'artifact_platform': 'mac',
    },
    'win32': {
        'arch': 'i686',
        'platform': 'win32',
        'os': 'win8-32',
        'extension': 'zip',
        'artifact_platform': 'win32',
    },
    'win32_64': {
        'arch': 'i686',
        'platform': 'win32',
        'os': 'win8-64',
        'extension': 'zip',
        'artifact_platform': 'win32',
    },
    'win7_32': {
        'arch': 'i686',
        'platform': 'win32',
        'os': 'win7-32',
        'extension': 'zip',
        'artifact_platform': 'win32',
    },
    'win7_32_64': {
        'arch': 'i686',
        'platform': 'win32',
        'os': 'win7-64',
        'extension': 'zip',
        'artifact_platform': 'win32',
    },
    'win7_64': {
        'arch': 'x86_64',
        'platform': 'win64',
        'os': 'win7-64',
        'extension': 'zip',
        'artifact_platform': 'win64',
    },
    'winxp_32': {
        'arch': 'i686',
        'platform': 'win32',
        'os': 'winxp-32',
        'extension': 'zip',
        'artifact_platform': 'win32',
    },
    'win64': {
        'arch': 'x86_64',
        'platform': 'win64',
        'os': 'win8-64',
        'extension': 'zip',
        'artifact_platform': 'win64',
    },
}


class GenerateWebRTCJobs(JobGenerator):
    def __init__(self, argv):
        super(GenerateWebRTCJobs, self).__init__(argv)
        self.REGEXPS = {
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
            'slave': r'XXSLAVEXX',
            'sigserver': r'XXXSIGSERVERXXX',
            'tests_release': r'XXXTESTSRELEASEXXX',
            'os1': r'XXOS1XX',
            'os2': r'XXOS2XX',
        }

    def process_row(self, row, template):
        jobname = 'webrtc-%s-%s' % (row['Release1'], row['PlatformJobLabel1'])
        if row['Release1'] != row['Release2']:
            jobname = '%s-%s' % (jobname, row['Release2'])
        jobname = '%s-%s' % (jobname, row['PlatformJobLabel2'])
        if row['Networking']:
            jobname = '%s-%s' % (jobname, row['Networking'])

        print 'jobname = %s' % jobname

        tests_release = self.get_lowest_release(row['Release1'], row['Release2'])

        if tests_release == 'beta':
            triggers = ''
        else:
            triggers = 'trigger-firefox-%s-%s' % (row['Release1'], row['Platform1'])
            if row['Release1'] != row['Release2'] or row['Platform1'] != row['Platform2']:
                triggers = '%s,trigger-firefox-%s-%s' % (triggers, row['Release2'], row['Platform2'])

            expand = 'expand-tests-%s-linux64' % tests_release
            if row['Networking']:
                expand = '%s-network' % expand
            triggers = '%s,%s' % (triggers, expand)

        if row['Networking']:
            sigserver = "NETWORK_SIGNALLING_SERVER"
        else:
            sigserver = "SIGNALLING_SERVER"

        url1 = '%s/job/firefox-%s-%s/ws/releases' % (self.config['host'], row['Release1'], row['Platform1'])
        url2 = '%s/job/firefox-%s-%s/ws/releases' % (self.config['host'], row['Release2'], row['Platform2'])

        artifact_platform1 = platform_host_data[row['Platform1']]['artifact_platform']
        artifact_platform2 = platform_host_data[row['Platform2']]['artifact_platform']

        package1 = 'firefox-latest-%s.en-US.%s.%s' % (row['Release1'], artifact_platform1, platform_host_data[row['Platform1']]['extension'])
        package2 = 'firefox-latest-%s.en-US.%s.%s' % (row['Release2'], artifact_platform2, platform_host_data[row['Platform2']]['extension'])

        build_file1 = 'firefox-latest-%s.en-US.%s.txt' % (row['Release1'], artifact_platform1)
        build_file2 = 'firefox-latest-%s.en-US.%s.txt' % (row['Release2'], artifact_platform2)

        template = re.sub(self.REGEXPS['triggers'], triggers, template)
        template = re.sub(self.REGEXPS['url1'], url1, template)
        template = re.sub(self.REGEXPS['url2'], url2, template)
        template = re.sub(self.REGEXPS['package1'], package1, template)
        template = re.sub(self.REGEXPS['package2'], package2, template)
        template = re.sub(self.REGEXPS['build_file1'], build_file1, template)
        template = re.sub(self.REGEXPS['build_file2'], build_file2, template)
        template = re.sub(self.REGEXPS['machine1'], row['Host1'], template)
        template = re.sub(self.REGEXPS['machine2'], row['Host2'], template)
        template = re.sub(self.REGEXPS['arch1'], row['Arch1'], template)
        template = re.sub(self.REGEXPS['arch2'], row['Arch2'], template)
        template = re.sub(self.REGEXPS['slave'], row['Slave'], template)
        template = re.sub(self.REGEXPS['sigserver'], sigserver, template)
        template = re.sub(self.REGEXPS['tests_release'], tests_release, template)
        template = re.sub(self.REGEXPS['os1'], platform_host_data[row['Platform1']]['os'], template)
        template = re.sub(self.REGEXPS['os2'], platform_host_data[row['Platform2']]['os'], template)

        return jobname, template

def generate_jobs(argv):
    generator = GenerateWebRTCJobs(argv)
    return generator.generate()

if __name__ == '__main__':
    result = generate_jobs(sys.argv[1:])
    if result == 0:
        os._exit(0)
    else:
        sys.exit(1)
