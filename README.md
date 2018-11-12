# nagios-avamar
Python script to check avamar for failures within X minutes. Output is in Nagios format. 

Usage.

Usage: check_ave.py -d DB -u USER -H HOST -P PORT -p PWD -M MINUTES

Options:
  -h, --help  show this help message and exit
  -d D        Avamar PG Database [default: mcdb]
  -u U        PG User [default: viewuser]
  -H H        Avamar Server [default: localhost]
  -P P        PG Port [default: 5555]
  -p P        PG Password [default: viewuser1]
  -M M        Minutes to query [default: 5 Minutes(s)]

