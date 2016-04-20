#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import jenkins
import re
import sys

parser = argparse.ArgumentParser(description='Copy jobs from one Jenkins instance to another')
parser.add_argument('--regexp', required=True)
parser.add_argument('--jenkins-src-host', required=True, dest='srchost')
parser.add_argument('--jenkins-dest-host', required=True, dest='desthost')

args = parser.parse_args(sys.argv[1:])

pattern = re.compile(args.srchost)
src_jenkins_instance = jenkins.Jenkins(args.srchost)
dest_jenkins_instance = jenkins.Jenkins(args.desthost)
jobs = src_jenkins_instance.get_job_info_regex(args.regexp)
for job in jobs:
    name = job['name']
    config_xml = src_jenkins_instance.get_job_config(name)
    new_config = re.sub(pattern, args.desthost, config_xml)

    if config_xml == new_config:
        print 'Skipping %s...' % name
    else:
        if dest_jenkins_instance.job_exists(name):
            print 'Updating %s...' % name
            dest_jenkins_instance.reconfig_job(name, new_config)
        else:
            print 'Creating %s...' % name
            dest_jenkins_instance.create_job(name, new_config)
        dest_jenkins_instance.disable_job(name)

print 'Done.'


