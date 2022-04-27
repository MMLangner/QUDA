# QUDA Tool models 
# (c) Maurice Langner, Linguistics, RUB




from django.db import models
from django.template import Context, Template, loader
import uuid
import xml.etree.ElementTree as et
from django.views.static import serve
from io import StringIO





class PLAIN:
    def __init__(self, txt):
        self.text = txt

    def toHTML(self, request):
        template = loader.get_template("viewer/plain.html")

        context = {"plaintext":self.text}
        return template.render(context, request)




class Document:
    def __init__(self, config, XMLroot):
        self.root = XMLroot
        self.rootqud = self.parse(config, self.root)
        #self.rootqud[0].printData()
        self.identifyQUD()


    def getAllUnclassifiedSegments(self, rqud, arr):
        if rqud.type == "QUD":
            for subU in rqud.subUnits:
                self.getAllUnclassifiedSegments(subU, arr)
        else:
            for segm in rqud.subsegments:
                if segm.classification == "":
                    arr.append(segm.idn)



    

    def findByID(self, someObj, idnn, previous=None):

        if someObj.type == "QUD":

            print("IDN found: ",someObj.idn)
            print("IDN in search: ", idnn)
            if someObj.idn == idnn:
                return someObj, previous
            else:
                for subq in someObj.subUnits:
                    subqBool, subqPrev = self.findByID(subq, idnn, someObj)
                    if subqBool:
                        return subqBool, subqPrev

                for segm in someObj.subUnits:
                    subSBool, subSPrev = self.findByID(segm, idnn, someObj)
                    if subSBool:
                        return subSBool, subSPrev
            
            return False, False

        else:
            if someObj.idn == idnn:
                return someObj, previous
            else:
                for segm in someObj.subsegments:
                    subSBool, subSPrev = self.findByID(segm, idnn, someObj)
                    if subSBool:
                        return subSBool, subSPrev
            
            return False, False



    def findQUD(self, someObj, idnn):
        
        if someObj.type == "QUD":

            if someObj.identifier == idnn:
                return someObj
            else:
                for subq in someObj.subUnits:
                    subidn = self.findQUD(subq, idnn)
                    if subidn:
                        return subidn
        return False




    def parse(self, config, root):
        allquds = []
        for elem in root:
            if elem.tag == "QUD":
                this_q = QUD(elem.get("string"), elem)
                this_q.classification = elem.get("classification")
                #this_q.subUnits = self.parse("testconfig", elem)
                this_q.parseSubUnits(elem)
                allquds.append(this_q)
            else:
                continue
                #self.parse("testconfig", elem)
        return allquds

    def toHTML(self, request):
        htmlmarkup = self.rootqud[0].toHTML(request)
        return htmlmarkup
        

    def identifyQUD(self):
        i = 0
        ident = "Q." + str(i)
        if len(self.rootqud) == 0:
            return 0
        self.rootqud[0].identifier = ident
        i += 1
        print(ident)
        for subq in self.rootqud[0].subUnits:
            if subq.type == "QUD":
                self.recursiveIdentifying(subq, i,  None)
                i += 1

    
    def toXML(self):
        root = et.Element("ROOT")
        rootqud = et.SubElement(root, "QUD", string=self.rootqud[0].qudForm, classification=self.rootqud[0].classification)

        #for subseg in self.rootqud[0].segList:
        #    subsgm = subseg.toXML(rootqud)

        for subqud in self.rootqud[0].subUnits:
            subq = subqud.toXML(rootqud)
        

        tree = et.ElementTree(root)
        #file_obj = StringIO(et.tostring(root))
        #print(et.tostring(root))
        #return file_obj
        #tree.write("result.xml")
        return et.tostring(root, "utf-8").decode("utf-8")

    def recursiveIdentifying(self, qud, i, previous):

        j = 1
        print("recursive call")
        if previous == None:
            ident = "Q." + str(i)
            qud.identifier = ident
            print(ident)
            for q in qud.subUnits:
                if q.type == "QUD":
                    self.recursiveIdentifying(q, j, ident)
                    j += 1
        else:
            ident = previous + "." + str(i)
            qud.identifier = ident
            print(ident)
            for q in qud.subUnits:
                if q.type == "QUD":
                    self.recursiveIdentifying(q, j, ident)
                    j += 1


