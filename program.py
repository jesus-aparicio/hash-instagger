# =================================================
#               STORED DEPENDENCIES
# -------------------------------------------------

from PyQt5.QtWidgets import QMessageBox as alert
from PyQt5 import QtWidgets as widgets
from PyQt5 import QtGui as interface
from PyQt5 import QtCore as assets
from bs4 import BeautifulSoup as soup
import gui as form
import sys as system
import time
import random
import os

# =================================================
#                 STATIC REFERENCE
# -------------------------------------------------

global sys, ui, gui, hashTags, categories, types, reloading, request, requestedTopics, requestedTopicSelector, location

# =================================================
#                    STRUCTURES
# -------------------------------------------------

class Category:
    def __init__(self, tag: str = 'category'):
        self._tag = tag

    def setName(self,newName):
        self._tag = newName

    def getName(self) -> str:
        return self._tag
    
    def getTypeIntesity(self, type) -> int:
        global types, hashTags
        resolve = 0
        totalInCategory = 0
        totalInHashType = 0
        
        for hashKey in hashTags.keys():
            # print("For: " + hashKey)
            for typeKey in types.keys():
                # print("For type '" + typeKey + "' over category '" + self.getName() + "':")
                # print("Category intensity: " + str(hashTags[hashKey].getCategoryIntensity(self)))
                if int(hashTags[hashKey].getCategoryIntensity(self)) > 0:
                    # print("Type intensity: " + str(hashTags[hashKey].getTypeIntensity(types[typeKey])))
                    if int(hashTags[hashKey].getTypeIntensity(types[typeKey])) > 0:
                        # print("Product: " + str(int(hashTags[hashKey].getCategoryIntensity(self))*int(hashTags[hashKey].getCategoryIntensity(types[typeKey]))))
                        totalInCategory += int(hashTags[hashKey].getCategoryIntensity(self))*int(hashTags[hashKey].getTypeIntensity(types[typeKey]))
                        if type.getName() == types[typeKey].getName():
                            totalInHashType += int(hashTags[hashKey].getCategoryIntensity(self))*int(hashTags[hashKey].getTypeIntensity(types[typeKey]))        
        # print(str(totalInHashType))
        # print(str(totalInCategory))
        if totalInCategory > 0:
            resolve = int(100*(float(totalInHashType)/float(totalInCategory)))
        return resolve

class HashTag:
    def __init__(self, tag: str = 'hashtag'):
        self._tag = tag

        self._categories = {}
        self._types = {}

        self.setUpTypes()

    def setCategoryIntensity(self,category,intensity):
        if category.getName() in self._categories.keys():
            self._categories[category.getName()]["intensity"] = intensity
            self._categories[category.getName()]["object"] = category
            self._categories[category.getName()]["name"] = category.getName()
        else:
            self.addCategory(category,intensity)

    def setName(self,newName):
        self._tag = newName

    def setTypeIntensity(self,type,intensity):
        if type.getName() in self._types.keys():
            self._types[type.getName()]["intensity"] = int(intensity)
        else:
            pass

    def setUpTypes(self):
        global types

        for key in types.keys():
            newType = {}
            newType["name"] = types[key].getName()
            newType["intensity"] = 0
            newType["object"] = types[key]
            self._types[types[key].getName()] = newType

    def addCategory(self,category,intensity):
        resolve = False

        if self._categories.get(category.getName()):
            self._categories[category.getName()]["intensity"] = int(intensity)
            self._categories[category.getName()]["object"] = category
            self._categories[category.getName()]["name"] = category.getName()
        else:
            resolve = True
            newCategory = {}
            newCategory["name"] = category.getName()
            newCategory["intensity"] = int(intensity)
            newCategory["object"] = category
            self._categories[category.getName()] = newCategory
        return resolve
    
    def removeCategory(self, category):
        resolve = True

        if not self._categories.pop(category.getName() , False):
            resolve = False
        return resolve

    def getName(self) -> str:
        return self._tag

    def getTypeIntensity(self, type) -> int:
        resolve = 0

        if type.getName() in self._types.keys():
            resolve = int(self._types[type.getName()]["intensity"])
        return resolve

    def getType(self,type: str):
        resolve = None

        if type in self._types.keys():
            resolve = self._types[type]["object"]
        return resolve

    def getTypes(self):
        dictionary = dict()

        for index in self._types.keys():
            if 'intensity' in self._types[index].keys():
                dictionary[index] = dict()
                dictionary[index]["intensity"] = int(self._types[index]["intensity"])
                dictionary[index]["object"] = self._types[index]["object"]
                dictionary[index]["name"] = self._types[index]["object"].getName()
        return dictionary

    def getCategoryIntensity(self,category):
        response = 0

        if category.getName() in self._categories.keys():
            response = int(self._categories[category.getName()]["intensity"])
        return response

    def getCategory(self,category: str):
        global categories
        response = None

        if category in self._categories.keys() and category in categories.keys():
            response = self._categories[category]["object"]
            if int(self._categories[category]["intensity"]) == 0:
                response = None
        return response

    def getCategories(self):
        global categories
        dictionary = dict()

        for index in self._categories.keys():
            if index in categories.keys():
                if 'intensity' in self._categories[index].keys():
                    if int(self._categories[index]["intensity"]) > 0:
                        dictionary[index] = dict()
                        dictionary[index]["intensity"] = int(self._categories[index]["intensity"])
                        dictionary[index]["object"] = self._categories[index]["object"]
                        dictionary[index]["name"] = self._categories[index]["object"].getName()
        return dictionary


