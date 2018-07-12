import os
import psycopg2

conn = psycopg2.connect(database="FakeUData")
print "Opened database successfully"

cur = conn.cursor()

cur.execute("SELECT SU, cast(SN as float)/cast(TOTAL as float)\
             FROM\
             (SELECT SU,COUNT(SID) AS SN\
              FROM(SELECT TERM,SID,SUM(UNITS) AS SU\
                   FROM Take\
                   GROUP BY TERM,SID)A\
              Where SU in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20) \
              GROUP BY A.SU)B\
              ,\
              (SELECT COUNT(*) AS Total\
               FROM (SELECT DISTINCT SID,TERM\
                     FROM Take) C\
               ) D\
               order by SU\
               ;")
rows = cur.fetchall()
print 'result for 3a: '
for row in rows:
   print 'unit is: ' + str(row[0]) + ', percentage is: ' + str(row[1]*100)[:4] +'%'
print '=============================='
print '=============================='

cur.execute('''(SELECT instructors, SGrade \
             From  \
             \
            (SELECT AVG(NGRADE) as SGrade, instructors \
             FROM \
                  (SELECT instructors, Meeting.CID as CID, Meeting.TERM as TERM, Meeting.SUMMER as SUMMER \
                   FROM Meeting,Courses\
                   WHERE Meeting.CID= Courses.CID AND\
                         Meeting.SUMMER=Courses.SUMMER AND\
                         Meeting.TERM=Courses.TERM) A\
                ,  \
                  (SELECT NGRADE, TERM, CID, SUMMER\
                   FROM Take \
                   WHERE NGRADE > -1) Take2\
                   \
             WHERE Take2.TERM = A.TERM AND\
                   Take2.CID = A.CID  AND\
                   Take2.SUMMER = A.SUMMER\
             Group by A.instructors) C \
            \
            Where SGrade in (\
                \
                SELECT MAX(SGrade) as SGrade\
                From (\
                    SELECT AVG(NGRADE) as SGrade, instructors \
                    FROM    (SELECT instructors, Meeting.CID as CID, Meeting.TERM as TERM, Meeting.SUMMER as SUMMER \
                             FROM Meeting,Courses\
                             WHERE   Meeting.CID= Courses.CID AND\
                                     Meeting.SUMMER=Courses.SUMMER AND\
                                     Meeting.TERM=Courses.TERM) A\
                                    ,  \
                            (SELECT NGRADE, TERM, CID, SUMMER\
                             FROM Take \
                             Where NGRADE > -1) Take1\
                    WHERE Take1.TERM = A.TERM AND\
                          Take1.CID = A.CID  AND\
                          Take1.SUMMER = A.SUMMER\
                    group by A.instructors) B  ))\
                    \
            union \
            \
            (SELECT instructors, SGrade \
                         From  \
                         \
                        (SELECT AVG(NGRADE) as SGrade, instructors \
                         FROM \
                              (SELECT instructors, Meeting.CID as CID, Meeting.TERM as TERM, Meeting.SUMMER as SUMMER \
                               FROM Meeting,Courses\
                               WHERE Meeting.CID= Courses.CID AND\
                                     Meeting.SUMMER=Courses.SUMMER AND\
                                     Meeting.TERM=Courses.TERM) A\
                            ,  \
                              (SELECT NGRADE, TERM, CID, SUMMER\
                               FROM Take \
                               WHERE NGRADE > -1) Take2\
                               \
                         WHERE Take2.TERM = A.TERM AND\
                               Take2.CID = A.CID  AND\
                               Take2.SUMMER = A.SUMMER\
                         Group by A.instructors) C \
                        \
                        Where SGrade in (\
                            \
                            SELECT MIN(SGrade) as SGrade\
                            From (\
                                SELECT AVG(NGRADE) as SGrade, instructors \
                                FROM    (SELECT instructors, Meeting.CID as CID, Meeting.TERM as TERM, Meeting.SUMMER as SUMMER \
                                         FROM Meeting,Courses\
                                         WHERE   Meeting.CID= Courses.CID AND\
                                                 Meeting.SUMMER=Courses.SUMMER AND\
                                                 Meeting.TERM=Courses.TERM) A\
                                                ,  \
                                        (SELECT NGRADE, TERM, CID, SUMMER\
                                         FROM Take \
                                         Where NGRADE > -1) Take1\
                                WHERE Take1.TERM = A.TERM AND\
                                      Take1.CID = A.CID  AND\
                                      Take1.SUMMER = A.SUMMER\
                                group by A.instructors) B  ))\
            ''')
rows = cur.fetchall()
print 'result for 3b(easiest and hardest:):'
for row in rows:
       print 'professor is: ' + row[0] + ' and the gpa is: ' + str(row[1])
