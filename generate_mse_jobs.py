#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Generate jobs for jenkins based on a .csv file describing the parameters."""

import os
import re
import sys

from job_generator import JobGenerator

class GenerateMSEJobs(JobGenerator):
    def __init__(self, argv):
        super(GenerateMSEJobs, self).__init__(argv)
        self.REGEXPS = {
            'url1': r'XXURL1XX',
            'package': r'XXPACKAGEXX',
            'url2': r'XXURL2XX',
            'common_tests': r'XXCOMMONTESTSXX',
            'web_platform_tests': r'XXWEBPLATFORMTESTSXX',
            'triggers': r'XXTRIGGERSXX',
            'expand': r'XXEXPANDXX',
            'slave': r'XXSLAVEXX',
            'platform': r'XXPLATFORMXX',
            'python': r'XXPYTHONXX',
            'bash': r'XXBASHXX',
        }

    def process_row(self, row, template):
        jobname = 'mse-web-platform-%s-%s' % (row['Release'], row['PlatformJobLabel'])

        print 'jobname = %s' % jobname

        if (row['Release'] != 'beta'):
            triggers = 'trigger-firefox-%s-%s,trigger-tests-%s-%s' % (row['Release'], row['Platform'], row['Release'], row['Platform'])
        else:
            triggers = ''

        url1 = '%s/job/firefox-%s-%s/ws/releases' % (self.config['host'], row['Release'], row['Platform'])
        url2 = '%s/job/tests-%s-%s/ws/releases' % (self.config['host'], row['Release'], row['Platform'])

        artifact_platform = self.get_artifact_platform(row['Platform'])

        package = 'firefox-latest-%s.en-US.%s.%s' % (row['Release'], artifact_platform, self.get_platform_extension(row['Platform']))
        common_tests = 'firefox-latest-%s.en-US.%s.common.tests.zip' % (row['Release'], artifact_platform)
        web_platform_tests = 'firefox-latest-%s.en-US.%s.web-platform.tests.zip' % (row['Release'], artifact_platform)

        template = re.sub(self.REGEXPS['triggers'], triggers, template)
        template = re.sub(self.REGEXPS['url1'], url1, template)
        template = re.sub(self.REGEXPS['url2'], url2, template)
        template = re.sub(self.REGEXPS['package'], package, template)
        template = re.sub(self.REGEXPS['common_tests'], common_tests, template)
        template = re.sub(self.REGEXPS['web_platform_tests'], web_platform_tests, template)
        template = re.sub(self.REGEXPS['slave'], row['Slave'], template)
        template = re.sub(self.REGEXPS['platform'], row['Platform'], template)
        template = re.sub(self.REGEXPS['python'], row['Python'], template)
        template = re.sub(self.REGEXPS['bash'], row['Bash'], template)

        return jobname, template

def generate_jobs(argv):
    generator = GenerateMSEJobs(argv)
    return generator.generate()

if __name__ == '__main__':
    result = generate_jobs(sys.argv[1:])
    if result == 0:
        os._exit(0)
    else:
        sys.exit(1)