class Type:
    def __init__(self, tag: str = 'type'):
        self._tag = tag

    def setName(self,newName):
        self._tag = newName

    def getName(self) -> str:
        return self._tag


class Request:
    def __init__(self):
        self._categories = {}
        self._types = {}

        self._hashtags = {}
        self._size = 0
        self._values = {}

        self.setUpTypes()

    def setTypeIntensity(self,type,intensity):
        if type.getName() in self._types.keys():
            self._types[type.getName()]["intensity"] = int(intensity)
        else:
            pass
    
    def setProportionalCandidateList(self):
        global hashTags, types, ui
        value = 0
        worth = 0

        for tag in hashTags.keys():
            value = 0
            for category in self._categories.keys():
                if category in hashTags[tag].getCategories():
                    for type in types.keys():
                        if self.getTypeIntensity(types[type]) > 0:
                            value += int(float(1+float(random.randint(0,ui.spinBoxError.value()))/100)*float(self.getTypeIntensity(types[type])))
            self._values[tag] = int(value)
            worth += value
            # print(value)
        for tag in self._values.keys():
            if self._values[tag] > 0:
                self.addHashTag(hashTags[tag])
            if worth > 0:
                self._values[tag] = int(100*float(self._values[tag])/float(worth))
            # print("For '" + tag + "' the net worth is " + str(self._values[tag]) + "%")     

    def setUpTypes(self):
        for key in types.keys():
            newType = {}
            newType["name"] = types[key].getName()
            newType["intensity"] = 0
            newType["object"] = types[key]
            self._types[types[key].getName()] = newType
    
    def makeReplyBySimplyOrderingValues(self, ammount: int) -> str:
            global hashTags
            response = list()

            self.setProportionalCandidateList()
            for round in range(ammount):
                if len(self._hashtags) <= 0:
                    break
                else:
                    tagAdded = str(max(self._values, key = lambda key: self._values[key]))
                    self.deleteHashTag(hashTags[tagAdded])
                    response.append(tagAdded)
            random.shuffle(response)
            return ' '.join(response)
    
    def addCategory(self,category):
        resolve = False
        if self._categories.get(category.getName()):
            self._categories[category.getName()] = category
        else:
            resolve = True
            self._categories[category.getName()] = category
        return resolve

    def addHashTag(self,hashTag):
        resolve = False
        if self._hashtags.get(hashTag.getName()):
            self._hashtags[hashTag.getName()] = hashTag
        else:
            resolve = True
            self._hashtags[hashTag.getName()] = hashTag
        return resolve        
    
    def deleteCategory(self, category):
        resolve = True

        if not self._categories.pop(category.getName() , False):
            resolve = False
        return resolve

    def deleteHashTag(self, hashTag):
        resolve = True

        if not self._hashtags.pop(hashTag.getName() , False):
            resolve = False
        else:
            self._values.pop(hashTag.getName() , False)
        return resolve

    def getCategories(self):
        global categories
        dictionary = dict()
    
        for index in self._categories.keys():
            if index in categories.keys():
                dictionary[index] = self._categories[index]
        return dictionary
    
    def getTypeIntensity(self,type) -> int:
        response = 0
        
        if type.getName() in self._types.keys():
            response = int(self._types[type.getName()]["intensity"])
        return response

    def getTypes(self):
        dictionary = dict()

        for index in self._types.keys():
            if 'intensity' in self._types[index].keys():
                dictionary[index] = dict()
                dictionary[index]["intensity"] = int(self._types[index]["intensity"])
                dictionary[index]["object"] = self._types[index]["object"]
                dictionary[index]["name"] = self._types[index]["object"].getName()
        return dictionary

    def getHashTags(self):
        global hashTags
        dictionary = dict()
    
        for index in self._hashtags.keys():
            if hashtag in hashTags.keys():
                dictionary[index] = self._hashtags[index]
        return dictionary

