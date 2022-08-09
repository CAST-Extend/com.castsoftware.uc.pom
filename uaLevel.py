import cast_upgrade_1_6_13 # @UnusedImport
import cast.analysers.ua
from cast.analysers import log, create_link
import xml.etree.ElementTree as ET

class PomProject:
    def __init__(self, uaObject, parentArtifactId, parentGroupId):
        self.uaObject = uaObject
        self.parentArtifactId = parentArtifactId
        self.parentGroupId = parentGroupId
        #todo dependencies?

class PomParser(cast.analysers.ua.Extension):
    def __init__(self):
        self.linkCount = 0
        self.pomProjects = {}
        self.pomParentProjects = {}
        self.project = None

    def start_analysis(self):
        log.info('Starting Pom extension...')
    
    def end_analysis(self):
        log.info("Ending Pom extension...")
        for pomProject in self.pomProjects.values():
            parentFullName = '%s.%s' % (pomProject.parentGroupId, pomProject.parentArtifactId)
            log.info(parentFullName)
            if parentFullName in self.pomProjects:
                parentPom = self.pomProjects[parentFullName]
            else:
                if parentFullName in self.pomParentProjects:
                    parentPom = self.pomParentProjects[parentFullName]
                else:
                    obj = cast.analysers.CustomObject()
                    obj.set_name(pomProject.parentArtifactId)
                    obj.set_fullname(parentFullName)
                    obj.set_type('POMProject')
                    obj.set_parent(self.project)
                    obj.save()
                    obj.save_property('POM_Properties.groupId', pomProject.parentGroupId)
                    
                    parentPom = PomProject(obj, '', '')
                    self.pomParentProjects[parentFullName] = parentPom
            
            #create relyOn link
            create_link("relyonLink", pomProject.uaObject, parentPom.uaObject)
            self.linkCount += 1
        
        log.info('Pom.xml: %d' % len(self.pomProjects))
        log.info('Links: %d' % self.linkCount)
        
    def start_file(self, file):
        if file.get_name().lower() != 'pom.xml':
            return
        
        if self.project == None:
            self.project = file.get_project()
        
        log.info("Parsing %s ..." % file.get_path().lower());
        tree = ET.parse(file.get_path(), ET.XMLParser(encoding="UTF-8"))
        root = tree.getroot()
        
        #1st level should have name, artifactId
        #and maybe groupId and parent
        name = ''
        artifactId = ''
        groupId = ''
        parentArtifactId = ''
        parentGroupId = ''
        
        for a in root:
            if a.tag.find('}') == -1:
                tag = a.tag
            else:
                tag = a.tag.split('}')[1]
                
            if tag == 'name':
                name = a.text
            if tag == 'artifactId':
                artifactId = a.text
            if tag == 'groupId':
                groupId = a.text
            if tag == 'parent':
                for b in a:
                    if b.tag.find('}') == -1:
                        tag = b.tag
                    else:
                        tag = b.tag.split('}')[1]
                    
                    if tag == 'artifactId':
                        parentArtifactId = b.text
                    if tag == 'groupId':
                        parentGroupId = b.text
        
        if groupId == '':
            if parentGroupId == '':
                log.warning('Could not find groupId in project or in parent!')
            else:
                groupId = parentGroupId
        
        fullName = '%s.%s' % (groupId, artifactId)
        obj = cast.analysers.CustomObject()
        obj.set_name(artifactId)
        obj.set_fullname(fullName)
        obj.set_type('POMProject')
        obj.set_parent(file)
        obj.save()
        obj.save_property('POM_Properties.displayName', name)
        obj.save_property('POM_Properties.groupId', groupId)
        obj.save_property('POM_Properties.fileName', file.get_path().lower())
        
        if fullName in self.pomProjects:
            log.warning('Duplicate pom found: %s [%s]' % (fullName, file.get_path().lower()))
        else:
            self.pomProjects[fullName] = PomProject(obj, parentArtifactId, parentGroupId)
