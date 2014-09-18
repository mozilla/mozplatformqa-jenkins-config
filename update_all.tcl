#!/usr/bin/tclsh

set job_files [glob jobs/*/config.xml]

foreach file $job_files {
    puts -nonewline "Processing $file..."
    flush stdout
    set fd [open $file]
    set contents [read $fd]
    close $fd

    if {[regsub {[ \t]*<hudson\.plugins\.girls\.CordellWalkerRecorder.*/hudson\.plugins\.girls\.CordellWalkerRecorder>\n} $contents {} newcontents]} {
        set fd [open $file w]
        puts $fd $newcontents
        puts -nonewline "\nReplaced..."
        close $fd
    }


    puts "done"

}