# =================================================
#                  STATIC METHODS
# -------------------------------------------------

def bindEvents():
    global ui
    tag = HashTag()

    ui.pushButtonRequestsAddTopic_2.clicked.connect(lambda: ui.plainTextEditGeneratedHashTags.setPlainText(''))
    ui.pushButtonGetHashtags.clicked.connect(getHashTagsRequested)
    ui.pushButtonFileNamesLoadGroupings.clicked.connect(loadCategoriesFromFile)
    ui.pushButtonFileNamesLoadHashes.clicked.connect(loadHashTagsFromFile)
    ui.dialHashtagEditSelectedTopicIntensity.valueChanged.connect(setCategoryIntensity)
    ui.verticalSliderHashtagEditNicheValue.valueChanged.connect(setTypesIntensities)
    ui.verticalSliderPhraseValue.valueChanged.connect(setTypesIntensities)
    ui.verticalSliderLocationValue.valueChanged.connect(setTypesIntensities)
    ui.verticalSliderHashtagEditEventValue.valueChanged.connect(setTypesIntensities)
    ui.verticalSliderEmojiValue.valueChanged.connect(setTypesIntensities)
    ui.pushButtonHashtagEditAddUnrelatedTopic.clicked.connect(addCategoryToHashTag)
    ui.pushButtonHashtagEditRemoveUnrelatedTopic.clicked.connect(deleteCategoryFromHashTag)
    ui.comboBoxHashtagEditTopicsAdded.currentIndexChanged.connect(refreshHashtagEditSelectedTopicIntensity)
    ui.comboBoxHashtagEditHashTags.currentIndexChanged.connect(refreshEditedHashtag)
    ui.pushButtonHashtagEditAddUnrelatedTopic_2.clicked.connect(addNedHashTag)
    ui.pushButtonHashtagEditRemoveUnrelatedTopic_3.clicked.connect(overWriteHashTag)
    ui.pushButtonHashtagEditRemoveUnrelatedTopic_2.clicked.connect(deleteHashTag)
    ui.comboBoxTagGroupsExisting.currentIndexChanged.connect(refreshEditedCategory)
    ui.dialRequestEmoji.valueChanged.connect(setRequestTypeIntensity)
    ui.dialRequestEvent.valueChanged.connect(setRequestTypeIntensity)
    ui.dialRequestNiche.valueChanged.connect(setRequestTypeIntensity)
    ui.dialRequestPhrase.valueChanged.connect(setRequestTypeIntensity)
    ui.dialRequestPlaces.valueChanged.connect(setRequestTypeIntensity)
    ui.pushButtonRequestsAddTopic.clicked.connect(addNewCategoryToRequest)
    ui.pushButtonRequesteRemoveTopic.clicked.connect(deleteCategoryFromRequest)
    ui.pushButtonTagGroupsRemove.clicked.connect(deleteCategory)
    ui.pushButtonTagGroupsOverWrite.clicked.connect(overWriteCategory)
    ui.pushButtonTagGroupsAddNew.clicked.connect(addCategory)
    ui.pushButtonFileNamesNewGroupings.clicked.connect(saveCategories)
    ui.pushButtonFileNamesAddNewHashes.clicked.connect(saveHashTags)

def bindDisplay():
    refreshEditedCategory()
    refreshLineEditHashtagEditName()
    refreshComboBoxHashtagEditTopics()
    refreshSliderHashtagEditValues()
    refreshHashtagEditSelectedTopicIntensity()
    setRequestTypeIntensity()

def attribute():
    global gui

    gui.setFixedSize(gui.size())
    gui.setStyleSheet(" QToolTip{ white-space: pre ; font: 9pt ; font-family: Arial }")

def makeRequestedTopicsAndSelector():
    global ui, requestedTopics, requestedTopicSelector, request

    request = Request()
    requestedTopics = interface.QStandardItemModel()
    ui.listWidgetRequestedTopics.setModel(requestedTopics)
    requestedTopicSelector = ui.listWidgetRequestedTopics.selectionModel()
    ui.listWidgetRequestedTopics.setEditTriggers(widgets.QAbstractItemView.NoEditTriggers)

def makeTypes():
    global types
    types = {}
    types["emoji"] = Type("emoji")
    types["event"] = Type("event")
    types["place"] = Type("place")
    types["niche"] = Type("niche")
    types["phrase"] = Type("phrase")

def reader(filename: str):
    return soup(open(filename).read(),features="html.parser")

def getHashTagsRequested():
    global request, ui

    ui.plainTextEditGeneratedHashTags.setPlainText(request.makeReplyBySimplyOrderingValues(int(ui.lineEditExpectedTags.text())))

