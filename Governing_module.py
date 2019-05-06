from Topic_collection_module import TopicCollection
from Lookup_module import ArrangeDatabase, ConvertWorkbook, GeneralTemplates, GameCourseTemplates, GameStatisticsTemplates
from Template_selection_module import GeneralTemplateSelection, GameCourseTemplateSelection, GameStatisticsTemplateSelection
from Template_filler_module import TemplateReplacement
from Text_collection_module import TextCollection
import pickle
import json

def GeneralEvents():
    #General events in the current system consist of three sentences: a title, a general sentence describing whether the focus team won/tied/lost,
    #A general sentence detailing the final score.
    return ['title', 'general', 'final_score']

def TopicWalk(file):
    # The game data is important for many rules in the RuleSet, for getting the right databases, and much more
    with open(file, 'rb') as f:
        jsongamedata = json.load(f)    


    topics = TopicCollection(jsongamedata)
    #Get three lists for the three paragraphs the current system uses: General, Game Course and Game Statistics
    general, gamecourse, gamestatistics = (GeneralEvents(),) + topics
    if len(gamestatistics) == 0:
        gamestatistics = [{'event': None}]

    # Get the right databases for the home and away report
    homedbtuple, awaydbtuple, neutraldbtuple = ArrangeDatabase(jsongamedata)
    # Get all the templates and categories
    homelegend, hometemplates = ConvertWorkbook(homedbtuple[0])
    awaylegend, awaytemplates = ConvertWorkbook(awaydbtuple[0])
    neutrallegend, neutraltemplates = ConvertWorkbook(neutraldbtuple[0])


    # Collect all the home, away and neutral templates
    templatehomelist = []
    templateawaylist = []
    templateneutrallist = []
    #Get all possible topics for general first
    for generaltopic in general:
        possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral = GeneralTemplates(generaltopic, homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates)
        #Select a template for the home team
        templatehome = GeneralTemplateSelection(generaltopic, possiblelegendhome, possibletemplateshome, gamecourse, gamestatistics, jsongamedata, 'home')
        templatehomelist.append(templatehome)
        #And a template for the away team
        templateaway = GeneralTemplateSelection(generaltopic, possiblelegendaway, possibletemplatesaway, gamecourse, gamestatistics, jsongamedata, 'away')
        templateawaylist.append(templateaway)
        #And a template for the neutral version
        templateneutral = GeneralTemplateSelection(generaltopic, possiblelegendneutral, possibletemplatesneutral, gamecourse, gamestatistics, jsongamedata, 'home')
        templateneutrallist.append(templateneutral)

    pdb.set_trace()
    #Get a separate gamecoursehome, away and neutral, since the gamecourselist can be modified
    gamecoursehome = gamecourse.copy()
    gamecourseaway = gamecourse.copy()
    gamecourseneutral = gamecourse.copy()

    # And then for the gamecourse
    for idx, gamecoursetopic in enumerate(gamecourse):
        #The subsequent goals template merges events and shortens the gamecourse, so only look for a template if there is the need for it in the gamecourselist
        if idx < len(gamecoursehome):
            possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral = GameCourseTemplates(gamecoursehome[idx], homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates)
            gamecoursehome, templatehome = GameCourseTemplateSelection(gamecoursehome[idx], possiblelegendhome, possibletemplateshome, gamecoursehome, jsongamedata, 'home', idx, templatehomelist)
            templatehomelist.append(templatehome)
        if idx < len(gamecourseaway):
            possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral = GameCourseTemplates(gamecourseaway[idx], homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates)
            gamecourseaway, templateaway = GameCourseTemplateSelection(gamecourseaway[idx], possiblelegendaway, possibletemplatesaway, gamecourseaway, jsongamedata, 'away', idx, templateawaylist)
            templateawaylist.append(templateaway)
        if idx < len(gamecourseneutral):
            possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral = GameCourseTemplates(gamecourseneutral[idx], homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates)
            gamecourseneutral, templateneutral = GameCourseTemplateSelection(gamecourseneutral[idx], possiblelegendneutral, possibletemplatesneutral, gamecourseneutral, jsongamedata, 'home', idx, templateneutrallist)
            templateneutrallist.append(templateneutral)
    #And then for the game statistics
    for idx, gamestatisticstopic in enumerate(gamestatistics):
        #If this is not the first yellow card/twice yellow card in the list, than the event is already covered and altered by the previous event
        #So, if the eventtype is not a dict, skip it
        if type(gamestatistics[idx]) == dict:
            possiblelegendhome, possibletemplateshome, possiblelegendaway, possibletemplatesaway, possiblelegendneutral, possibletemplatesneutral = GameStatisticsTemplates(gamestatisticstopic, homelegend, hometemplates, awaylegend, awaytemplates, neutrallegend, neutraltemplates)
            templatehome = GameStatisticsTemplateSelection(gamestatistics[idx], possiblelegendhome, possibletemplateshome, gamestatistics, jsongamedata, 'home', idx, templatehomelist)
            templatehomelist.append(templatehome)
            templateaway = GameStatisticsTemplateSelection(gamestatistics[idx], possiblelegendaway, possibletemplatesaway, gamestatistics, jsongamedata, 'away', idx, templateawaylist)
            templateawaylist.append(templateaway)
            templateneutral = GameStatisticsTemplateSelection(gamestatistics[idx], possiblelegendneutral, possibletemplatesneutral, gamestatistics, jsongamedata, 'home', idx, templateneutrallist)
            templateneutrallist.append(templateneutral)

    # Save the templatelist, which you can use to get new templates every iteration
    with open('templateshome.p', 'wb') as f:
        pickle.dump(templatehomelist, f)
    with open('templatesaway.p', 'wb') as f:
        pickle.dump(templateawaylist, f)
    with open('templatesneutral.p', 'wb') as f:
        pickle.dump(templateneutrallist, f)

    #Filter out all the empty strings from gamestatistics
    gamestatistics = list(filter(None, gamestatistics))
    alleventshome = general + gamecoursehome + gamestatistics
    alleventsaway = general + gamecourseaway + gamestatistics
    alleventsneutral = general + gamecourseneutral + gamestatistics
    previousgaplisthome = [''] * len(templatehomelist)
    for idx, val in enumerate(templatehomelist):
        if idx <= 1:
            lastgaphome = []
        else:
            lastgaphome = previousgaplisthome[idx - 1]
        templatehomelist[idx], previousgaplisthome[idx] = TemplateReplacement(jsongamedata, 'home', templatehomelist[idx], event=alleventshome[idx], gamecourselist=gamecoursehome, previousgaplist=lastgaphome, gamestatisticslist=gamestatistics, eventlist=alleventshome, idx=idx)
    templatetexthome, templatedicthome = TextCollection(templatehomelist, jsongamedata, 'home', len(general), len(gamecoursehome), len(gamestatistics))

    previousgaplistaway = [''] * len(templateawaylist)
    for idx, val in enumerate(templateawaylist):
        if idx <= 1:
            lastgapaway = []
        else:
            lastgapaway = previousgaplistaway[idx - 1]
        templateawaylist[idx], previousgaplistaway[idx] = TemplateReplacement(jsongamedata, 'away', templateawaylist[idx], event=alleventsaway[idx],
                                                                          gamecourselist=gamecourseaway, previousgaplist=lastgapaway,
                                                                          gamestatisticslist=gamestatistics, eventlist=alleventsaway, idx=idx)
    templatetextaway, templatedictaway = TextCollection(templateawaylist, jsongamedata, 'away', len(general), len(gamecourseaway), len(gamestatistics))

    previousgaplistneutral = [''] * len(templateneutrallist)
    for idx, val in enumerate(templateneutrallist):
        if idx <= 1:
            lastgapneutral = []
        else:
            lastgapneutral = previousgaplistneutral[idx - 1]
        templateneutrallist[idx], previousgaplistneutral[idx] = TemplateReplacement(jsongamedata, 'home', templateneutrallist[idx], event=alleventsneutral[idx],
                                                                              gamecourselist=gamecourseneutral, previousgaplist=lastgapneutral,
                                                                              gamestatisticslist=gamestatistics, eventlist=alleventsneutral, idx=idx)
    templatetextneutral, templatedictneutral = TextCollection(templateneutrallist, jsongamedata, 'neutral', len(general), len(gamecourseneutral), len(gamestatistics))

    templatedict = {'home_team': templatedicthome.copy()}
    templatedict.update({'away_team': templatedictaway})
    templatedict.update({'neutral': templatedictneutral})
    return templatetexthome, templatetextaway, templatetextneutral, templatedict, jsongamedata