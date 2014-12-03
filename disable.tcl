#!/usr/bin/tclsh

set job_files [glob jobs/nightly*/config.xml jobs/aurora*/config.xml]

foreach file $job_files {
    puts -nonewline "Processing $file..."
    flush stdout
    set fd [open $file]
    set contents [read $fd]
    close $fd

    set newcontents $contents
    if {[regsub -all {<disabled>false</disabled>} $newcontents <disabled>true</disabled> newcontents]} {
        puts -nonewline "disabled..."
    }
    if {![string equal $contents $newcontents]} {
        set fd [open $file w]
        puts -nonewline $fd $newcontents
        puts -nonewline "Replaced..."
        close $fd
    }

    puts "done"
}