def setRequestTypeIntensity():
    global request, ui
    total = 0

    request.setTypeIntensity(types['emoji'],ui.dialRequestEmoji.value())
    total += ui.dialRequestEmoji.value()
    request.setTypeIntensity(types['event'],ui.dialRequestEvent.value())
    total += ui.dialRequestEvent.value()
    request.setTypeIntensity(types['place'],ui.dialRequestPlaces.value())
    total += ui.dialRequestPlaces.value()
    request.setTypeIntensity(types['phrase'],ui.dialRequestPhrase.value())
    total += ui.dialRequestPhrase.value()
    request.setTypeIntensity(types['niche'],ui.dialRequestNiche.value())
    total += ui.dialRequestNiche.value()
    if total > 0:
        ui.labelRequestPercentEmoji.setText(str(int(100*float(ui.dialRequestEmoji.value())/float(total)))+"%")
        request.setTypeIntensity(types['emoji'],int(100*float(ui.dialRequestEmoji.value())/float(total)))
        ui.labelRequestPercentEvent.setText(str(int(100*float(ui.dialRequestEvent.value())/float(total)))+"%")
        request.setTypeIntensity(types['event'],int(100*float(ui.dialRequestEvent.value())/float(total)))
        ui.labelRequestPercentPlaces.setText(str(int(100*float(ui.dialRequestPlaces.value())/float(total)))+"%")
        request.setTypeIntensity(types['place'],int(100*float(ui.dialRequestPlaces.value())/float(total)))
        ui.labelRequestPercentPhrase.setText(str(int(100*float(ui.dialRequestPhrase.value())/float(total)))+"%")
        request.setTypeIntensity(types['phrase'],int(100*float(ui.dialRequestPhrase.value())/float(total)))
        ui.labelRequestPercentNiche.setText(str(int(100*float(ui.dialRequestNiche.value())/float(total)))+"%")
        request.setTypeIntensity(types['niche'],int(100*float(ui.dialRequestNiche.value())/float(total)))

def setItemSelectedInCombo(text: str, comboBox):
    index = int(comboBox.findText(text, assets.Qt.MatchFixedString))
    
    if index >= 0:
        comboBox.setCurrentIndex(index)
        print(comboBox.currentText())

def setCategoryIntensity():
    global categories, ui

    if ui.comboBoxHashtagEditHashTags.currentText() != "" and ui.comboBoxHashtagEditTopicsAdded.currentText() != '':
        if ui.comboBoxHashtagEditHashTags.currentText() in hashTags.keys():
            # print("Current text is: '"+ui.comboBoxHashtagEditHashTags.currentText()+"'.")
            # integer = int(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getCategories()[ui.comboBoxHashtagEditTopicsAdded.currentText()]["intensity"])
            # print("Integer is: "+str(integer))
            hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setCategoryIntensity(categories[ui.comboBoxHashtagEditTopicsAdded.currentText()], ui.dialHashtagEditSelectedTopicIntensity.value())
    refreshHashtagEditSelectedTopicIntensity()
    refreshEditedCategory()

def setGreenBarAndPercent(type, value: int):
    global ui
    greenBar = False
    percent = False

    if type == "emoji":
        greenBar = ui.progressBar
        percent = ui.labelTagGroupsPercentEmoji
    elif type == "event":
        greenBar = ui.progressBarEvent
        percent = ui.labelTagGroupsPercentEvent
    elif type == "phrase":
        greenBar = ui.progressBarPhrase
        percent = ui.labelTagGroupsPercentPhrase
    elif type == "place":
        greenBar = ui.progressBarPlaces
        percent = ui.labelTagGroupsPercentLocation
    elif type == 'niche':
        greenBar = ui.progressBarNiche
        percent = ui.labelTagGroupsPercentNiche
    if greenBar and percent:
        greenBar.setValue(100 - value)
        percent.setText(str(value)+"%")

def setTypesIntensities():
    global types, reloading, ui

    if not reloading:
        hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setTypeIntensity(types["emoji"], int(ui.verticalSliderEmojiValue.value()))
        hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setTypeIntensity(types["niche"], int(ui.verticalSliderHashtagEditNicheValue.value()))
        hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setTypeIntensity(types["place"], int(ui.verticalSliderLocationValue.value()))
        hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setTypeIntensity(types["event"], int(ui.verticalSliderHashtagEditEventValue.value()))
        hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setTypeIntensity(types["phrase"], int(ui.verticalSliderPhraseValue.value()))

        refreshSliderPercentages()
        refreshEditedCategory()

