#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import jenkins
import os
import sys


parser = argparse.ArgumentParser(description='Save jobs from a jenkins instance.')
parser.add_argument('--regexp')
parser.add_argument('--jenkins-host', required=True, dest='host')
args = parser.parse_args(sys.argv[1:])

print "Saving configs for %s" % args.host

jenkins_instance = jenkins.Jenkins(args.host)
if args.regexp:
    jobs = jenkins_instance.get_job_info_regex(args.regexp)
else:
    jobs = jenkins_instance.get_jobs()

if not os.path.exists('jobs'):
    os.makedirs('jobs')


for job in jobs:
    print 'Saving %s...' % job['name']
    config = jenkins_instance.get_job_config(job['name'])

    dir = os.path.join('jobs', job['name'])
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Write it out
    config_path = os.path.join('jobs', job['name'], 'config.xml')
    config_file = open(config_path, 'w')
    config_file.write(config)
    config_file.close()

print 'Done.'


