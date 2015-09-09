#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import jenkins
import os
import sys

from time import sleep


parser = argparse.ArgumentParser(description='Save jobs from a jenkins instance.')
parser.add_argument('--old-host', required=True, dest='old')
parser.add_argument('--new-host', required=True, dest='new')
parser.add_argument('--generate-files', action='store_true')
parser.add_argument('--regexp')

args = parser.parse_args(sys.argv[1:])

print 'Migrating from %s to %s...' % (args.old, args.new)

jenkins_instance = jenkins.Jenkins(args.new)

if args.regexp:
    jobs = jenkins_instance.get_job_info_regex(args.regexp)
else:
    jobs = jenkins_instance.get_jobs()

for job in jobs:
    config = jenkins_instance.get_job_config(job['name'])

    new_config = config.replace(args.old, args.new)

    if config != new_config:
        print 'Updating %s...' % job['name']
        if args.generate_files:
            if not os.path.exists('jobs'):
                os.makedirs('jobs')

            dir = os.path.join('jobs', job['name'])
            if not os.path.exists(dir):
                os.makedirs(dir)

            # Write it out
            config_path = os.path.join('jobs', job['name'], 'config.xml')
            config_file = open(config_path, 'w')
            config_file.write(new_config)
            config_file.close()
        else:
            # Tell Jenkins about it.
            if jenkins_instance.job_exists(job['name']):
                jenkins_instance.reconfig_job(job['name'], new_config)
            else:
                jenkins_instance.create_job(job['name'], new_config)
                # Inundating the jenkins server causes it to raise
                sleep(1)

print 'Done.'