def addCategory():
    global ui, categories

    if ui.lineEditTagGroupsNameEdited.text() not in categories.keys():
        if ui.lineEditTagGroupsNameEdited.text() != "":
            name = ui.lineEditTagGroupsNameEdited.text()
            categories[name] = Category(name)
            loadCategoriesComboBox(categories)
            bindDisplay()
            setItemSelectedInCombo(categories[name].getName(),ui.comboBoxTagGroupsExisting)

def addNewCategoryToRequest():
    global requestedTopics, request, categories, ui
    repeated = False

    for index in range(requestedTopics.rowCount()):
        if requestedTopics.item(index).text() == ui.comboBoxRequestSelectedTopics.currentText():
            repeated = True
            alert.warning(ui.profiling, 'Category Exists', "Already requesting that category", alert.Ok , alert.Ok)    
    if not repeated:
        requestedTopics.appendRow(interface.QStandardItem(ui.comboBoxRequestSelectedTopics.currentText()))
        request.addCategory(categories[ui.comboBoxRequestSelectedTopics.currentText()])

def addNedHashTag():
    global hashTags, ui
    addedTag = ui.lineEditHashtagEditName.text()

    if addedTag not in hashTags.keys():
        hashTags[addedTag] = HashTag(addedTag)
        refreshEditedHashtag()
        refreshHashTagComboBoxes()
        alert.warning(ui.handleHashtags, 'New Hashtag', "New tag '"+ addedTag +"' added", alert.Ok, alert.Ok) 
    setItemSelectedInCombo(addedTag, ui.comboBoxHashtagEditHashTags)
    

def addCategoryToHashTag():
    global hashTags, categories, ui
    newCategory = ui.comboBoxHashtagEditTopicsUrelated.currentText()

    if ui.comboBoxHashtagEditTopicsUrelated.count() > 0:
        if(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].addCategory(categories[newCategory],ui.dialHashtagEditSelectedTopicIntensity.value())):
            refreshComboBoxHashtagEditTopics()
            refreshHashtagEditSelectedTopicIntensity()
            refreshEditedCategory()
    
    setItemSelectedInCombo(newCategory, ui.comboBoxHashtagEditTopicsAdded)

def overWriteCategory():
    global ui, categories, hashTags

    if ui.lineEditTagGroupsNameEdited.text() not in categories.keys():
        if ui.lineEditTagGroupsNameEdited.text() != "":
            oldName = ui.comboBoxTagGroupsExisting.currentText()
            name = ui.lineEditTagGroupsNameEdited.text()
            categories[name] = categories[oldName]
            categories.pop(oldName)
            categories[name].setName(name)
            for hash in hashTags.keys():
                if oldName in hashTags[hash]._categories.keys():
                    if name not in hashTags[hash]._categories.keys():
                        hashTags[hash]._categories[name] = dict()
                        hashTags[hash]._categories[name]["object"] = hashTags[hash]._categories[oldName]["object"]
                        hashTags[hash]._categories[name]["intensity"] = hashTags[hash]._categories[oldName]["intensity"]
                        hashTags[hash]._categories[name]["name"] = hashTags[hash]._categories[oldName]["name"]
                        hashTags[hash]._categories[name]["object"].setName(name)      
                        hashTags[hash]._categories.pop(oldName)                  
            loadCategoriesComboBox(categories)
            bindDisplay()
            setItemSelectedInCombo(categories[name].getName(),ui.comboBoxTagGroupsExisting)

def overWriteHashTag():
    global hashTags, ui
    overWrittenTag = ui.lineEditHashtagEditName.text()

    if overWrittenTag not in hashTags.keys():
        if ui.comboBoxHashtagEditHashTags.currentText() in hashTags.keys():
            hashTags[ui.comboBoxHashtagEditHashTags.currentText()].setName(overWrittenTag)
            hashTags[overWrittenTag] = hashTags[ui.comboBoxHashtagEditHashTags.currentText()]
            hashTags.pop(ui.comboBoxHashtagEditHashTags.currentText())
            refreshEditedHashtag()
            refreshHashTagComboBoxes()
            refreshEditedCategory()
        else:
            alert.warning(ui.handleHashtags, 'Error', "Could not overwrite", alert.Ok, alert.Ok)
    else:
        alert.warning(ui.handleHashtags, 'Name Exists', "Name'" + overWrittenTag + "'already exists.", alert.Ok, alert.Ok)    
    setItemSelectedInCombo(overWrittenTag, ui.comboBoxHashtagEditHashTags)

def deleteCategory():
    global categories, ui

    if ui.comboBoxTagGroupsExisting.currentText() in categories.keys():
        categories.pop(ui.comboBoxTagGroupsExisting.currentText())
        setItemSelectedInCombo(categories[random.choice(list(categories))].getName(),ui.comboBoxTagGroupsExisting)
        loadCategoriesComboBox(categories)
        bindDisplay()