class QUD:
    def __init__(self,string, subtree):
        self.type = "QUD"
        self.identifier = ""
        self.subtree = subtree
        self.qudForm = string
        self.subUnits = [] #+ self.parseElems(subtree, [])
        self.idn = str(uuid.uuid4())
        self.classification = "QUD"



    def parseSubUnits(self, subtree):
        
        labels = ["AT","CT", "DT", "F", "CMT", "CON", "NAI", "RES"]

        for unit in subtree:

            if unit.tag == "QUD":
                subq = QUD(unit.get("string"), unit)
                subq.classification = unit.get("classification")
                subq.parseSubUnits(unit)
                self.subUnits.append(subq)
            
            elif unit.tag == "UNIT" or unit.tag == "OVERT":
                
                du = DISCOURSE_UNIT(unit.text)
                du.parseSubSegments(unit)
                du.classification = unit.tag
                self.subUnits.append(du)

            elif unit.tag in labels:
                seg = SEGMENT(unit.text)
                seg.classification = unit.tag
                seg.parseSubSegments(unit)
                self.subsegments.append(seg)
            







    def printData(self):
        print("QUD: ", self.qudForm)

        for qud in self.subUnits:
            if qud.type == "QUD":
                qud.printData()
            else:
                qud.printSegment()
        
        


    def toXML(self, superqud):
        this_subq = et.SubElement(superqud, "QUD", string = self.qudForm, classification = self.classification)
        
        for sq in self.subUnits:
            sq.toXML(this_subq)

        




    def parse(self):
        listing = self.recurse(self.subtree, "SEGMENT", "QUD")
        listing = [SEGMENT(x) for x in listing]
        #print(listing)
        return listing

    
    # def parseElems(self, root, parent):
    #     allSegments = []
    #     previous = False
    #     labels = ["AT","CT", "DT", "F", "CMT", "CON", "NAI", "RES"]
    #     for elem in root:
    #         if elem.tag in labels:

    #             previous = True
    #             this_seg = SEGMENT("")
    #             this_seg.classification = elem.tag
    #             this_seg.subsegments = self.parseElems(elem, [this_seg])
    #             allSegments.append(this_seg)

                
    #         elif elem.tag == "SEGMENT":
    #             if len(parent) == 1:
    #                 if previous:
                    
    #                     sec_seg = SEGMENT("")
    #                     sec_seg.classification = parent[0].classification
    #                     sec_seg.text = elem.text
    #                     sec_seg.subsegments = self.parseElems(elem, [sec_seg])
    #                     previous = False
    #                     allSegments.append(sec_seg)
                    
    #                 else:
    #                     parent[0].text += elem.text
    #                     parent[0].subsegments = self.parseElems(elem, [parent[0]])
    #             elif len(parent) == 0:
    #                 print("ERROR")
    #         else:
    #             continue
            
    #         #for subelem in elem:
    #         #    self.parseElems(subelem, [this_seg])
            

    #     return allSegments
        

    def parseElems(self, root, parent):
        allSegments = []
        labels = ["AT","CT", "DT", "F", "CMT", "CON", "NAI", "RES"]
        for elem in root:
            if elem.tag in labels:
                i = 0
                indexlist = []
                sgmts = {}
                for subelem in elem:
                    sgmts[i] = subelem
                    if subelem.tag == "SEGMENT":
                        indexlist.append(i)
                    i += 1


                if len(indexlist) > 0:
                    for s in range(0, indexlist[0]):
                        this_seg = SEGMENT("")
                        this_seg.classification = sgmts[indexlist[s]].tag
                        this_seg.text = sgmts[indexlist[s]].text
                        this_seg.subsegments += self.deepparse(sgmts[s], [this_seg])
                        allSegments.append(this_seg)




                for ind in range(len(indexlist)):

                    this_seg = SEGMENT("")
                    this_seg.classification = elem.tag
                    this_seg.text = sgmts[indexlist[ind]].text
                    #print(sgmts[indexlist[ind]].text)
                    try:    
                        for s in range(indexlist[ind], indexlist[ind+1]):
                            this_seg.subsegments += self.deepparse(sgmts[s], [this_seg])
                        allSegments.append(this_seg)
                    except:
                        for s in range(indexlist[ind], len(elem.getchildren())):
                            this_seg.subsegments += self.deepparse(sgmts[s], [this_seg])
                        allSegments.append(this_seg)
                
            else:
                continue
            
            #for subelem in elem:
            #    self.parseElems(subelem, [this_seg])
            

        return allSegments


    def deepparse(self, elem, parent):
        labels = ["AT","CT", "DT", "F", "CMT", "CON", "NAI", "RES"]
        allSegments = []
        if elem.tag in labels:
            i = 0
            indexlist = []
            sgmts = {}
            for subelem in elem:
                sgmts[i] = subelem
                if subelem.tag == "SEGMENT":
                    indexlist.append(i)
                i += 1
            
            if len(indexlist) > 0:
                for s in range(0, indexlist[0]):
                    this_seg = SEGMENT("")
                    this_seg.classification = sgmts[indexlist[s]].tag
                    this_seg.text = sgmts[indexlist[s]].text
                    this_seg.subsegments += self.deepparse(sgmts[s], [this_seg])
                    allSegments.append(this_seg)

            for ind in range(len(indexlist)):

                this_seg = SEGMENT("")
                this_seg.classification = elem.tag
                this_seg.text = sgmts[indexlist[ind]].text
                try:    
                    for s in range(indexlist[ind], indexlist[ind+1]):
                        this_seg.subsegments += self.deepparse(sgmts[s], [this_seg])
                    
                except:
                    for s in range(indexlist[ind], len(elem.getchildren())):
                        this_seg.subsegments += self.deepparse(sgmts[s], [this_seg])
                
                allSegments.append(this_seg)

            
        else:
            pass
        return allSegments



    
    # def parseElems(self, root):
    #     allSegments = []
    #     labels = ["AT","CT", "DT", "F", "CMT", "CON", "NAI", "RES"]
    #     for elem in root:
    #         if elem.tag in labels:
    #             this_seg = SEGMENT("")
    #             this_seg.classification = elem.tag
    #             for subelem in elem:
    #                 if subelem.tag == "SEGMENT":
    #                     this_seg.text += subelem.text
    #                     this_seg.subsegments += self.parseElems(subelem)
                
    #                 else:
    #                     this_seg.subsegments += self.parseElems(subelem)
                
    #             allSegments.append(this_seg)
                
    #         else:
    #             continue

            
    #     return allSegments    



    def recurse(self, root, get, block):
        allnodes = []
        
        #print(len(root))
        for elem in root:
            #print(elem.tag)
            if elem.tag == get:
                allnodes.append(elem.text)
            elif elem.tag == block:
                continue
            else:
                allnodes += self.recurse(elem, get, block)
        return allnodes

    def joinSegments(self):
        if len(self.subUnits) > 0:
            allsegments = ""
            for seg in self.subUnits:
                if seg.type == "SEGMENT":
                    allsegments += seg.text
            this_seg = SEGMENT(allsegments)
            self.subUnits += [this_seg]
        else:
            pass


    def toHTML(self, request):
        #self.joinSegments()
        template = loader.get_template("viewer/qud.html")
        #context = {"string":self.text}
        #return template.render(context)
        subunit_markup = ""
       
        for subunit in self.subUnits:
            subunit_markup += (subunit.toHTML(request) + "\n")

        context = {"name":str(self.idn), "idn":str(self.idn), "idn_del":str(self.idn)+"_del","qud":self.qudForm, "qud_class":self.classification, "ident":self.identifier,
        "deepembed":subunit_markup}
        return template.render(context, request)


