import csv
import sys
import os
import fnmatch
import ntpath
import psycopg2
# this function actually knows argv is blank, relative path, abs path and
# returns the absdir magically
absdir = ''
if len(sys.argv) == 1:
    absdir = os.path.abspath('')
else:
    absdir = os.path.abspath(sys.argv[1])
l = []

for file in os.listdir(absdir):
    if fnmatch.fnmatch(file, '*.csv'):
        fullpathfile = os.path.join(absdir,file)
	l.append(fullpathfile)


conn = psycopg2.connect(database="FakeUData")
print 'connect successful'
cursor=conn.cursor()
cursor.execute('''
create table Courses(
CID varchar(20) ,
TERM varchar(20),
SUBJ varchar(20),
CRSE varchar(20),
SEC varchar(20),
UNITS varchar(20),
SUMMER integer,
primary key (CID,TERM,SUMMER)
);

create table Take(
SID varchar(20),
SUMMER integer,
CID varchar(20),
TERM varchar(20),
MAJOR varchar(20),
SEAT varchar(20),
CLASS varchar(20),
LEVEL varchar(20),
UNITS float,
GRADE varchar(20),
NGRADE float,
primary key (CID,TERM,SUMMER,SID)
);

create table Students(
SID varchar(20),
STATUS varchar(20),
PREFNAME varchar(50),
SURNAME varchar(50),
EMAIL varchar(50),
primary key(SID)
);

create table Meeting(
CID varchar(20),
TIME varchar(20),
BUILD varchar(20),
DAYS varchar(20),
INSTRUCTORS varchar(50),
TYPE varchar(30),
ROOM varchar(30),
TERM varchar(30),
SUMMER integer,
primary key (TYPE, TERM,SUMMER,CID,DAYS,TIME,ROOM),
foreign key (CID,TERM,SUMMER) references Courses(CID,TERM,SUMMER)
);
''')





#this is list of 4 relations tuples, tl = tuple list, ts = tuple strings
#each element is a tuple string
#it has to be outside big loop because they are relations, and I don't want
#them to duplicate
newstudentstl = []
newstudentsts = ''
studentstl = []
studentsts = ''
taketl = []
takets = ''
coursestl = []
coursests = ''
meetingtl = []
meetingts = ''
gradedic = {'A+':4.000,'A':4.000,'A-':3.700,'B+':3.300,'B':3.000,'B-':2.700, \
            'C+':2.300,'C':2.000,'C-':1.700,'D+':1.300,'D':1.000,'D-':0.700, \
            'F':0.000}

sidl = []  #check whether we are inserting duplicate student relation
           #if there is duplicate, we should not insert it again in relation

countfile = 0   #to debug if there are something wrong with looping files
printedfile = [] # to debug, same reason above

#looping for each csv file
#looping for each csv file
for allcsvfile in l:
    # if allcsvfile != '/Users/jackie/Desktop/Grades/1992_Q4.csv':
    #     continue
    eachfile = open(allcsvfile,'r')
    reader = csv.reader(eachfile)
    listreader = list(reader)
    lenlist = len(listreader)


    cidtermtl = []  #check whether a course cid and term appear twice
                    #which means that this is a summer 2 class
    summer = 0


    # header = next(reader)
    i = 0
    while i < lenlist:

        if i == 0:
            if listreader[0] != ['']:
                print("file begining doesn't begin with empty \
                        line, which I thought it should")

            i += 1
            continue

        if i > 0:
            lastrow = listreader[i-1]
        row = listreader[i]
        if i < lenlist - 1 :
            nextrow = listreader[i+1]


        # currentrow is CID,TERM,SUBJ...
        if row[0] =='CID':

            summer = 0 #set summer to 0 to avoid mistakes,
                       #we change summer only in CID-if

            #trying to find whether this class has student
            findnextseat = i
            while findnextseat < lenlist:
                if listreader[findnextseat][0] != 'SEAT':
                    findnextseat += 1

                #now findnextseat is the line that is SEAT,SID...
                else:
                    break

                #reach the end of file, and it ends with a class has no student
            if findnextseat + 1 == lenlist:
                # print("this is the end of the file, and this class class has no student")
                countfile += 1
                printedfile.append(ntpath.basename(allcsvfile))
                # print(countfile)


                break

            #this is not the last class in file, and this class has no student,
            #we set i to the nextline of the SEAT,SID...
            elif listreader[findnextseat + 1] == ['']:
                i = findnextseat + 1
                continue

            else: #this course has student, it is a valid class
                cid = nextrow[0]
                term = nextrow[1]
                subj = nextrow[2]
                crse = nextrow[3]
                sec = nextrow[4]
                units = nextrow[5]


                cidterm = cid+term
                if cidterm in cidtermtl:
                    # print("we have a summer 2 now")
                    # possible bug: no summer 2 printed
                    summer = 1
                else:
                    cidtermtl.append(cidterm)


                coursestuple = (cid, term, crse, sec, units, subj,summer)
                coursestl.append(coursestuple)


                i += 1
                continue

        # currentrow is INSTRUCTOR(S),TYPE,DAYS...
        elif row[0] == 'INSTRUCTOR(S)':

            #j represents the next total empty line
            j = i
            while j < lenlist:
                if listreader[j] != ['']:
                    j += 1
                else:
                    break

            # no instructor at all, totally empty
            # because CID-IF will jump through the class who has no student,
            # then in this if, there has to be student below,even
            # there is no instructor at all (no type, no days...)
            # which actually should not happen, because no student can have no instructor
            if j == i+1 :
                i += 2