def deleteCategoryFromRequest():
    global requestedTopics, request, categories, requestedTopicSelector, ui

    if requestedTopicSelector.isSelected:
        request.deleteCategory(categories[requestedTopicSelector.currentIndex().data()])
        requestedTopics.removeRow(requestedTopicSelector.currentIndex().row())
    else:
       alert.warning(ui.handleHashtags, 'Select Category', "There is no category selected for removal.", alert.Ok, alert.Ok) 

def deleteCategoryFromHashTag():
    global hashTagsglobal, categories, ui

    if ui.comboBoxHashtagEditTopicsAdded.count() > 0:
        if hashTags[ui.comboBoxHashtagEditHashTags.currentText()].removeCategory(categories[ui.comboBoxHashtagEditTopicsAdded.currentText()]):
            refreshComboBoxHashtagEditTopics()
            refreshHashtagEditSelectedTopicIntensity()
            refreshEditedCategory()

def deleteHashTag():
    if alert.Yes == alert.warning(ui.handleHashtags, 'Delete Hashtag', "Are you sure you want to delete the hashtag and lose it's data?", alert.Yes | alert.No | alert.Cancel, alert.Cancel):
        if ui.comboBoxHashtagEditHashTags.currentText() in hashTags.keys():
            hashTags.pop(ui.comboBoxHashtagEditHashTags.currentText())
            refreshEditedHashtag()
            refreshHashTagComboBoxes()

def saveCategories():
    global categories

    # if alert.question(ui.profiling, 'Saving File', "Do you really want to save?", alert.Yes | alert.No | alert.Cancel, alert.Cancel) == alert.Yes:
    if True:
        try:
        # if True:
            fileLocation = widgets.QFileDialog.getSaveFileName(gui, 'Save as...', str(os.path.dirname(os.path.abspath(__file__))),"HTML (*.html)")
            with open(fileLocation[0], "w", encoding="utf-8") as list:
                data = ('<!DOCTYPE HTML><meta charset="utf-8"/><html><head><title>Categories</title></head><body><ul>')
                for category in categories.keys():
                    if categories[category].getName() != '':
                        data +='<li>'
                        data += categories[category].getName()
                        data += '</li>'
                data += '</ul></body></html>'
                list.write(data)
            alert.information(ui.profiling, 'File Saved', "File has been saved", alert.Yes , alert.Yes)
        except:
            alert.warning(ui.profiling, 'Error While Saving', "There was an error while saving...", alert.Ok , alert.Ok)

def saveHashTags():
    global categories, hashTags, types

    if True:
        try:
        # if True:
            fileLocation = widgets.QFileDialog.getSaveFileName(gui, 'Save as...', str(os.path.dirname(os.path.abspath(__file__))),"HTML (*.html)")
            with open(fileLocation[0], "w", encoding="utf-8") as list:
                data = ('<!DOCTYPE HTML><meta charset="utf-8"/><html><head><title>Hashtags</title></head><body><ul>')
                for hashTag in hashTags.keys():
                    data +='<li id="'
                    data += hashTags[hashTag].getName()
                    data += '">'
                    for category in hashTags[hashTag].getCategories().keys():
                        data += '<category id="'
                        data += category
                        data += '" value="'
                        data += str(hashTags[hashTag].getCategoryIntensity(categories[category]))
                        data += '"/>'
                    for type in types.keys():
                        data += '<type id="'
                        data += type
                        data += '" value="'
                        data += str(hashTags[hashTag].getTypeIntensity(types[type]))
                        data += '"/>'
                    data += '</li>'
                data += '</ul></body></html>'
                list.write(data)
            alert.information(ui.profiling, 'File Saved', "Hashtags have been saved", alert.Yes , alert.Yes)
        except:
            alert.warning(ui.profiling, 'Error While Saving', "There was an error while saving...", alert.Ok , alert.Ok)


def loadHashTags(decoder):
    # print(filename[0])
    global categories, hashTags, gui, types
    resolve = dict()

    gui.setCursor(interface.QCursor(assets.Qt.WaitCursor))
    for tag in decoder.find_all('li'):
        resolve[tag['id']] = HashTag(tag['id'])
        # print(resolve[tag['id']].getName())
        for category in tag.find_all("category"):
            # print(category['id'])
            if category['id'] in categories.keys():
                resolve[tag['id']].addCategory(categories[category['id']],int(category['value']))
            for kind in tag.find_all("type"):
                    if kind["id"] in types.keys():
                        resolve[tag["id"]].setTypeIntensity(types[kind["id"]],int(kind["value"]))
    hashTags = resolve
    loadHashTagsComboBoxes(resolve)
    # for key in hashTags.keys():
    #     print(hashTags[key].getName()+":")
    #     for typeKey in hashTags[key].getTypes().keys():
    #         print(hashTags[key].getTypes()[typeKey]["object"].getName())
    gui.setCursor(interface.QCursor(assets.Qt.PointingHandCursor))   
    return resolve