class DISCOURSE_UNIT:
    def __init__(self, string):
        self.type = "SEGMENT"
        self.subtype = "discourse_unit"
        self.text = string
        self.idn = str(uuid.uuid4())
        self.classification = "UNIT"
        self.subsegments = []
        self.identifier = ""
    

    def parseSubSegments(self, subtree):
        for segm in subtree:
            
            seg = SEGMENT(segm.text)
            seg.classification = segm.tag
            seg.parseSubSegments(segm)
            self.subsegments.append(seg)


    def toXML(self, superElem):
        
        this_seg = et.SubElement(superElem, self.classification)

        this_seg.text = self.text

        for subseg in self.subsegments:
            subseg.toXML(this_seg)


    def printSegment(self): #, depth):
        print("class: ", self.classification)
        print("string: ", self.text)
        #depth += 1

        for subseg in self.subsegments:
            subseg.printSegment()

    def toHTML(self, request):
        template = loader.get_template("viewer/segment.html")
        subtags = ""
        if len(self.subsegments) > 0:
            for subelem in self.subsegments:
                subtags += (subelem.toHTML(request) + "\n")
        #print(subtags)   
        context = {"segment":self.text, "name":str(self.idn), "idn":str(self.idn), "idn_del":str(self.idn)+"_del", "wraplabel":str(self.classification), "COL":str(self.classification), "wrapid":self.identifier, "deepembedseg":subtags, "menutype":"discourse"}
        return template.render(context, request)


class SEGMENT(DISCOURSE_UNIT):
    def __init__(self, string):
        super().__init__(string)
        self.classification = ""
        self.type = "SEGMENT"
        self.subtype = "segment"
    
    def toXML(self, superElem):
        
        this_seg = et.SubElement(superElem, self.classification)

        this_seg.text = self.text

        for subseg in self.subsegments:
            subseg.toXML(this_seg)


    def toHTML(self, request):
        template = loader.get_template("viewer/segment.html")
        subtags = ""
        if len(self.subsegments) > 0:
            for subelem in self.subsegments:
                subtags += (subelem.toHTML(request) + "\n")
        #print(subtags)   
        context = {"segment":self.text, "name":str(self.idn), "idn":str(self.idn), "idn_del":str(self.idn)+"_del", "wraplabel":str(self.classification), "COL":str(self.classification), "wrapid":self.identifier, "deepembedseg":subtags, "menutype":"segment"}
        return template.render(context, request)
