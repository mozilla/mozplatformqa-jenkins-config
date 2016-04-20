#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import jenkins
import re
import sys

parser = argparse.ArgumentParser(description='Create/update jobs in a jenkins instance based on one release but using another')
parser.add_argument('--project-regexp', required=True)
parser.add_argument('--jenkins-host', required=True, dest='host')
parser.add_argument('--src-release', required=True, dest='srcrelease')
parser.add_argument('--dest-release', required=True, dest='destrelease')

args = parser.parse_args(sys.argv[1:])

pattern = re.compile(args.project_regexp)
jenkins_instance = jenkins.Jenkins(args.host)
jobs = jenkins_instance.get_job_info_regex(pattern)

pattern = re.compile(args.srcrelease)
mozharness_pattern = re.compile("mozharness-%s" % args.destrelease)

for job in jobs:
    name = job['name']
    config_xml = jenkins_instance.get_job_config(name)
    newname = re.sub(pattern, args.destrelease, name)
    new_config = re.sub(pattern, args.destrelease, config_xml)
    new_config = re.sub(mozharness_pattern, "mozharness-nightly", new_config)

    if jenkins_instance.job_exists(newname):
        print 'Updating %s...' % newname
        jenkins_instance.reconfig_job(newname, new_config)
    else:
        print 'Creating %s...' % newname
        jenkins_instance.create_job(newname, new_config)
    jenkins_instance.disable_job(newname)

print 'Done.'


