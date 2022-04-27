# QUDA Tool view functions
# (c) Maurice Langner, Linguistics, RUB



from django.shortcuts import render, redirect


from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from viewer.models import *
import os


from django_downloadview import VirtualDownloadView
from django_downloadview import VirtualFile
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login, logout


import xml.etree.ElementTree as et
import numpy as np
from .forms import UploadFileForm




def loggingin(request):
    template = loader.get_template("viewer/login.html")
    context = {}
    return HttpResponse(template.render(context,request))


def checklogin(request):
    if request.method == 'POST' and "usrname" in request.POST.keys():
        usrname = request.POST["usrname"]
        pswd = request.POST["usrpasswd"]
        user = authenticate(request, username=usrname, password=pswd)
        if user is not None:
            login(request, user)
            #template = loader.get_template("viewer/surface.html")
            #context = {"message":"", "overlay":0, "leftfile":"", "rightfile":"", "reload":0}   
            #return HttpResponse(template.render(context, request))
            return HttpResponseRedirect(reverse('viewer:index'))
        else:
            return HttpResponseRedirect(reverse('viewer:loggingin'))

            



def loggingout(request):
    if request.method == 'POST' and "logout" in request.POST.keys():
        if request.session.get("lbadge_int",0) == 0 and request.session.get("rbadge_int",0) == 0:
       
            logout(request)
            return HttpResponseRedirect(reverse('viewer:loggingin'))

        else:
            request.session["overlay"] = True
            request.session["message"] = "Please save your progress before logging out!"
            return HttpResponseRedirect(reverse('viewer:index'))

def index(request, scroll=0):
    
    #if request.user.is_authenticated:
    #    print("user is already authenticated")

    try:
        #del request.session["leftfile"]

        docuLeft =  request.session["leftfile"]
        markup1 = docuLeft.toHTML(request)
        print("left file opened")
    except:
        markup1 = ""


    try:
        #del request.session["rightfile"]
        docuRight =  request.session["rightfile"]
        markup2 = docuRight.toHTML(request)
        #print(markup2)
        print("right file opened")
    except:
        markup2 = ""
        request.session["toggleFileType"] = request.session.get("toggleFileType", "TXT")
        print("default file type set: ", request.session["toggleFileType"])


    # try:
    #     selection = request.POST['file1']
    #     print(selection)
    
    # except:
    #     print("failure")
    

    # tree = et.parse('test1.xml')
    # root = tree.getroot()
    # docu = Document("testconfig", root)
    # markup = docu.toHTML()
    # request.session["leftfile"] = docu

    # tree2 = et.parse('test2.xml')
    # root2 = tree2.getroot()
    # docu2 = Document("testconfig", root2)
    # markup2 = docu2.toHTML()


    #print(docu.rootqud[0].qudForm)
    # for q in docu.rootqud[0].subQUDs:
    #     print(q.qudForm)
    #     for q2 in q.subQUDs:
    #         print(q2.qudForm)
    #         for q3 in q2.subQUDs:
    #             print(q3.qudForm)
    #             for q4 in q3.subQUDs:
    #                 print(q4.qudForm)
    #                 print([x.toHTML() for x in q4.segList])

    try:
        scroll = request.session["scrollPos"]
        print("Id for scrolling found")
    except:
        scroll = 0
        print("Id for scrolling not found")
    
    

    
    lb = request.session.get("lbadge_int",0)
    rb = request.session.get("rbadge_int",0)

    template = loader.get_template("viewer/surface.html")
    context = {"message":"", "overlay":0, "leftfile":markup1, "rightfile":markup2, "reload":scroll, "lb":lb, "rb":rb, "filetype":request.session["toggleFileType"]}   
    #context = {"rightfile":"left", "leftfile":"right"}
    if "overlay" in request.session.keys():
        print("active overlay")
        message = request.session["message"]
        del request.session["message"]
        del request.session["overlay"]
        context["message"] = message
        context["overlay"] = "block"

    return HttpResponse(template.render(context, request))
    #else:
    #    return HttpResponseRedirect(reverse('viewer:loggingin'))



def openFile(request):
    
    if request.method == 'POST' and "leftfile" in request.FILES.keys():
        #myfile1 = request.POST['leftfile']
        myfile = request.FILES['leftfile']
        request.session["lfile_name"] = myfile.name
        fs = FileSystemStorage()
        myfile1 = fs.save(myfile.name, myfile)
        tree = et.parse(myfile1)
        root = tree.getroot()
        docu = Document("testconfig", root)
        request.session["leftfile"] = docu
        request.session["lbadge_int"] = 0
        print(myfile1)
        fs.delete(myfile1)

    elif request.method == 'POST' and "rightfile" in request.FILES.keys():
        
        myfile = request.FILES['rightfile']
        request.session["rfile_name"] = myfile.name
        fs = FileSystemStorage()
        myfile2 = fs.save(myfile.name, myfile)
        
        if request.session["toggleFileType"] == "XML":
            tree = et.parse(myfile2)
            root = tree.getroot()
            docu2 = Document("testconfig", root)
            request.session["rightfile"] = docu2
            request.session["rbadge_int"] = 0
            print(myfile2)
            fs.delete(myfile2)
        
        else:
            handle = open(myfile2)
            plain = PLAIN(handle.read())
            request.session["rightfile"] = plain
            fs.delete(myfile2)
            print(plain.text)





        #fs = FileSystemStorage()
        #filename = fs.save(myfile.name, myfile)
    return HttpResponseRedirect(reverse('viewer:index'))


def close(request):
    
    if request.method == 'POST' and "closeleft" in request.POST.keys():
        if request.session.get("lbadge_int") == 0:
       
            try:
                del request.session["leftfile"]
                
            except: 
                pass
        else:
            request.session["overlay"] = True
            request.session["message"] = "Please save your progress before closing!"
            return HttpResponseRedirect(reverse('viewer:index'))
    elif request.method == 'POST' and "closeright" in request.POST.keys():
        
        
        if request.session.get("toggleFileType",0) == "XML":
        
            if request.session.get("rbadge_int") == 0:
                try:
                    del request.session["rightfile"]
                except:
                    pass
            else:
                request.session["overlay"] = True
                request.session["message"] = "Please save your progress before closing!"
                return HttpResponseRedirect(reverse('viewer:index'))
        elif request.session.get("toggleFileType",0) == "TXT":
            try:
                del request.session["rightfile"]
            except:
                pass

        else:
            pass

    return HttpResponseRedirect(reverse('viewer:index'))




