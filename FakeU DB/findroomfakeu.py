import csv
import sys
import os
import fnmatch
import ntpath
import psycopg2
# this function actually knows argv is blank, relative path, abs path and
# returns the absdir magically


expandterm = '200103'
expandcid = '93007'
expandstudent = 5

# expandterm = sys.argv[1]
# expandcid = sys.argv[2]
# expandstudent = sys.argv[3]


#we need to find each room's capacity first.
conn = psycopg2.connect(database="FakeUData")
print 'connect successful'
cursor=conn.cursor()


cursor.execute('''\
    WITH R1 AS(\
        SELECT meeting.term as term1, meeting.summer as summer1, meeting.cid as cid1, \
                courses.term as term2, courses.summer as summer2, courses.cid as cid2,\
                build,room,days,time,subj,crse \
        FROM Meeting, Courses \
        WHERE meeting.term = courses.term and meeting.summer = courses.summer and \
                meeting.cid = courses.cid )\
        \
        SELECT term1,summer1,cid1,build,room,days,time,subj,crse \
        FROM R1 ''')


allinfo = cursor.fetchall()

cursor.execute('''\
    WITH R1 AS (\
        SELECT meeting.term as term1, meeting.summer as summer1, meeting.cid as cid1, \
                courses.term as term2, courses.summer as summer2, courses.cid as cid2,\
                build,room,days,time,subj,crse \
        FROM Meeting, Courses \
        WHERE meeting.term = courses.term and meeting.summer = courses.summer and \
                meeting.cid = courses.cid), \
    \
    R2 AS ( \
        SELECT term,summer,cid,build,room, cast(MAX(seat) as integer) as peoplepresent,subj,crse,days,time \
        FROM R1,Take \
        WHERE term1 = term and summer1 = summer and cid1 = cid \
        GROUP BY term,summer,cid,build,room,subj,crse,days,time),\
    \
    R4 AS (\
        SELECT  R2.TERM AS TERM1, R2.SUMMER AS SUMMER1, R2.BUILD AS BUILD1,\
                R2.ROOM AS ROOM1, R2.DAYS AS DAYS1, R2.TIME AS TIMES1, \
                SUM(R2.peoplepresent) AS lecturepeople \
        FROM  R2, R2 R3\
        WHERE R2.TERM = R3.TERM AND R2.SUMMER = R3.SUMMER AND R2.CID != R3.CID AND \
                R2.BUILD = R3.BUILD AND R2.ROOM = R3.ROOM and R2.TIME = R3.TIME  \
                AND R2.DAYS = R3.DAYS \
        GROUP BY R2.TERM, R2.SUMMER, R2.BUILD, R2.ROOM, R2.DAYS, R2.TIME ),\
    \
    \
    R5 AS(\
        SELECT BUILD1,ROOM1,cast(MAX(lecturepeople) as integer) AS CAPACITY \
        FROM R4 \
        GROUP BY BUILD1,ROOM1 ),\
    \
    NEWMEETING AS(\
        SELECT TERM,SUMMER,ROOM,CID,TIME,DAYS,TYPE,BUILD,instructors,CAPACITY\
        FROM MEETING,R5\
        WHERE BUILD1 = BUILD AND ROOM1 = ROOM),\
    \
    R6 AS(\
        SELECT CAST(MAX(SEAT) AS INTEGER) AS CURRENTSTUDENT,COURSES.TERM AS TERM1, COURSES.SUMMER AS SUMMER1, COURSES.CID AS CID1\
        FROM Courses,Take\
        WHERE COURSES.CID = TAKE.CID AND COURSES.TERM = TAKE.TERM AND COURSES.SUMMER = TAKE.SUMMER \
        GROUP BY COURSES.TERM, COURSES.SUMMER, COURSES.CID )\
    \
        SELECT TERM,SUMMER,CID,BUILD,ROOM,DAYS,TIME,CAPACITY,CURRENTSTUDENT\
        FROM R6, NEWMEETING\
        WHERE TERM1 = TERM AND SUMMER1 = SUMMER AND CID1 = CID ''')


summercount = 0
chosenlist = []
allinfo= cursor.fetchall()
print 'length of allinfo is: ' + str(len(allinfo))
for allinforow in allinfo:
    if allinforow[0] == expandterm and allinforow[2] == expandcid:
        print("there is such a course, and we will figure out the expansion process")
        summercount += 1
        chosenlist.append(allinforow)
        if summercount == 2:

            break
    else:
        continue
summer = 0
if summercount > 1:
    summer = raw_input('you are entering a possible summer course, specify it. Enter 1 as summer 1, enter 2 as summer 2: ')

if summer == 2:
    therow = chosenlist[1]
else:
    therow = chosenlist[0]

if therow[8] + expandstudent <= therow[7]:
    print "you don't need to change the classroom location. It can hold you all"

else:
    print "I'm sorry I couldn't find the classroom for you although I am pretty sure you will need an expansion"
















        # for l in range(i,j):
        #
        #
        #
        #
        #
        #
        # if j != i + 1 :
        #     instructorslist = []
        #     typelist = []
        #     dayslist = []
        #     timelist = []
        #     buildlist = []
        #     roomlist = []
        #
        #     #k is used to read every valid instructor line
        #     #if what it reads is empty string, it should be treated as null
        #     #not an empty line
        #     k = i
        #     while k < j:
        #         instructors = listreader[k+1][0]
        #         if instructors = '':
        #             if k = i:
        #                 instructors = ''
        #                 type = nextrow[1]
        #                 days = nextrow[2]
        #                 time = nextrow[3]
        #                 build = nextrow[4]
        #                 room = nextrow[5]
        #         instructorlist.append(instructors)
