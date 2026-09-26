import sys,csv
for a in sys.argv[1:]:
    for row in csv.reader(open('idmaster_0908.tsv',encoding='utf-8'),delimiter='\t'):
        if len(row)>4 and row[4].strip()==a.strip('#'): print(' | '.join(row[:7]))
