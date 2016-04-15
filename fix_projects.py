#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import jenkins
import re
import sys

parser = argparse.ArgumentParser(description='Enable jobs in a jenkins instance')
parser.add_argument('--regexp', required=True)
parser.add_argument('--config-re', required=True, dest='config_re')
parser.add_argument('--replacement', required=True)
parser.add_argument('--jenkins-host', required=True, dest='host')

args = parser.parse_args(sys.argv[1:])

pattern = re.compile(args.config_re)
jenkins_instance = jenkins.Jenkins(args.host)
jobs = jenkins_instance.get_job_info_regex(args.regexp)
for job in jobs:
    name = job['name']
    config_xml = jenkins_instance.get_job_config(name)
    new_config = re.sub(pattern, args.replacement, config_xml)

    if config_xml == new_config:
        print 'Skipping %s...' % name
    else:
        print 'Updating %s...' % name
        jenkins_instance.reconfig_job(name, new_config)

print 'Done.'


