import cast_upgrade_1_6_13 # @UnusedImport
from cast.application import ApplicationLevelExtension, create_link
import logging

class ApplicationExtension(ApplicationLevelExtension):        
    def start_application(self, application):
        logging.info('Starting Pom Application Level Processing...')

    def end_application(self, application):
        logging.info('Ending Pom Application Level Processing...')
        #todo logical links
        
        #Pom project found?
        #logging.info('Is the extension used properly?')
        pomProjectFound = False
        for pro in application.get_projects(): #POMCASTProject
            #logging.info('Is %s the project we are looking for?' % pro.get_type())
            if pro.get_type() == 'POMCASTProject':
                pomProjectFound = True
                break
            
        if not pomProjectFound:
            logging.error('No POM Analysis Unit found! For this extension to work, manually add a universal analysis Unit for language "POM"')
        
        logging.info('Loading POM Projects...')
        pomProjects = {}
        for pomProject in application.search_objects(category='POMProject', load_properties=True):
            projectDisplayName = pomProject.get_property('POM_Properties.displayName')
            if projectDisplayName is not None:          
                pomProjects[projectDisplayName] = pomProject
        logging.info('%d pom projects loaded' % len(pomProjects))
        
        #JV_CLASS JV_INTERFACE JV_METHOD
        #for javaObj in application.search_objects(category='JV_CLASS'):
        #    logging.info('%s -> %s' % (javaObj.get_name(), javaObj.get_project()))
        linkCount = 0
        for pro in application.get_projects():
            if pro.get_type() == 'JV_PROJECT':
                javaProjectName = pro.get_name().split('_')[1]
                if javaProjectName in pomProjects:
                    #logging.info('Project: %s' % javaProjectName)
                    currentProject = pomProjects[javaProjectName]
                    for javaObject in pro.get_objects():
                        if javaObject.get_type() != 'JV_PACKAGE':
                            #logging.info('%s [%s]' % (javaObject.get_fullname(), javaObject.get_type()))
                            create_link("referLink", javaObject, currentProject)
                            linkCount += 1
                else:
                    logging.warning('Project %s not found!' % javaProjectName)
                
        logging.info('Link Count: %d' % linkCount)