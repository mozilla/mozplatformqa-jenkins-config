#!/usr/bin/tclsh

set job_files [glob jobs/webrtc-*nightly*/config.xml jobs/webrtc-*aurora*/config.xml]

foreach file $job_files {
    if {[string match {*beta*} $file]} {
	puts "Skipping $file..."
	continue
    }
    puts -nonewline "Processing $file..."
    flush stdout
    set fd [open $file]
    set contents [read $fd]
    close $fd

    set newcontents $contents
    if {[regsub -all {<disabled>true</disabled>} $newcontents <disabled>false</disabled> newcontents]} {
        puts -nonewline "enabled..."
    }
    if {![string equal $contents $newcontents]} {
        set fd [open $file w]
        puts -nonewline $fd $newcontents
        puts -nonewline "Replaced..."
        close $fd
    }

    puts "done"
}