def addQUD(request):
    if request.method == 'POST':
        this_seg = request.POST["addQUD"]
        print("present QUD: ", this_seg)
        request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            print("added sub qud left")
            newQUD = QUD("", "")
            obj.subUnits = obj.subUnits + [newQUD]
            doculeft.identifyQUD()
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1
        elif obj2:
            print("added sub qud right")
            newQUD = QUD("", "")
            obj2.subUnits = obj2.subUnits + [newQUD]
            docuright.identifyQUD()
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1

    return HttpResponseRedirect(reverse('viewer:index'))
    #return index(request, scroll=this_seg)



def submitArea(request):

    if request.method == 'POST':
        this_seg = request.POST["submitArea"]
        textinput = request.POST["inputtext"]
        print("present Element: ", this_seg)
        request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            if obj.type == "QUD":
                obj.qudForm = textinput
            elif obj.type == "SEGMENT":
                obj.text = textinput
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1
        elif obj2:
            if obj2.type == "QUD":
                obj2.qudForm = textinput
            elif obj2.type == "SEGMENT":
                obj2.text = textinput
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1

            
    return HttpResponseRedirect(reverse('viewer:index'))


def removeQUD(request):

    if request.method == 'POST':
        this_seg = request.POST["removeQUD"]
        print("present QUD: ", this_seg)
        #request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            if obj.identifier == "Q.0":
                request.session["overlay"] = True
                request.session["message"] = "You cannot delete Q.0!"
                return HttpResponseRedirect(reverse('viewer:index'))
            else:

                index = None
                for s in range(len(prev.subUnits)):
                    if prev.subUnits[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                prev.subUnits = prev.subUnits[:index] + prev.subUnits[index+1:]
                request.session["scrollPos"] = prev.idn
                doculeft.identifyQUD()
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1

        elif obj2:
            if obj2.identifier == "Q.0":
                request.session["overlay"] = True
                request.session["message"] = "You cannot delete Q.0!"
                return HttpResponseRedirect(reverse('viewer:index'))
            else:

                index = None
                for s in range(len(prev2.subUnits)):
                    if prev2.subUnits[s].idn == obj2.idn:
                        index = s
                        break
                    else:
                        continue
                prev2.subUnits = prev2.subUnits[:index] + prev2.subUnits[index+1:]
                request.session["scrollPos"] = prev2.idn
                docuright.identifyQUD()
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1
        
    return HttpResponseRedirect(reverse('viewer:index'))


def associateQUD(request):


    def isSubbranch(q1, q2):
        # q1 to copy, q2 target
        lq1 = q1.split(".")
        lq2 = q2.split(".")
        # If lengths are identical (equal depth) and one
        # branch is different, ok
        if len(lq1) == len(lq2):
            if any(map(lambda x,y: x!=y,  lq1,lq2)):
                return False
                # else identical and no copy possible
            else:
                return True
        # if depth of copy is lower than target, q1
        # might be a dominating node of q2        
        elif len(lq1) < len(lq2):
            diff = len(lq2) - len(lq1)
            # if one of the first n branches are different,
            # copying is fine since q1 does not dominate q1
            if any(map(lambda x,y: x!=y,  lq1,lq2[:-diff])):
                return False
                # otherwise q1 dominates q2 and copying is not possible
            else:
                return True
        # in case the copy element is deeper than the target node,
        # q1 cannot dominate q2 and copying is ok
        else:
            return False




    if request.method == 'POST' and "associate" in request.POST.keys():
        associate_target = request.POST["associate"]
        this_seg = request.POST["associateButton"]
        print(associate_target, this_seg)
        
        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            target = doculeft.findQUD(doculeft.rootqud[0], associate_target)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
            target = docuright.findQUD(docuright.rootqud[0], associate_target)
        except:
            obj2 = False

        if obj and target:
            if obj.identifier == "Q.0":
                request.session["overlay"] = True
                request.session["message"] = "You cannot associate Q.0!"
                return HttpResponseRedirect(reverse('viewer:index'))
            elif isSubbranch(obj.identifier, target.identifier):
                request.session["overlay"] = True
                request.session["message"] = "You cannot rebranch a QUD to a dominated QUD or to itself!"
                return HttpResponseRedirect(reverse('viewer:index'))


            else:

                index = None
                for s in range(len(prev.subUnits)):
                    if prev.subUnits[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                prev.subUnits = prev.subUnits[:index] + prev.subUnits[index+1:]
                target.subUnits = target.subUnits + [obj]
                request.session["scrollPos"] = target.idn
                doculeft.identifyQUD()
                request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1

        elif obj2 and target:
            if obj2.identifier == "Q.0":
                request.session["overlay"] = True
                request.session["message"] = "You cannot associate Q.0!"
                return HttpResponseRedirect(reverse('viewer:index'))

            elif isSubbranch(obj2.identifier, target.identifier):
                request.session["overlay"] = True
                request.session["message"] = "You cannot rebranch a QUD to a dominated QUD or to itself!"
                return HttpResponseRedirect(reverse('viewer:index'))


            else:

                index = None
                for s in range(len(prev2.subUnits)):
                    if prev2.subUnits[s].idn == obj2.idn:
                        index = s
                        break
                    else:
                        continue
                prev2.subUnits = prev2.subUnits[:index] + prev2.subUnits[index+1:]
                target.subUnits = target.subUnits + [obj]
                request.session["scrollPos"] = target.idn
                docuright.identifyQUD()
                request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1

        else:
            
            request.session["overlay"] = True
            request.session["message"] = "Target QUD does not exist!"
            return HttpResponseRedirect(reverse('viewer:index'))

    return HttpResponseRedirect(reverse('viewer:index'))


def addSubSegment(request):
    if request.method == 'POST':
        this_seg = request.POST["addSegment"]
        print("present Segment: ", this_seg)
        request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            if obj.type == "QUD":
                newSeg = DISCOURSE_UNIT("")
                obj.subUnits = obj.subUnits + [newSeg]
                
            else:
                newSeg = SEGMENT("")
                obj.subsegments = obj.subsegments + [newSeg]
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1
                
            
        elif obj2:

            if obj2.type == "QUD":
                newSeg = DISCOURSE_UNIT("")
                obj2.subUnits = obj2.subUnits + [newSeg]
                
            else:
                newSeg = SEGMENT("")
                obj2.subsegments = obj2.subsegments + [newSeg]
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1



    return HttpResponseRedirect(reverse('viewer:index'))

def moveDown(request):

    def shiftd(obj, prev):
        if obj.type == "SEGMENT":
            if prev.type == "SEGMENT":
                index = None
                for s in range(len(prev.subsegments)):
                    if prev.subsegments[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                if index == len(prev.subsegments)-1:
                    return 0
                elif index < len(prev.subsegments)-1:
                    prev.subsegments = prev.subsegments[:index] + [prev.subsegments[index+1]] + [prev.subsegments[index]] + prev.subsegments[index+2:] 
            elif prev.type == "QUD":
                index = None
                for s in range(len(prev.subUnits)):
                    if prev.subUnits[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                if index == len(prev.subUnits)-1:
                    return 0
                elif index < len(prev.subUnits)-1:
                    prev.subUnits = prev.subUnits[:index] + [prev.subUnits[index+1]] + [prev.subUnits[index]] + prev.subUnits[index+2:]
            
        elif obj.type == "QUD":
            index = None
            for s in range(len(prev.subUnits)):
                if prev.subUnits[s].idn == obj.idn:
                    index = s
                    break
                else:
                    continue
            if index == len(prev.subUnits)-1:
                return 0
            elif index < len(prev.subUnits)-1:
                prev.subUnits = prev.subUnits[:index] + [prev.subUnits[index+1]] + [prev.subUnits[index]] + prev.subUnits[index+2:] 
                
    if request.method == 'POST':
        this_seg = request.POST["pushDown"]
        request.session["scrollPos"] = this_seg
        print("present QUD: ", this_seg)
        
        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            shiftd(obj, prev)
            doculeft.identifyQUD()
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1

        elif obj2:
            shiftd(obj2, prev2)
            docuright.identifyQUD()
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1
            
            
    return HttpResponseRedirect(reverse('viewer:index'))



def moveUp(request):
    def shiftu(obj, prev):
        if obj.type == "SEGMENT":
            if prev.type == "SEGMENT":
                index = None
                for s in range(len(prev.subsegments)):
                    if prev.subsegments[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                if index == 0:
                    return 0
                elif index > 0:
                    prev.subsegments = prev.subsegments[:index-1] + [prev.subsegments[index]] + [prev.subsegments[index-1]] + prev.subsegments[index+1:] 
            elif prev.type == "QUD":
                index = None
                for s in range(len(prev.subUnits)):
                    if prev.subUnits[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                if index == 0:
                    return 0
                elif index > 0:
                    prev.subUnits = prev.subUnits[:index-1] + [prev.subUnits[index]] + [prev.subUnits[index-1]] + prev.subUnits[index+1:] 
            
            
        elif obj.type == "QUD":
            index = None
            for s in range(len(prev.subUnits)):
                if prev.subUnits[s].idn == obj.idn:
                    index = s
                    break
                else:
                    continue
            if index == 0:
                return 0
            elif index > 0:
                prev.subUnits = prev.subUnits[:index-1] + [prev.subUnits[index]] + [prev.subUnits[index-1]] + prev.subUnits[index+1:] 
            

    if request.method == 'POST':
        this_seg = request.POST["pushUp"]
        request.session["scrollPos"] = this_seg
        print("present QUD: ", this_seg)
        
        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            shiftu(obj, prev)
            doculeft.identifyQUD()
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1

        elif obj2:
            shiftu(obj2, prev2)
            docuright.identifyQUD()
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1
            
            
    return HttpResponseRedirect(reverse('viewer:index'))


def associateSegment(request):

    def associate(obj, prev, target):
        if prev.type == "QUD":
            index = None
            for s in range(len(prev.subUnits)):
                if prev.subUnits[s].idn == obj.idn:
                    index = s
                    break
                else:
                    continue
            prev.subUnits = prev.subUnits[:index] + prev.subUnits[index+1:]
            target.subUnits = target.subUnits + [obj]
            request.session["scrollPos"] = target.idn

        else:
            index = None
            for s in range(len(prev.subsegments)):
                if prev.subsegments[s].idn == obj.idn:
                    index = s
                    break
                else:
                    continue
            prev.subsegments = prev.subsegments[:index] + prev.subsegments[index+1:]
            target.subUnits = target.subUnits + [obj] 
            request.session["scrollPos"] = target.idn
            



    if request.method == 'POST' and "associate" in request.POST.keys():
        associate_target = request.POST["associate"]
        this_seg = request.POST["associatebutton"]
        

        if associate_target == "":
            request.session["overlay"] = True
            request.session["message"] = "You did not enter a target QUD for rebranching!"
            return HttpResponseRedirect(reverse('viewer:index'))
        
        
        print(associate_target, this_seg)
        
        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            target = doculeft.findQUD(doculeft.rootqud[0], associate_target)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
            target = docuright.findQUD(docuright.rootqud[0], associate_target)
        except:
            obj2 = False

        if obj:
           associate(obj, prev, target)
           request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1

        elif obj2:
           associate(obj2, prev2, target)
           request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1

    return HttpResponseRedirect(reverse('viewer:index'))




def removeSegment(request):

    if request.method == 'POST' and "removeSegment" in request.POST.keys():
        this_seg = request.POST["removeSegment"]
        print("present Segment: ", this_seg)
        #request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            if prev.type == "QUD":
                index = None
                for s in range(len(prev.subUnits)):
                    if prev.subUnits[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                prev.subUnits = prev.subUnits[:index] + prev.subUnits[index+1:]
                request.session["scrollPos"] = prev.idn
            else:
                index = None
                for s in range(len(prev.subsegments)):
                    if prev.subsegments[s].idn == obj.idn:
                        index = s
                        break
                    else:
                        continue
                prev.subsegments = prev.subsegments[:index] + prev.subsegments[index+1:]
                request.session["scrollPos"] = prev.idn
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1



        elif obj2:
            if prev2.type == "QUD":
                index = None
                for s in range(len(prev2.subUnits)):
                    if prev2.subUnits[s].idn == obj2.idn:
                        index = s
                        break
                    else:
                        continue
                prev2.subUnits = prev2.subUnits[:index] + prev2.subUnits[index+1:]
                request.session["scrollPos"] = prev2.idn
            else:
                index = None
                for s in range(len(prev2.subsegments)):
                    if prev2.subsegments[s].idn == obj2.idn:
                        index = s
                        break
                    else:
                        continue
                prev2.subsegments = prev2.subsegments[:index] + prev2.subsegments[index+1:]
                request.session["scrollPos"] = prev2.idn
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1
        
    return HttpResponseRedirect(reverse('viewer:index'))






def classify(request):
    if request.method == 'POST' and "classify" in request.POST.keys():
        this_seg = request.POST["classifybutton"]
        this_class = request.POST["classify"]
        print("present Element: ", this_seg)
        request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False

        if obj:
            obj.classification = this_class
            print(obj.classification)
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1
        elif obj2:
            obj2.classification = this_class
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1

            
    return HttpResponseRedirect(reverse('viewer:index'))


def saveSegID(request):
    if request.method == 'POST':
        this_seg = request.POST["saveSegID"]
        this_idinput = request.POST["saveSegIDInput"]
        print("present Segment: ", this_seg)
        request.session["scrollPos"] = this_seg

        try:
            doculeft = request.session["leftfile"]
            obj, prev = doculeft.findByID(doculeft.rootqud[0], this_seg, previous=None)
            print(obj)
        except:
            obj = False
        try:
            docuright = request.session["rightfile"]
            obj2, prev2 = docuright.findByID(docuright.rootqud[0], this_seg, previous=None)
        except:
            obj2 = False


        if obj:
            obj.identifier = this_idinput
            request.session["lbadge_int"] = request.session.get("lbadge_int",0) + 1

        elif obj2:
            obj2.identifier = this_idinput
            request.session["rbadge_int"] = request.session.get("rbadge_int",0) + 1

    return HttpResponseRedirect(reverse('viewer:index'))



def saveFile(request):
    if request.method == 'POST':
        if "saveleft" in request.POST.keys():
            try:
                doculeft =  request.session["leftfile"]

                nonclassSegms = []
                doculeft.getAllUnclassifiedSegments(doculeft.rootqud[0], nonclassSegms)
                
                if nonclassSegms:
                    first = nonclassSegms[0]
                    request.session["overlay"] = True
                    request.session["message"] = "Please classify the SEGMENT in Focus first!"
                    request.session["scrollPos"] = first
                    return HttpResponseRedirect(reverse('viewer:index'))









                file_obj = doculeft.toXML()
                request.session["lbadge_int"] = 0
                response = HttpResponse(file_obj, content_type='text/xml')
                if "lfile_name" in request.session.keys():
                    response['Content-Disposition'] = 'attachment; filename={}'.format(request.session["lfile_name"])
                else:
                    response['Content-Disposition'] = 'attachment; filename=download.xml'
                #request.session["download"] = response
        
                return response
                #return HttpResponseRedirect(reverse('viewer:index'))
            except:
                return HttpResponseRedirect(reverse('viewer:index'))




        elif "saveright" in request.POST.keys():
            try:
                docuright =  request.session["rightfile"]
                file_obj = docuright.toXML()
                request.session["rbadge_int"] = 0
                response = HttpResponse(file_obj, content_type='text/xml')
                response['Content-Disposition'] = 'attachment; filename=download.xml'
                
                return response
            except:
                return HttpResponseRedirect(reverse('viewer:index'))


    #return HttpResponseRedirect(reverse('viewer:index'))
    

def toggleFileType(request):
    if request.method == "POST" and "toggleFileType" in request.POST.keys():
        if request.session["toggleFileType"] == "XML":
            request.session["toggleFileType"] = "TXT"
            print("filetype changed to TXT")
        elif request.session["toggleFileType"] == "TXT":
            request.session["toggleFileType"] = "XML"
            print("filetype changed to XML")
        else:
            print("toggle filetype failed")
    
    return HttpResponseRedirect(reverse('viewer:index'))
    


def initiate(request):
    if request.method == 'POST':

        if request.session.get("lbadge_int",0) == 0 and request.session.get("rbadge_int",0) == 0:
            if "initleft" in request.POST.keys():
                
                doculeft = Document("","")
                newQUD = QUD("Please enter QUD text here...", "")
                doculeft.rootqud = [newQUD]
                doculeft.identifyQUD()
                request.session["leftfile"] = doculeft
                request.session["lbadge_int"] = 1
            elif "initright" in request.POST.keys():
                            
                docuright = Document("","")
                newQUD = QUD("Please enter QUD text here...", "")
                docuright.rootqud = [newQUD]
                docuright.identifyQUD()
                request.session["rightfile"] = docuright
                request.session["rbadge_int"] = 1
        else:
            request.session["overlay"] = True
            request.session["message"] = "Please save your progress before starting a new annotation!"
            return HttpResponseRedirect(reverse('viewer:index'))


    return HttpResponseRedirect(reverse('viewer:index'))



def agreement(request):
    
    # 3rd-party code for agreement calculation (alpha, kappa)
    # adapted, ML


    def get_annos(node, annos, tags, id=0):
        #Get annotation-tags out of a file for each word.
        #Input: root or current node-element, list of annotations, list of tags, number of current node level"
        #Output: Updated annotation-list

        for child in node:
            if child.tag == "SEGMENT":
                #get terminals out of the tree
                words = child.text.split()
                for word in words:
                    #save the word and its annotation-tags in the annotation-list
                    annos.append([word, tags[:id]])
            else:
                id+= 1
                #save the tag of the current node in the tags-list
                try:
                    tags[id-1] = child.tag
                except:
                    tags.append(child.tag)

                if child:
                    annos = get_annos(child, annos, tags, id)
                else:
                    words = child.text.split()
                    for word in words:
                        annos.append([word, tags[:id]])
                id-= 1

        return annos

    ########################

    def read_files(file1, file2):
        #Get the values that are needed for the formulas out of the Input-files.
        #Input: 2 files with QUD-annotations
        #Output:  number of words, dictionary with matrixes that contain the values for calculating kappa,
        #        dictionary with matrixes that contain the values for calculating alpha

        #Read file1
        #tree = et.parse(file1)
        root = et.fromstring(file1)
        #get annotation-tags for each word
        annos1 = get_annos(root, [], [])
        #number of words
        w1 = len(annos1)

        #Read file2
        #tree = et.parse(file2)
        root = et.fromstring(file2)
        #get annotation-tags for each word
        annos2 = get_annos(root, [], [])
        #number of words
        w2 = len(annos2)

        #check if both files have the same word number
        if w1 != w2:
            return [w1, w2], [], []

        else:
            #number of words
            w = w1
            #Tagset
            S = ["AT", "F", "CMT", "CON", "CT", "NAI"]

            #dictionary with matrixes; key: Tag, value: Matrix that belongs to this tag
            kappa_matrixes = dict()
            for s in S:
                #for each tag create a (w x 2)-matrix
                matrix = np.zeros((w,2))
                #the i-th row contains the number of annotators who assigned the i-th word with Tag s (first column) or not (second column)
                for i in range(w):
                    if s in annos1[i][1]: matrix[i][0] += 1
                    else: matrix[i][1] += 1
                    if s in annos2[i][1]: matrix[i][0] += 1
                    else: matrix[i][1] += 1

                #check if a tag is used by at least one annotator; if not value is NA
                column_sum = np.sum(matrix, axis=0)
                if column_sum[0] == 0: kappa_matrixes[s] = "NA"
                else: kappa_matrixes[s] = matrix

            #dictionary with matrixes; key: Tag, value: Matrix that belongs to this tag
            alpha_matrixes = dict()
            for s in S:
                #for each tag create a (2 x 2)-matrix
                matrix = np.zeros((2,2))
                #row 1 contains the number of words that both annotators (first column) or only annotator 1 (second column) assigned with tag s
                #row 2 contains the number of words that only annotator 2 (first column) or no annotator (second column) assigned with tag s
                for i in range(w):
                    if s in annos1[i][1]:
                        if s in annos2[i][1]: matrix[0][0] += 2
                        else: matrix[0][1] += 1
                    else:
                        if s in annos2[i][1]: matrix[0][1] += 1
                        else: matrix[1][1] += 2
                matrix[1][0] = matrix[0][1]

                #check if a tag is used by at least one annotator; if not value is NA
                row_sum = np.sum(matrix, axis=1)
                if row_sum[0] == 0: alpha_matrixes[s] = "NA"
                else: alpha_matrixes[s] = matrix

            return w, kappa_matrixes, alpha_matrixes

    ########################

    def read_qud_tags(file1, file2):
        #Get the values that are needed for calculating the metrics of the QUD-tags out of the files.
        #Input: 2 files with QUD annotations
        #Output: dictionary with matrixes that contain the values for calculating kappa,
        #        dictionary with matrixes that contain the values for calculating alpha,
        #        number of words, number of spans

        ########################

        def get_QUD_spans(qud, qud_spans=list(), qud_bounds=list(), word_id=0):
            #Get all annotated QUD-spans and QUD-boundaries out of a file.
            #Input: Current QUD-node, list with all QUD-spans, list with all QUD-boundaries, current word index
            #Output: Updated QUD-spans-list, Updated QUD-bounds-list, word index

            #length of the current QUD-span
            span = len(get_annos(qud, [], [])) - 1
            #index of the word where the QUD-span ends
            span_end = word_id+span
            #add the current QUD-span to the spans-list
            if (word_id, span_end) not in qud_spans: qud_spans.append((word_id, span_end))
            #add the word index where the QUD-span ends to the bounds-list
            if span_end not in qud_bounds: qud_bounds.append(span_end)

            if qud.find("QUD"):
                #get the spans and boundaries for every sub-QUD-node
                for child in qud:
                    if child.tag == "QUD":
                        qud_spans, qud_bounds, word_id = get_QUD_spans(child, qud_spans, qud_bounds, word_id)
                    else:
                        span = len(get_annos(child, [], []))
                        word_id += span
            else:
                word_id += span + 1

            return qud_spans, qud_bounds, word_id

        ########################

        #Read file1
        #tree = ET.parse(file1)
        root = et.fromstring(file1)
        #find the first QUD-node
        qud = root.find("QUD")
        #get QUD-spans, QUD-boundaries and the number of words out of the annotation-file
        spans1, bounds1, word_id = get_QUD_spans(qud)

        #Read file2
        #tree = ET.parse(file2)
        root = et.fromstring(file2)
        #find the first QUD-node
        qud = root.find("QUD")
        #get QUD-spans, QUD-boundaries and the number of words out of the annotation-file
        spans2, bounds2, word_id = get_QUD_spans(qud, [], [], 0)


        kappa_matrixes = dict() #key: Bounds or Trees; value: matrix that belongs to QUD-bounds or QUD-trees

        #get values for comparing only the QUD-boundaries:
        #create a (word-number x 2)-matrix
        matrix = np.zeros((word_id, 2))
        #the i-th row contains the number of annotators who have a QUD-boundary after the i-th word (first column) or not (second column)
        for i in range(word_id):
            if i in bounds1: matrix[i][0] += 1
            else: matrix[i][1] += 1
            if i in bounds2: matrix[i][0] += 1
            else: matrix[i][1] += 1
        kappa_matrixes["Bounds"] = matrix

        #get values for comparing the whole QUD-trees:
        #total number of possible QUD-spans
        row_nr = int(word_id*(word_id+1)/2)
        #create a (span-number x 2)-matrix
        matrix = np.zeros((row_nr, 2))
        x = 0
        row = 0
        while x < word_id:
            #the i-th row contains the number of annotators who assigned the i-th word-span as QUD (first column) or not (second column)
            for i in range(x, word_id):
                if (x, i) in spans1: matrix[row][0] += 1
                else:  matrix[row][1] += 1
                if (x, i) in spans2: matrix[row][0] += 1
                else:  matrix[row][1] += 1
                row += 1
            x += 1
        kappa_matrixes["Trees"] = matrix


        alpha_matrixes = dict() #key: Bounds or Trees; value: matrix that belongs to QUD-bounds or QUD-trees

        #get values for comparing only the QUD-boundaries:
        #create a (2 x 2)-matrix
        matrix = np.zeros((2, 2))
        #row 1 contains the number of words after that both annotators (first column) or only annotator 1 (second column) have a QUD-boundary
        #row 2 contains the number of words after that only annotator 2 (first column) or no annotator (second column) has a QUD-boundary
        for i in range(word_id):
            if i in bounds1:
                if i in bounds2: matrix[0][0] += 2
                else: matrix[0][1] += 1
            else:
                if i in bounds2: matrix[0][1] += 1
                else: matrix[1][1] += 2
        matrix[1][0] = matrix[0][1]
        alpha_matrixes["Bounds"] = matrix

        #get values for comparing the whole QUD-trees:
        #create a (2 x 2)-matrix
        matrix = np.zeros((2, 2))
        #row 1 contains the number of spans that both annotators (first column) or only annotator 1 (second column) assigned with a QUD-tag
        #row 2 contains the number of spans that only annotator 2 (first column) or no annotator (second column) assigned with a QUD-tag
        for span in spans1:
            if span in spans2: matrix[0][0] += 2
            else: matrix[0][1] += 1
        for span in spans2:
            if span not in spans1: matrix[0][1] += 1
        matrix[1][0] = matrix[0][1]
        sum = np.sum(matrix)
        matrix[1][1] = 2*row_nr - sum
        alpha_matrixes["Trees"] = matrix

        return kappa_matrixes, alpha_matrixes, word_id, row_nr

    ########################

    def calculate_kappa(matrix, n, s, w):
        #Function that calculates Fleiss' Kappa.
        #Input: matrix with the annotation-values, number of annotators, number of tags, number of words
        #Output: Kappa (value between 0 and 1)

        #calculate P_a (agreement probability)
        sum_rows = 0
        for i in range(w): #iterate over rows
            sum_cols = 0
            for j in range(s): #iterate over columns
                sum_cols += matrix[i][j]*(matrix[i][j] - 1)
            sum_rows += sum_cols/(n*(n - 1))
        P_a = sum_rows / w

        #calculate P_c (agreement by chance)
        sum_cols = 0
        for j in range(s): #iterate over columns
            sum_rows = 0
            for i in range(w): #iterate over rows
                sum_rows += matrix[i][j]/(n*w)
            sum_cols += sum_rows*sum_rows
        P_c = sum_cols

        #calculate Kappa
        kappa = round((P_a - P_c)/(1 - P_c), 3)

        return kappa

    ########################

    def calculate_alpha(matrix, n, w):
        #Function that calculates Krippendorff's Alpha.
        #Input: matrix with the annotation-values, number of annotators, number of words
        #Output: Alpha (value between 0 and 1)

        #calculate P_d (disagreement probability)
        P_d = matrix[1][0] / (n*(n-1)*w)

        #calculate P_c (disagreement by chance)
        sum_rows = np.sum(matrix, axis=1)
        tag1 = sum_rows[0] #total number of tag1
        tag2 = sum_rows[1] #total number of tag2
        P_c = 2*tag1*tag2 / (w*n*(w*n-1))

        #calculate alpha
        alpha = round(1 - P_d/P_c, 3)

        return alpha

    ########################

    def calculateAgreement(file1, file2):
        
        #get values for all tags - except of QUD-tags - out of the files
        w, kappa_matrixes, alpha_matrixes = read_files(file1, file2)

        #metrics can only be calculated if both files consists of exactly the same words
        if not kappa_matrixes:
            message: "The files are inconsistent. Agreement Calculation impossible"
            return message
        else:
            #calculate kappa for each tag
            kappas = dict()
            for tag in kappa_matrixes:
                #if a tag is not used at all, value is "NA"
                if isinstance(kappa_matrixes[tag], str) and kappa_matrixes[tag] == "NA":
                    kappas[tag] = "NA"
                else:
                    kappas[tag] = calculate_kappa(kappa_matrixes[tag], 2, 2, w)

            #calculate alpha for each tag
            alphas = dict()
            for tag in alpha_matrixes:
                #if a tag is not used at all, value is "NA"
                if isinstance(alpha_matrixes[tag], str) and alpha_matrixes[tag] == "NA":
                    alphas[tag] = "NA"
                else:
                    alphas[tag] = calculate_alpha(alpha_matrixes[tag], 2, w)

            #calculate kappa and alpha for QUD-tags (on word level)
            qud_kappa_matrixes, qud_alpha_matrixes, w1, w2 = read_qud_tags(file1, file2)
            kappas["QUD-Bounds"] = calculate_kappa(qud_kappa_matrixes["Bounds"], 2, 2, w1)
            kappas["QUD-Trees"] = calculate_kappa(qud_kappa_matrixes["Trees"], 2, 2, w2)
            alphas["QUD-Bounds"] = calculate_alpha(qud_alpha_matrixes["Bounds"], 2, w1)
            alphas["QUD-Trees"] = calculate_alpha(qud_alpha_matrixes["Trees"], 2, w2)

            #Output
            return kappas, alphas


    # End of 3rd-party code

    if request.method == 'POST':
        if "agreement" in request.POST.keys():
                
            request.session["overlay"] = True
            request.session["message"] = "You calculated the inter annotator agreement. Numbers I don't know."
        
            doculeft =  request.session["leftfile"]

            nonclassSegms = []
            doculeft.getAllUnclassifiedSegments(doculeft.rootqud[0], nonclassSegms)
            
            if nonclassSegms:
                first = nonclassSegms[0]
                request.session["overlay"] = True
                request.session["message"] = "Please classify the SEGMENT in Focus first!"
                request.session["scrollPos"] = first
                return HttpResponseRedirect(reverse('viewer:index'))


            docuright =  request.session["rightfile"]

            nonclassSegms = []
            docuright.getAllUnclassifiedSegments(docuright.rootqud[0], nonclassSegms)
            
            if nonclassSegms:
                first = nonclassSegms[0]
                request.session["overlay"] = True
                request.session["message"] = "Please classify the SEGMENT in Focus first!"
                request.session["scrollPos"] = first
                return HttpResponseRedirect(reverse('viewer:index'))



        



            xmlStringLeft = doculeft.toXML()
            xmlStringRight = docuright.toXML()
            kaps, alphs = calculateAgreement(xmlStringLeft, xmlStringRight)


            request.session["overlay"] = True
            mesg = "You calculated the inter annotator agreement:\n"
            mesg += "kappa values: " + str(kaps) + "\n"
            mesg += "alpha values: " + str(alphs) + "\n"

            request.session["message"] = mesg
        


            

    return HttpResponseRedirect(reverse('viewer:index'))



"""
# Calculation of annotation-metrics - Fleiss' Kappa & Krippendorff's Alpha

# Overview:
#     1. Input: 2 files with QUD-annotations
#     2. Get the values that are needed for the formulas out of the files --> functions: read_files, read_qud_tags
#     3. Calculate Kappa
#     4. Calculate Alpha
#     5. Output: dictionary with all Kappa-values, dictionary with all Alpha-values
saveleft
########################

import xml.etree.ElementTree as ET
import numpy as np

########################

def get_annos(node, annos, tags, id=0):
    #Get annotation-tags out of a file for each word.
    #Input: root or current node-element, list of annotations, list of tags, number of current node level"
    #Output: Updated annotation-list

    for child in node:
        if child.tag == "SEGMENT":
            #get terminals out of the tree
            words = child.text.split()
            for word in words:
                #save the word and its annotation-tags in the annotation-list
                annos.append([word, tags[:id]])
        else:
            id+= 1
            #save the tag of the current node in the tags-list
            try:
                tags[id-1] = child.tag
            except:
                tags.append(child.tag)

            if child:
                annos = get_annos(child, annos, tags, id)
            else:
                words = child.text.split()
                for word in words:
                    annos.append([word, tags[:id]])
            id-= 1

    return annos

########################

def read_files(file1, file2):
    #Get the values that are needed for the formulas out of the Input-files.
    #Input: 2 files with QUD-annotations
    #Output:  number of words, dictionary with matrixes that contain the values for calculating kappa,
    #        dictionary with matrixes that contain the values for calculating alpha

    #Read file1
    tree = ET.parse(file1)
    root = tree.getroot()
    #get annotation-tags for each word
    annos1 = get_annos(root, [], [])
    #number of words
    w1 = len(annos1)

    #Read file2
    tree = ET.parse(file2)
    root = tree.getroot()
    #get annotation-tags for each word
    annos2 = get_annos(root, [], [])
    #number of words
    w2 = len(annos2)

    #check if both files have the same word number
    if w1 != w2:
        return [w1, w2], [], []

    else:
        #number of words
        w = w1
        #Tagset
        S = ["AT", "F", "CMT", "CON", "CT", "NAI"]

        #dictionary with matrixes; key: Tag, value: Matrix that belongs to this tag
        kappa_matrixes = dict()
        for s in S:
            #for each tag create a (w x 2)-matrix
            matrix = np.zeros((w,2))
            #the i-th row contains the number of annotators who assigned the i-th word with Tag s (first column) or not (second column)
            for i in range(w):
                if s in annos1[i][1]: matrix[i][0] += 1
                else: matrix[i][1] += 1
                if s in annos2[i][1]: matrix[i][0] += 1
                else: matrix[i][1] += 1

            #check if a tag is used by at least one annotator; if not value is NA
            column_sum = np.sum(matrix, axis=0)
            if column_sum[0] == 0: kappa_matrixes[s] = "NA"
            else: kappa_matrixes[s] = matrix

        #dictionary with matrixes; key: Tag, value: Matrix that belongs to this tag
        alpha_matrixes = dict()
        for s in S:
            #for each tag create a (2 x 2)-matrix
            matrix = np.zeros((2,2))
            #row 1 contains the number of words that both annotators (first column) or only annotator 1 (second column) assigned with tag s
            #row 2 contains the number of words that only annotator 2 (first column) or no annotator (second column) assigned with tag s
            for i in range(w):
                if s in annos1[i][1]:
                    if s in annos2[i][1]: matrix[0][0] += 2
                    else: matrix[0][1] += 1
                else:
                    if s in annos2[i][1]: matrix[0][1] += 1
                    else: matrix[1][1] += 2
            matrix[1][0] = matrix[0][1]

            #check if a tag is used by at least one annotator; if not value is NA
            row_sum = np.sum(matrix, axis=1)
            if row_sum[0] == 0: alpha_matrixes[s] = "NA"
            else: alpha_matrixes[s] = matrix

        return w, kappa_matrixes, alpha_matrixes

########################

def read_qud_tags(file1, file2):
    #Get the values that are needed for calculating the metrics of the QUD-tags out of the files.
    #Input: 2 files with QUD annotations
    #Output: dictionary with matrixes that contain the values for calculating kappa,
    #        dictionary with matrixes that contain the values for calculating alpha,
    #        number of words, number of spans

    ########################

    def get_QUD_spans(qud, qud_spans=list(), qud_bounds=list(), word_id=0):
        #Get all annotated QUD-spans and QUD-boundaries out of a file.
        #Input: Current QUD-node, list with all QUD-spans, list with all QUD-boundaries, current word index
        #Output: Updated QUD-spans-list, Updated QUD-bounds-list, word index

        #length of the current QUD-span
        span = len(get_annos(qud, [], [])) - 1
        #index of the word where the QUD-span ends
        span_end = word_id+span
        #add the current QUD-span to the spans-list
        if (word_id, span_end) not in qud_spans: qud_spans.append((word_id, span_end))
        #add the word index where the QUD-span ends to the bounds-list
        if span_end not in qud_bounds: qud_bounds.append(span_end)

        if qud.find("QUD"):
            #get the spans and boundaries for every sub-QUD-node
            for child in qud:
                if child.tag == "QUD":
                    qud_spans, qud_bounds, word_id = get_QUD_spans(child, qud_spans, qud_bounds, word_id)
                else:
                    span = len(get_annos(child, [], []))
                    word_id += span
        else:
            word_id += span + 1

        return qud_spans, qud_bounds, word_id

    ########################

    #Read file1
    tree = ET.parse(file1)
    root = tree.getroot()
    #find the first QUD-node
    qud = root.find("QUD")
    #get QUD-spans, QUD-boundaries and the number of words out of the annotation-file
    spans1, bounds1, word_id = get_QUD_spans(qud)

    #Read file2
    tree = ET.parse(file2)
    root = tree.getroot()
    #find the first QUD-node
    qud = root.find("QUD")
    #get QUD-spans, QUD-boundaries and the number of words out of the annotation-file
    spans2, bounds2, word_id = get_QUD_spans(qud, [], [], 0)


    kappa_matrixes = dict() #key: Bounds or Trees; value: matrix that belongs to QUD-bounds or QUD-trees

    #get values for comparing only the QUD-boundaries:
    #create a (word-number x 2)-matrix
    matrix = np.zeros((word_id, 2))
    #the i-th row contains the number of annotators who have a QUD-boundary after the i-th word (first column) or not (second column)
    for i in range(word_id):
        if i in bounds1: matrix[i][0] += 1
        else: matrix[i][1] += 1
        if i in bounds2: matrix[i][0] += 1
        else: matrix[i][1] += 1
    kappa_matrixes["Bounds"] = matrix

    #get values for comparing the whole QUD-trees:
    #total number of possible QUD-spans
    row_nr = int(word_id*(word_id+1)/2)
    #create a (span-number x 2)-matrix
    matrix = np.zeros((row_nr, 2))
    x = 0
    row = 0
    while x < word_id:
        #the i-th row contains the number of annotators who assigned the i-th word-span as QUD (first column) or not (second column)
        for i in range(x, word_id):
            if (x, i) in spans1: matrix[row][0] += 1
            else:  matrix[row][1] += 1
            if (x, i) in spans2: matrix[row][0] += 1
            else:  matrix[row][1] += 1
            row += 1
        x += 1
    kappa_matrixes["Trees"] = matrix


    alpha_matrixes = dict() #key: Bounds or Trees; value: matrix that belongs to QUD-bounds or QUD-trees

    #get values for comparing only the QUD-boundaries:
    #create a (2 x 2)-matrix
    matrix = np.zeros((2, 2))
    #row 1 contains the number of words after that both annotators (first column) or only annotator 1 (second column) have a QUD-boundary
    #row 2 contains the number of words after that only annotator 2 (first column) or no annotator (second column) has a QUD-boundary
    for i in range(word_id):
        if i in bounds1:
            if i in bounds2: matrix[0][0] += 2
            else: matrix[0][1] += 1
        else:
            if i in bounds2: matrix[0][1] += 1
            else: matrix[1][1] += 2
    matrix[1][0] = matrix[0][1]
    alpha_matrixes["Bounds"] = matrix

    #get values for comparing the whole QUD-trees:
    #create a (2 x 2)-matrix
    matrix = np.zeros((2, 2))
    #row 1 contains the number of spans that both annotators (first column) or only annotator 1 (second column) assigned with a QUD-tag
    #row 2 contains the number of spans that only annotator 2 (first column) or no annotator (second column) assigned with a QUD-tag
    for span in spans1:
        if span in spans2: matrix[0][0] += 2
        else: matrix[0][1] += 1
    for span in spans2:
        if span not in spans1: matrix[0][1] += 1
    matrix[1][0] = matrix[0][1]
    sum = np.sum(matrix)
    matrix[1][1] = 2*row_nr - sum
    alpha_matrixes["Trees"] = matrix

    return kappa_matrixes, alpha_matrixes, word_id, row_nr

########################

def calculate_kappa(matrix, n, s, w):
    #Function that calculates Fleiss' Kappa.
    #Input: matrix with the annotation-values, number of annotators, number of tags, number of words
    #Output: Kappa (value between 0 and 1)

    #calculate P_a (agreement probability)
    sum_rows = 0
    for i in range(w): #iterate over rows
        sum_cols = 0
        for j in range(s): #iterate over columns
            sum_cols += matrix[i][j]*(matrix[i][j] - 1)
        sum_rows += sum_cols/(n*(n - 1))
    P_a = sum_rows / w

    #calculate P_c (agreement by chance)
    sum_cols = 0
    for j in range(s): #iterate over columns
        sum_rows = 0
        for i in range(w): #iterate over rows
            sum_rows += matrix[i][j]/(n*w)
        sum_cols += sum_rows*sum_rows
    P_c = sum_cols

    #calculate Kappa
    kappa = round((P_a - P_c)/(1 - P_c), 3)

    return kappa

########################

def calculate_alpha(matrix, n, w):
    #Function that calculates Krippendorff's Alpha.
    #Input: matrix with the annotation-values, number of annotators, number of words
    #Output: Alpha (value between 0 and 1)

    #calculate P_d (disagreement probability)
    P_d = matrix[1][0] / (n*(n-1)*w)

    #calculate P_c (disagreement by chance)
    sum_rows = np.sum(matrix, axis=1)
    tag1 = sum_rows[0] #total number of tag1
    tag2 = sum_rows[1] #total number of tag2
    P_c = 2*tag1*tag2 / (w*n*(w*n-1))

    #calculate alpha
    alpha = round(1 - P_d/P_c, 3)

    return alpha

########################

if __name__ == "__main__":

    #input files
    file1= input("Please give the path of the first annotation-file: ")
    file2= input("Please give the path of the second annotation-file: ")

    #get values for all tags - except of QUD-tags - out of the files
    w, kappa_matrixes, alpha_matrixes = read_files(file1, file2)

    #metrics can only be calculated if both files consists of exactly the same words
    if not kappa_matrixes:
        print("The files don't have the same word number: file1 has " + str(w[0]) + ", file2 has " + str(w[1]) + " words.")

    else:
        #calculate kappa for each tag
        kappas = dict()
        for tag in kappa_matrixes:
            #if a tag is not used at all, value is "NA"
            if isinstance(kappa_matrixes[tag], str) and kappa_matrixes[tag] == "NA":
                kappas[tag] = "NA"
            else:
                kappas[tag] = calculate_kappa(kappa_matrixes[tag], 2, 2, w)

        #calculate alpha for each tag
        alphas = dict()
        for tag in alpha_matrixes:
            #if a tag is not used at all, value is "NA"
            if isinstance(alpha_matrixes[tag], str) and alpha_matrixes[tag] == "NA":
                alphas[tag] = "NA"
            else:
                alphas[tag] = calculate_alpha(alpha_matrixes[tag], 2, w)

        #calculate kappa and alpha for QUD-tags (on word level)
        qud_kappa_matrixes, qud_alpha_matrixes, w1, w2 = read_qud_tags(file1, file2)
        kappas["QUD-Bounds"] = calculate_kappa(qud_kappa_matrixes["Bounds"], 2, 2, w1)
        kappas["QUD-Trees"] = calculate_kappa(qud_kappa_matrixes["Trees"], 2, 2, w2)
        alphas["QUD-Bounds"] = calculate_alpha(qud_alpha_matrixes["Bounds"], 2, w1)
        alphas["QUD-Trees"] = calculate_alpha(qud_alpha_matrixes["Trees"], 2, w2)

        #Output
        print("Kappas: ", kappas)
        print("Alphas: ", alphas)


"""