print '=============================='
print '=============================='

cur.execute(" SELECT SU,SUM(SG)/SUM(SU) AS GPA From \
              (SELECT SID,SU,SG FROM \
              (SELECT SID, SUM(UNITS) as SU, SUM(SG) as SG \
                   FROM (SELECT UNITS*NGrade as SG, TERM, SID, UNITS FROM TAKE WHERE NGrade >=0) C   \
                   GROUP BY SID) A \
               Where SU <= 20 and SU >= 1) B \
              GROUP BY SU \
              ORDER BY SU   \
")
rows = cur.fetchall()
print 'result for 3c:'
for row in rows:
   print 'unit is: ' + str(row[0]) + ', average gpa is: ' + str(row[1])[0:5]
print '=============================='
print '=============================='

cur.execute('''SELECT SUBJ,CRSE,n\
              FROM  ( \
     SELECT cast(P/T as float) as n, C.CRSE as CRSE, C.SUBJ as SUBJ From \
             (SELECT cast(COUNT(SID) as float) as P, CRSE,SUBJ FROM\
                (SELECT Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER, Take.SID as SID, CRSE as CRSE, SUBJ as SUBJ\
                 FROM Take, Courses \
                 WHERE Grade not in ('F','NF','NS','U','NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
                 AND Take.TERM = Courses.TERM \
                 AND Take.CID  = Courses.CID \
                 AND Take.SUMMER= Courses.SUMMER \
                ) A \
              Group by CRSE,SUBJ) C\
              ,  \
             (SELECT cast(COUNT(SID) as float) as T, CRSE, SUBJ \
              FROM Take, Courses \
              Where Take.CID = Courses.CID \
              AND Take.TERM= Courses.TERM \
              AND Take.SUMMER= Courses.SUMMER\
              and Take.grade not in ('NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
              GROUP BY CRSE,SUBJ) B \
             WHERE C.CRSE=B.CRSE\
             and C.SUBJ = B.SUBJ\
             ) as E\
             Where n in \
             (SELECT max(n) FROM ( \
             SELECT cast(P/T as float) as n, C.CRSE , C.SUBJ From \
             (SELECT cast(COUNT(SID) as float) as P, CRSE, SUBJ FROM\
                (SELECT Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER, Take.SID as SID, Courses.CRSE as CRSE, Courses.SUBJ as SUBJ\
                 FROM Take, Courses \
                 WHERE Grade not in ('F','NF','NS','U','NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
                 AND Take.TERM = Courses.TERM \
                 AND Take.CID  = Courses.CID \
                 AND Take.SUMMER= Courses.SUMMER \
                ) A \
              Group by CRSE, SUBJ) C\
              ,  \
             (SELECT cast(COUNT(SID) as float) as T, CRSE, SUBJ \
              FROM Take, Courses \
              Where Take.CID = Courses.CID \
              AND Take.TERM= Courses.TERM \
              AND Take.SUMMER= Courses.SUMMER \
              and Take.grade not in ('NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
              GROUP BY CRSE, SUBJ) B \
             WHERE C.CRSE=B.CRSE\
             and C.SUBJ=B.SUBJ\
             ) as D) \
             order by subj,crse \
             ''')
rows = cur.fetchall()
print 'result for 3d(highest):'
for row in rows:
   print ' '+ row[0] + row[1] + ' '+ str(row[2]*100)[:5] +'\%, '
