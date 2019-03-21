#!/usr/bin/python

__license__ = "GPL"
__maintainer__ = "Abel Laura"
__email__ = "abel.laura@gmail.com"

""" MODULE IMPORTS """
import psycopg2
import string
import datetime
import time
import optparse
import sys
import os
import getpass

""" NAGIOS API RETURN CODES """
nag_ret_dict = {'NagOk': 0,
                'NagWarn': 1,
                'NagCrit': 2,
                'NagUnknown': 3}

""" COMMAND LINE OPTION PARSING """
usage = "USAGE: %prog -d DB -u USER -H HOST -P PORT -p PWD -M MINUTES"
parser = optparse.OptionParser(usage=usage)
parser.add_option('-d', action="store", default="mcdb", help="Avamar PG Database [default: %default]", type="string")
parser.add_option('-u', action="store", default="viewuser", help="PG User [default: %default]", type="string")
parser.add_option('-H', action="store", default="localhost", help="Avamar Server [default: %default]", type="string")
parser.add_option('-P', action="store", default="5555", help="PG Port [default: %default]", type="string")
parser.add_option('-p', action="store", default="viewuser1", help="PG Password [default: %default]", type="string")
parser.add_option('-M', action="store", default="5", help="Minutes to query [default: %default Minutes(s)]", type="int")
options, args = parser.parse_args()

""" ARG COUNT CHECK """
if len(sys.argv[1:]) == 0:
    parser.print_help()
    sys.exit(nag_ret_dict['NagUnknown'])

""" TEST DATABASE CONNECTION """
try:
    conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s' port='%s'"\
    % (options.d, options.u, options.H, options.p, options.P))
except psycopg2.DatabaseError, e:
    print e
    sys.exit(nag_ret_dict['NagUnknown'])


""" GET FAILURES """
def count_failures_min():

    query1 = "SELECT count(*) FROM v_activities_2 "\
    "WHERE (completed_ts::timestamp at time zone 'UTC' > current_timestamp - interval '"+str(options.M)+" minutes') "\
    "and status_code!=30000 and status_code!=30005 and (v_activities_2.type like '%Backup%');"

    query2 = "SELECT count(*) FROM v_activities_2 "\
    "WHERE (completed_ts::timestamp at time zone 'UTC' > current_timestamp - interval '"+str(options.M)+" minutes') "\
    "and status_code = 30005 and (v_activities_2.type like '%Backup%');"
    f_list=""
    try:
        cur = conn.cursor()
        cur.execute(query1)
        row = cur.fetchone()
        count_f = row[0]
        cur.execute(query2)
        row = cur.fetchone()
        count_se = row[0]

        if count_f > 0:
            failq ="SELECT display_name, plugin_name FROM v_activities_2 "\
            "WHERE (completed_ts::timestamp at time zone 'UTC' > current_timestamp - interval '"+str(options.M)+" minutes') "\
            "and status_code!=30000 and status_code!=30005 and (v_activities_2.type like '%Backup%');"
            cur.execute(failq)
            for row in cur:
                f_list += row[0] +" "
        cur.close()
        conn.close()
        return count_f,count_se, f_list
    except psycopg2.DatabaseError, e:
        print ( 'Error %s' % e )
        parser.print_help()
        sys.exit(nag_ret_dict['NagUnknown'])


""" MAIN FUNCTION """
def main():
    fail_count, successwexception_count, failure_list  = count_failures_min()
    if fail_count == 0 and successwexception_count == 0:
        print("OK - No Failed Backups | failed=0, warning=0")
        sys.exit(nag_ret_dict['NagOk'])
    elif fail_count == 0 and successwexception_count > 0:
        print("WARN - %s Backup(s) reported Success w/Exception | failed=0, warning=%s") % (successwexception_count,successwexception_count)
        sys.exit(nag_ret_dict['NagWarn'])
    else:
        print("CRIT - %s Backup(s) reported Failures [ %s] | failed=%s, warning=%s") % (fail_count, failure_list, fail_count,successwexception_count)
        sys.exit(nag_ret_dict['NagCrit'])
if __name__ == "__main__":
    main()


