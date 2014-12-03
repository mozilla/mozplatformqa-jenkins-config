#!/usr/bin/tclsh

set files [glob jobs/*/config.xml]

foreach file $files {
    set fd [open $file]
    set contents [read $fd]
    close $fd

    if {[regexp {<disabled>true} $contents match]} {
	file delete $file
	puts "Removed $file."
    }
}