#                print("we shouldn't go into here because no student have no instructor")
                continue

            #at least one instructor line
            else:
                instructors = nextrow[0]

                #We want to know what is this course
                #we want tot get CID, TERM, SUMMER to create meeting tuples
                lastlastrow = listreader[i-2]
                cid = lastlastrow[0]
                term = lastlastrow[1]

                #this line(i+1) has no instructor, which means this class's instructors
                #is somewhere above
                #we assume that there are students below because we are supposed to
                #jump the whole block when it has no student in courses-if
                if instructors == '':
                    for backfindc in range(i-1,0,-1):
                        if listreader[backfindc][0] != 'CID':
                            continue
                        else: #backfindc is the line CID,TERM...
                            if listreader[backfindc + 1][2] == lastlastrow[2]   \
                            and listreader[backfindc + 1][3] == lastlastrow[3] \
                            and listreader[backfindc+4][0] != '':
                                instructors = listreader[backfindc+4][0]
                                break
                            else:
                                continue
                lastinstructors = instructors
                # if lastinstructors == '':
                #     print("we cannot find previous instructor, so I set it to empty string")
                #     print("this is in file: ",allcsvfile)
                #     print("i = ",i)


                #l represents possible instructors line
                #j should represent next empty line
                for l in range(i+1,j):
                    lcurrentrow = listreader[l]
		    llastrow = listreader[l-1]
                    if set(lcurrentrow) < set(llastrow) or set(lcurrentrow) == set(llastrow) :
			continue
                    if lcurrentrow[0] == '':
                        instructors = lastinstructors
                    else:
                        instructors = lcurrentrow[0]
                        lastinstructors = instructors
                    mtype = lcurrentrow[1]
                    days = lcurrentrow[2]
                    time = lcurrentrow[3]
                    build = lcurrentrow[4]
                    room = lcurrentrow[5]

		    if "'" in instructors:
			instructors = instructors.replace("'","")

                    meetingtuple = (cid,time,build,days,instructors,mtype, \
                            room,term,summer)
                    meetingtl.append(meetingtuple)

                i = j + 1
                continue





        #i/currentrow is SEAT,SID...
        elif row[0] == 'SEAT':
            #we want to make sure that this line follows by
            #non empty student information
            if i == lenlist -1 :
#                print("we reach end of file in student if-block ")
                break
            elif nextrow == ['']:
#                print("We are suppposed to jump the empty \
#                    student block, but we failed to do so")
                i += 1
                continue

            else: #now we know that nextrow has at least one valid student information

                #we need to find cid,term,ngrade
                #and make sure units is within the course units range

                #i is the line SEAT,SID...
                #so we need to find the line of CID,TERM to get info
                #and we need to find the range of units
                backcourserownumber = 0
                for backfindcourse in range(i-1,0,-1):
                    if listreader[backfindcourse][0] != 'CID':
                        continue
                    else:
                        backcourserownumber = backfindcourse
                        break

                backcourserow = listreader[backcourserownumber+1]
                cid = backcourserow[0]
                term = backcourserow[1]
                unitsrange = backcourserow[5]





                #we need to find snextemptyline (studentnextemptyline)
                #after student block
                snextemptyline = i
                while snextemptyline < lenlist:
                    if listreader[snextemptyline] != ['']:
                        snextemptyline += 1
                    else:
                        break

                for m in range(i+1,snextemptyline):
                    mcurrentrow = listreader[m]
                    seat = mcurrentrow[0]
                    sid = mcurrentrow[1]
                    qsurname = mcurrentrow[2]   #some students might have '
                    qprefname = mcurrentrow[3]  #in their name
                    level = mcurrentrow[4]
                    sunits = mcurrentrow[5]
                    sclass = mcurrentrow[6]  #avoid using keyword class
                    major = mcurrentrow[7]
                    grade = mcurrentrow[8]
                    status = mcurrentrow[9]
                    email = mcurrentrow[10]


                    # qindex = qsurname.find('\'')
                    # qindex2 = qprefname.find('\'')
                    # if qindex != -1:
                    #     surname = qsurname[:qindex] + '\'' + qsurname[qindex:]
                    # else:
                    #     surname = qsurname
                    # if qindex2 != -1:
                    #     prefname = qprefname[:qindex2] + '\'' + qprefname[qindex2:]
                    # else:
                    #     prefname = qprefname

                    if "'" in mcurrentrow[2]:
                        mcurrentrow[2] = mcurrentrow[2].replace("'","")
                    # else:
                    #     surname = qsurname
                    if "'" in qprefname:
                        mcurrentrow[3] = mcurrentrow[3].replace("'","")
                    # else:
                    #     prefname = qprefname


                    if "'" in mcurrentrow[10]:
                        mcurrentrow[10] = mcurrentrow[10].replace("'","")

                    if sid in sidl:
                        pass
                    else:
                        sidl.append(sid)
                        studentstuple = (sid,status,mcurrentrow[3],mcurrentrow[2],mcurrentrow[10])
                        studentstl.append(studentstuple)

                        newstudenttuple = '('+"'"+sid +"','"+status+"','"+mcurrentrow[3]+"','"+mcurrentrow[2]+"','"+email+"'"+ ')'
                        newstudentstl.append(newstudenttuple)

                    #construting take tuples
                    #find number grade using dictionary
                    if grade in gradedic:
                        ngrade = gradedic[grade]
                    else:
                        ngrade = -1

                    if sunits == '':
			units = -1
                        taketuple = (sid,cid,term,major,seat,sclass,level,units,\
                                grade,ngrade,summer)
                        taketl.append(taketuple)
			continue
                    else:
                        units = float(sunits)
                    #check whether units
                    if '-' in unitsrange:#this is a range of units
                        down = float(unitsrange.split('-')[0])
                        up = float(unitsrange.split('-')[1])
                        if (units > up or units < down) and units != 0:
                            print("up is " , up)
                            print("down is: ", down)
                            print("student units not in range")
                            print("stdeunt units is: ", units)
                            print("this file is: ",allcsvfile )
                            print("this line is: ",i)

                    else:
                        if units > float(unitsrange) and units < 0:
                            print("student units not the same as this class")
                            print("stdeunt units is: ", units)
                            print("this file is: ",allcsvfile )
                            print("this line is: ",i)
                    taketuple = (sid,cid,term,major,seat,sclass,level,units,\
                    grade,ngrade,summer)
		    # if cid == '40626' and term=='199001'and sid=='142697422':
			# print 'line is: ' + str(taketuple) +str(allcsvfile)
                    taketl.append(taketuple)




                i += 1
                continue




        else:
            i += 1
            continue





coursests = str(coursestl).strip('[]')
meetingts = str(meetingtl).strip('[]')
studentsts = str(studentstl).strip('[]')
takets = str(taketl).strip('[]')
newstudentsts = str(newstudentstl).strip('[]')


print 'finishes reading data, now we will insert them into database'
cursor.execute('''
insert into Courses (CID, TERM, CRSE, SEC, UNITS, SUBJ, SUMMER) values'''+coursests\
+''';insert into Meeting (CID,TIME,BUILD,DAYS,INSTRUCTORS,TYPE,ROOM,TERM,SUMMER ) values'''+meetingts\
+''';insert into Students(SID,STATUS,PREFNAME,SURNAME,EMAIL) values'''+studentsts\
+''';insert into Take(SID,CID,TERM,MAJOR,SEAT,CLASS,LEVEL,UNITS,GRADE,NGRADE,SUMMER)values'''+takets\
+''';''')

# cursor.execute('''Select * from Take''')
# drows=cursor.fetchall()
# for drow in drows:
#     print drow
conn.commit()
cursor.close()
conn.close()
print 'load successful!'
# adding more comment




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