def loadCategories(decoder, filename: tuple = (str(os.path.dirname(os.path.abspath(__file__))).replace("C:/",r'C:\\').replace("/",'\\')+r"\categories.html",r"HTML (*.html)")):
    global categories, gui
    response = dict()
    # print(filename[0])

    gui.setCursor(interface.QCursor(assets.Qt.WaitCursor))
    for tag in decoder.find_all('li'):
        response[tag.decode_contents()] = Category(tag.decode_contents())
        # print(resolve[tag['id']].getName())
    loadCategoriesComboBox(response)
    gui.setCursor(interface.QCursor(assets.Qt.PointingHandCursor))
    categories = response  
    return response

def loadCategoriesFromFile():
    global categories, gui, ui

    if(alert.question(ui.profiling, 'Reloading Categories', "Do you really want to reload all categories and lose changes?", alert.Yes | alert.No | alert.Cancel, alert.Cancel) == alert.Yes):
        gui.setCursor(interface.QCursor(assets.Qt.BusyCursor))
        categories = loadCategories(reader(widgets.QFileDialog.getOpenFileName(gui, 'Open file', str(os.path.dirname(os.path.abspath(__file__))),"HTML (*.html)")[0]))
        bindDisplay()
        alert.information(ui.profiling, 'Categories Reloaded', "All categories have been reloaded from file.", alert.Ok , alert.Ok)
        gui.setCursor(interface.QCursor(assets.Qt.PointingHandCursor))

def loadHashTagsFromFile():
    global hashTags, gui, ui

    if(alert.question(ui.profiling, 'Reloading Hashtags', "Do you really want to reload all hashtags and lose any current changes?", alert.Yes | alert.No | alert.Cancel, alert.Cancel) == alert.Yes):
        gui.setCursor(interface.QCursor(assets.Qt.BusyCursor))
        hashTags = loadHashTags(reader(widgets.QFileDialog.getOpenFileName(gui, 'Open file', str(os.path.dirname(os.path.abspath(__file__))),"HTML (*.html)")[0]))
        bindDisplay()
        alert.information(ui.profiling, 'Hashtags Reloaded', "All hashtags have been refreshed from selected file.", alert.Ok , alert.Ok)
        gui.setCursor(interface.QCursor(assets.Qt.PointingHandCursor))

def loadCategoriesComboBox(collection = None):
    global categories, requestedTopics, ui
    
    if collection == None:
        collection = categories
    gui.setCursor(interface.QCursor(assets.Qt.BusyCursor))
    ui.comboBoxTagGroupsExisting.clear()
    ui.comboBoxRequestSelectedTopics.clear()
    makeRequestedTopicsAndSelector()

    # print("Cleared category box...")
    for category in collection.keys():
        # print("For " + category)
        ui.comboBoxTagGroupsExisting.addItem(collection[category].getName())
        ui.comboBoxRequestSelectedTopics.addItem(collection[category].getName())
    gui.setCursor(interface.QCursor(assets.Qt.PointingHandCursor))

def loadHashTagsComboBoxes(collection = None):
    global hashTags, ui, gui

    if collection == None:
        collection = hashTags
    gui.setCursor(interface.QCursor(assets.Qt.BusyCursor))
    ui.comboBoxHashtagEditHashTags.clear()
    # print("Cleared hashtag box...")
    for tag in collection.keys():
        # print("For " + tag)
        ui.comboBoxHashtagEditHashTags.addItem(collection[tag].getName())
    gui.setCursor(interface.QCursor(assets.Qt.PointingHandCursor))

def refreshEditedCategory():
    global types, categories, ui

    if not ui.comboBoxTagGroupsExisting.currentText()=="":
        ui.lineEditTagGroupsNameEdited.setText(ui.comboBoxTagGroupsExisting.currentText())
        for type in types.keys():
            if ui.comboBoxTagGroupsExisting.currentText() in categories.keys():
                setGreenBarAndPercent(type,categories[ui.comboBoxTagGroupsExisting.currentText()].getTypeIntesity(types[type]))

def refreshHashTagComboBoxes():
    global hashTags

    loadHashTagsComboBoxes(hashTags)

