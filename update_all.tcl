#!/usr/bin/tclsh

set fd [open email.snippet]
set snippet [read $fd]
close $fd

set job_files [glob jobs/*/config.xml]

foreach file $job_files {
    puts -nonewline "Processing $file..."
    flush stdout
    set fd [open $file]
    set contents [read $fd]
    close $fd

    set newcontents $contents
    if {[regsub {(<hudson.tasks.Shell>[ \t\n]+<command>)(mkdir.*)(</command>\n[ \t]+</hudson.tasks.Shell>)} $newcontents {\1#!/bin/sh -x
\2 \&gt; steeplechase.out 2\&gt;\&amp;1
ret=$?
cat steeplechase.out
if [ $ret \&gt; 0 ]; then
    exit $ret
fi\3} newcontents]} {
        puts -nonewline "replaced"
    }

    if {![string equal $contents $newcontents]} {
        set fd [open $file w]
        puts -nonewline $fd $newcontents
        puts -nonewline "Replaced..."
        close $fd
    }

    puts "done"
}
