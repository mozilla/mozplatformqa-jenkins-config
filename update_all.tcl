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
    if {[regsub -all {<hudson.plugins.emailext.plugins.recipients.DevelopersRecipientProvider/>[\s]*<hudson.plugins.emailext.plugins.recipients.[Ll]istRecipientProvider/>} $newcontents <hudson.plugins.emailext.plugins.recipients.ListRecipientProvider/> newcontents]} {
        puts -nonewline "two recipients..."
    }
    if {[regsub {<hudson.plugins.emailext.plugins.recipients.DevelopersRecipientProvider/>} $newcontents <hudson.plugins.emailext.plugins.recipients.ListRecipientProvider/> newcontents]} {
        puts -nonewline "one recipient..."
    }
    if {![string equal $contents $newcontents]} {
        set fd [open $file w]
        puts -nonewline $fd $newcontents
        puts -nonewline "Replaced..."
        close $fd
    }

    puts "done"
}