cur.execute(" SELECT SUBJ,CRSE,n\
              FROM  ( \
     SELECT cast(P/T as float) as n, C.CRSE as CRSE, C.SUBJ as SUBJ From \
             (SELECT cast(COUNT(SID) as float) as P, CRSE,SUBJ FROM\
                (SELECT Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER, Take.SID as SID, CRSE as CRSE, SUBJ as SUBJ\
                 FROM Take, Courses \
                 WHERE Grade not in ('F','NF','NS','U','NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
                 AND Take.TERM = Courses.TERM \
                 AND Take.CID  = Courses.CID \
                 AND Take.SUMMER= Courses.SUMMER \
                ) A \
              Group by CRSE,SUBJ) C\
              ,  \
             (SELECT cast(COUNT(SID) as float) as T, CRSE, SUBJ \
              FROM Take, Courses \
              Where Take.CID = Courses.CID \
              AND Take.TERM= Courses.TERM \
              AND Take.SUMMER= Courses.SUMMER\
              and Take.grade not in ('NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
              GROUP BY CRSE,SUBJ) B \
             WHERE C.CRSE=B.CRSE\
             and C.SUBJ = B.SUBJ\
             ) as E\
             Where n in \
             (SELECT min(n) FROM ( \
             SELECT cast(P/T as float) as n, C.CRSE , C.SUBJ From \
             (SELECT cast(COUNT(SID) as float) as P, CRSE, SUBJ FROM\
                (SELECT Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER, Take.SID as SID, Courses.CRSE as CRSE, Courses.SUBJ as SUBJ\
                 FROM Take, Courses \
                 WHERE Grade not in ('F','NF','NS','U','NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
                 AND Take.TERM = Courses.TERM \
                 AND Take.CID  = Courses.CID \
                 AND Take.SUMMER= Courses.SUMMER \
                ) A \
              Group by CRSE, SUBJ) C\
              ,  \
             (SELECT cast(COUNT(SID) as float) as T, CRSE, SUBJ \
              FROM Take, Courses \
              Where Take.CID = Courses.CID \
              AND Take.TERM= Courses.TERM \
              AND Take.SUMMER= Courses.SUMMER \
              and Take.grade not in ('NG','I','Y','WD2','IP','WD1','W04','WI','WN','XR','W10','WD4','WDC') \
              GROUP BY CRSE, SUBJ) B \
             WHERE C.CRSE=B.CRSE\
             and C.SUBJ=B.SUBJ\
             ) as D) \
             order by subj,crse \
             ")
rows = cur.fetchall()
print 'result for 3d(lowest):'
for row in rows:
   print ' '+ row[0] + row[1] + ' '+ str(row[2]*100)[:5] +'\%, '
print '=============================='
print '=============================='

cur.execute('''\
    WITH R0 AS (\
        SELECT Meeting.term as term, meeting.summer as summer, meeting.cid as cid, subj,crse,time,days,INSTRUCTORS
        FROM Meeting,Courses
        WHERE meeting.term = Courses.term AND Meeting.summer = Courses.summer AND Meeting.cid = Courses.cid \
                AND time != '' AND DAYS != '' AND INSTRUCTORS != ''), \
    \
    R1 AS (\
        SELECT T1.TERM AS TERM1,T1.CID AS CID1, T1.TIME AS TIME1,T1.DAYS AS DAYS1,T1.INSTRUCTORS AS INSTRUCTORS1,T1.SUMMER AS SUMMER,\
                T2.TERM AS TERM2,T2.CID AS CID2, T2.TIME AS TIME2,T2.DAYS AS DAYS2,T2.INSTRUCTORS AS INSTRUCTORS2, \
                T1.SUBJ AS SUBJ1, T2.SUBJ AS SUBJ2, T1.CRSE AS CRSE1, T2.CRSE AS CRSE2 \
        FROM R0 T1, R0 T2 \
        WHERE T1.TERM=T2.TERM AND T1.CID != T2.CID AND T1.TIME=T2.TIME AND T1.DAYS=T2.DAYS AND T1.INSTRUCTORS=T2.INSTRUCTORS\
                AND T1.SUMMER = T2.SUMMER AND T1.subj != T2.SUBJ ),\
    \
    R2 AS (\
        SELECT DISTINCT ON(SUBJ1,CRSE1,SUBJ2,CRSE2) SUBJ1,CRSE1,SUBJ2,CRSE2,TERM1 \
        FROM R1\
        ORDER BY SUBJ1,CRSE1 )\
    \
    SELECT *
    FROM R2
    ORDER BY TERM1


            ''')
rows = cur.fetchall()
print 'result for 3e:'
for row in rows:
       print row[0] + row[1] + ' is cross listed with '+ row[2] + row[3]
print '=============================='
print '=============================='

cur.execute("SELECT GPA, MAJOR\
             FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='ABC' \
                    and NGrade >=0 ) D\
                    Group by MAJOR) F\
             where GPA in (SELECT Max(GPA) FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='ABC' \
                    and NGrade >=0 ) G\
                   \
            Group by MAJOR) B )\
             ")
rows = cur.fetchall()
print 'result for 3f'
print 'perform the best on average in ABC courses: '
for row in rows:
       print 'major is: ' + row[1] + ' and its average gpa is: ' + str(row[0])[0:5]
print '=============================='
cur.execute("SELECT GPA, MAJOR\
             FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='ABC' \
                    and NGrade >=0 ) D\
                    Group by MAJOR) F\
             where GPA in (SELECT min(GPA) FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='ABC' \
                    and NGrade >=0 ) G\
                   \
            Group by MAJOR) B )\
             ")
rows = cur.fetchall()
print 'result for 3f'
print 'perform the worst on average in ABC courses: '
for row in rows:
       print 'major is: ' + row[1] + ' and its average gpa is: ' + str(row[0])[0:5]
print '=============================='

cur.execute("SELECT GPA, MAJOR\
             FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='DEF' \
                    and NGrade >=0 ) D\
                    Group by MAJOR) F\
             where GPA in (SELECT Max(GPA) FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='ABC' \
                    and NGrade >=0 ) G\
                   \
            Group by MAJOR) B )\
             ")
rows = cur.fetchall()
print 'result for 3f'
print 'perform the best on average in DEF courses: '
for row in rows:
       print 'major is: ' + row[1] + ' and its average gpa is: ' + str(row[0])[0:5]
print '=============================='
cur.execute("SELECT GPA, MAJOR\
             FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='DEF' \
                    and NGrade >=0 ) D\
                    Group by MAJOR) F\
             where GPA in (SELECT min(GPA) FROM (SELECT MAJOR,SUM(N)/SUM(UNITS) as GPA \
             FROM  (SELECT take.UNITS, take.UNITS * take.NGrade as N, MAJOR, Take.CID as CID, Take.TERM as TERM, Take.SUMMER as SUMMER\
                    FROM Courses,Take\
                    Where Courses.CID=Take.CID\
                    and Courses.TERM = Take.TERM\
                    and Courses.SUMMER=Take.SUMMER\
                    and SUBJ='ABC' \
                    and NGrade >=0 ) G\
                   \
            Group by MAJOR) B )\
             ")
rows = cur.fetchall()
print 'result for 3f'
print 'perform the worst on average in DEF courses: '
for row in rows:
       print 'major is: ' + row[1] + ' and its average gpa is: ' + str(row[0])[0:5]
print '=============================='
print '=============================='

cur.execute("\
   SELECT * FROM (\
   SELECT E.Major, cast(n/c as float) as per FROM \
   (SELECT * FROM\
   (SELECT n, MAJOR FROM\
   (SELECT cast(Count(SID) as float) as n, MAJOR FROM\
   (SELECT DISTINCT SID,MAJOR FROM (\
   SELECT TERM1,TERM2,SID,MAJOR FROM\
   (SELECT DISTINCT cast(T1.TERM as integer) as TERM1, cast(T2.TERM as integer) as TERM2, T1.SID as SID, T1.MAJOR as MAJOR \
   FROM Take T1, Take T2\
   WHERE T1.SID=T2.SID\
   and T1.MAJOR != T2.MAJOR\
   and T2.MAJOR like 'ABC%'  \
   and T1.MAJOR not in ('ABC','ABC1','ABCG','ABC2')\
   ) as A \
   where TERM1<TERM2\
   order by SID) B) C\
   GROUP by MAJOR) D\
   order by n desc) E\
   limit 5) E\
   ,\
   (SELECT cast(COUNT(SID) as float) AS C ,MAJOR FROM(\
   SELECT distinct SID,MAJOR\
   FROM Take\
   )B\
   Group by major) F\
   Where E.major=F.major) G\
   order by per desc\
   ")
rows = cur.fetchall()
print 'result for 3g:'
for row in rows:
       print 'major is: ' + row[0] + ' and percentage is: ' +str(row[1]*100)[:4] +'%'
print '=============================='
print '=============================='

cur = conn.cursor()
cur.execute("\
   SELECT * FROM (\
   SELECT E.Major, cast(n/c as float) as per FROM \
   (SELECT * FROM\
   (SELECT n, MAJOR FROM\
   (SELECT cast(Count(SID) as float) as n, MAJOR FROM\
   (SELECT DISTINCT SID,MAJOR FROM (\
   SELECT TERM1,TERM2,SID,MAJOR FROM\
   (SELECT DISTINCT cast(T1.TERM as integer) as TERM1, cast(T2.TERM as integer) as TERM2, T1.SID as SID, T2.MAJOR as MAJOR \
   FROM Take T1, Take T2\
   WHERE T1.SID=T2.SID\
   and T1.MAJOR != T2.MAJOR\
   and T1.MAJOR like 'ABC%'  \
   and T2.MAJOR not in ('ABC','ABC1','ABCG','ABC2')\
   ) as A \
   where TERM1<TERM2\
   order by SID) B) C\
   GROUP by MAJOR) D\
   order by n desc) E\
   limit 5) E\
   ,\
   (SELECT cast(COUNT(SID) as float) AS C ,MAJOR FROM(\
   SELECT distinct SID,MAJOR\
   FROM Take\
   )B\
   Group by major) F\
   Where E.major=F.major) G\
   order by per desc")
rows = cur.fetchall()
print 'result for 3h:'
for row in rows:
       print 'major is: ' + row[0] + ' and percentage is: ' +str(row[1]*100)[:4] +'%'
print '=============================='
print '=============================='


conn.close()
