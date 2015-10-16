#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import jenkins
import sys

parser = argparse.ArgumentParser(description='Disable jobs in a jenkins instance')
parser.add_argument('--regexp', required=True)
parser.add_argument('--jenkins-host', required=True, dest='host')
args = parser.parse_args(sys.argv[1:])

jenkins_instance = jenkins.Jenkins(args.host)
jobs = jenkins_instance.get_job_info_regex(args.regexp)
for job in jobs:
    print 'Disabling %s...' % job['name']
    jenkins_instance.disable_job(job['name'])

print 'Done.'


