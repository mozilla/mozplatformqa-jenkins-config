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

    if {[regexp {ExtendedEmailPublisher} $contents match]} {
        puts -nonewline "already there..."
    } else {
        set newcontents $contents
        if {[regsub {(<publishers>.*)(\n[\s]*</publishers>)} $newcontents \\1\n$snippet\\2 newcontents]} {
            puts -nonewline "existing publishers..."
        }
        if {[regsub {<publishers/>} $newcontents "<publishers>\n$snippet\n  </publishers>" newcontents]} {
            puts -nonewline "blank publishers..."
        }
        if {![string equal $contents $newcontents]} {
            set fd [open $file w]
            puts -nonewline $fd $newcontents
            puts -nonewline "Replaced..."
            close $fd
        }
    }

    puts "done"
}