def refreshEditedHashtag():
    refreshLineEditHashtagEditName()
    refreshComboBoxHashtagEditTopics()
    refreshSliderHashtagEditValues()
    refreshHashtagEditSelectedTopicIntensity()

def refreshLineEditHashtagEditName():
    global ui

    ui.lineEditHashtagEditName.setText(ui.comboBoxHashtagEditHashTags.currentText())

def refreshComboBoxHashtagEditTopics():
    global categories, hashTags, ui

    ui.comboBoxHashtagEditTopicsAdded.clear()
    ui.comboBoxHashtagEditTopicsUrelated.clear()
    # for key in hashTags.keys():
    #     print(key)
    for key in categories.keys():
        if ui.comboBoxHashtagEditHashTags.currentText() != "":
            if ui.comboBoxHashtagEditHashTags.currentText() in hashTags.keys():
                if categories[key].getName() in hashTags[str(ui.comboBoxHashtagEditHashTags.currentText())].getCategories().keys():
                    ui.comboBoxHashtagEditTopicsAdded.addItem(categories[key].getName())
                else:
                    ui.comboBoxHashtagEditTopicsUrelated.addItem(categories[key].getName())

def refreshHashtagEditSelectedTopicIntensity():
    global hashTags, ui

    if ui.comboBoxHashtagEditHashTags.currentText() != "" and ui.comboBoxHashtagEditTopicsAdded.currentText() != '':
        if ui.comboBoxHashtagEditHashTags.currentText() in hashTags.keys():
            # print("Current text is: '"+ui.comboBoxHashtagEditHashTags.currentText()+"'.")
            # integer = int(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getCategories()[ui.comboBoxHashtagEditTopicsAdded.currentText()]["intensity"])
            # print("Integer is: "+str(integer))
            ui.dialHashtagEditSelectedTopicIntensity.setValue(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getCategories()[ui.comboBoxHashtagEditTopicsAdded.currentText()]["intensity"])
            ui.labelHashtagEditSelectedTopicIntesityPercent.setText(str(ui.dialHashtagEditSelectedTopicIntensity.value())+"%")
            ui.labelHashtagEditIntensityForTagExplained.setText("(for "+ ui.comboBoxHashtagEditTopicsAdded.currentText() +' in ' + ui.comboBoxHashtagEditHashTags.currentText() + ")")

def refreshSliderHashtagEditValues():
    global hashTags, reloading, ui
    reloading = True
    # print(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["niche"]["intensity"])
    # print(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["emoji"]["intensity"])
    # print(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["place"]["intensity"])
    # print(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["event"]["intensity"])
    # print(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["phrase"]["intensity"])
    if ui.comboBoxHashtagEditHashTags.currentText() in hashTags.keys():
        ui.verticalSliderEmojiValue.setValue(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["emoji"]["intensity"])
        ui.verticalSliderHashtagEditNicheValue.setValue(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["niche"]["intensity"])
        ui.verticalSliderLocationValue.setValue(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["place"]["intensity"])
        ui.verticalSliderHashtagEditEventValue.setValue(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["event"]["intensity"])
        ui.verticalSliderPhraseValue.setValue(hashTags[ui.comboBoxHashtagEditHashTags.currentText()].getTypes()["phrase"]["intensity"])

    refreshSliderPercentages()
    reloading = False

def refreshSliderPercentages():
    global ui

    ui.label_27.setText(str(ui.verticalSliderHashtagEditNicheValue.value())+"%")
    ui.label_28.setText(str(ui.verticalSliderEmojiValue.value())+"%")
    ui.labelHashtagEditEventPercent.setText(str(ui.verticalSliderHashtagEditEventValue.value())+"%")
    ui.labelHashtagEditLocationPercent.setText(str(ui.verticalSliderLocationValue.value())+"%")
    ui.labelPhrasePercent.setText(str(ui.verticalSliderPhraseValue.value())+"%")

# =================================================
#                    START UP
# -------------------------------------------------

if __name__ == "__main__":

    reloading = True
    sys = widgets.QApplication(system.argv)
    gui = widgets.QMainWindow()
    location = str(os.path.dirname(os.path.abspath(__file__))).replace("C:/",r'C:\\').replace("/",'\\')
   
    ui = form.Ui_Dialog()    
    ui.setupUi(gui)

    gui.show()
    reloading = False

    makeTypes()
    attribute()

    categories = loadCategories(reader(location+r"\categories.html"))
    hashTags = loadHashTags(reader(location+r"\hashtags.html"))
    request = Request()

    bindEvents()
    bindDisplay()

    for key in hashTags.keys():
        # print(hashTags[key].getName())
        pass

    system.exit(sys.exec_())

# =================================================

    

    
    
    

