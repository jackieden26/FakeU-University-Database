import os
import psycopg2

conn = psycopg2.connect(database="FakeUData")
print "Opened database successfully"

cur = conn.cursor()
cur.execute('''\
    WITH R0 AS (\
         SELECT cast(Take.TERM as integer) as TERM, Take.SID as SID, Take.CID as CID, Take.SUMMER as SUMMER, CRSE, SUBJ\
         From Take, Courses\
         where  Take.CID = Courses.CID\
         and Take.TERM=Courses.TERM\
         and Take.SUMMER=Courses.SUMMER\
         ),\
         \
         R1 AS (\
         SELECT DISTINCT SID, TERM1, TERM2, CRSE1, CRSE2, SUBJ1, SUBJ2 \
         FROM( \
         SELECT a1.SID as SID, a1.CID as CID1, a2.CID as CID2, a1.TERM as TERM1, a2.TERM as TERM2, a1.CRSE as CRSE1, a2.CRSE as CRSE2, a1.SUBJ as SUBJ1, a2.SUBJ as SUBJ2  \
         From R0 a1, R0 a2 \
         where a1.SID = a2.SID\
         and a1.CRSE != a2.CRSE\
         and a1.TERM < a2.TERM\
         and a2.SUBJ = 'ABC'\
         and a2.CRSE in ('20
         3','210','222')) A ),\
         \
         R2 AS (\
         SELECT cast(Count(SID) as float) as n, CRSE1,SUBJ1,CRSE2,SUBJ2 \
         FROM R1\
         Group by SUBJ1,CRSE1,SUBJ2,CRSE2\
         ),\
         \
         R3 AS (\
         SELECT cast(Count(SID) as float) as T, CRSE, SUBJ\
         From R0\
         Where CRSE in ('203','210','222')\
         and SUBJ = 'ABC'\
         Group by SUBJ,CRSE),\
         \
         R4 AS(\
         SELECT cast(n/t as float) as per, CRSE1,SUBJ1, R2.CRSE2 as CRSE2, R2.SUBJ2 as SUBJ2\
         FROM R2,R3\
         where\
         R2.CRSE2=R3.CRSE\
         and R2.SUBJ1=R3.SUBJ\
         order by CRSE2),\
         \
         R5 as (\
         SELECT per,CRSE1,SUBJ1,CRSE2,SUBJ2 \
         FROM R4\
         where per >= 0.5)\
         \
    SELECT * FROM R5\
             ''')
rows = cur.fetchall()
print 'result for 5a'
print '50%~55%:'
for row in rows:
    if row[0]>0.5 and row[0]<=0.55:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'

print '55%~60%:'
for row in rows:
    if row[0]>0.55 and row[0]<=0.6:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '60%~65%:'
for row in rows:
    if row[0]>0.6 and row[0]<=0.65:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '65%~70%:'
for row in rows:
    if row[0]>0.65 and row[0]<=0.70:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '70%~75%:'
for row in rows:
    if row[0]>0.7 and row[0]<=0.75:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '75%~80%:'
for row in rows:
    if row[0]>0.75 and row[0]<=0.80:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '80%~85%:'
for row in rows:
    if row[0]>0.80 and row[0]<=0.85:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '85%~90%:'
for row in rows:
    if row[0]>0.85 and row[0]<=0.90:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '90%~95%:'
for row in rows:
    if row[0]>0.9 and row[0]<=0.95:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
print '\n'
print '95%~100%:'
for row in rows:
    if row[0]>0.95 and row[0]<=1.00:
       print  str(row[0]*100)[:5]+ '\\%' + ' of the students have taken '+row [1] + row[2] + ' before taking '+ row[3] + row[4]
conn.close()
