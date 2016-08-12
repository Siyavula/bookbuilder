'''Attempting to make an automatic numbering script
This script does the following:
1. Updates the anchor tags to have the correct figure or table reference. This is only needed for science at present.
2. Updates the figure and table caption tags to have a prefix of table x: or figure x:. Again only for science.
3. Updates chapter titles, section titles and subsection titles. Chapter titles need chapter x: as  a prefix, section titles need 'no. title shortcode' and subsection titles just need the shortcode at the end.
4. Numbers the worked examples.
5. Numbers the exercises
'''

# Import the necessary items
import os

from lxml import etree

# Make the figure reference dictionary (for grade 12 science at present)
fig_ref_dict = {"#fig:scienceskills:science":"1.1",}

# and the table ref dictionary
table_ref_dict = {"#table:momentumandimpulse:units":"2.1",}

chapterList =[[1, "Getalle en getal-berekeninge"],
[2, "Patrone, verhoudings en voorstellings"],
[3, "Omskakelings en tyd"],
[4, "Finansiele dokumente en tarief sisteme"],
[5, "Meting van lengte, massa, volume en temperatuur"],
[6, "Skaal, kaarte en planne"],
[7, "Waarskynlikheid"],
[8, "Persoonlike inkomste, uitgawes en begrotings"],
[9, "Meting van omtrek en oppervlak"],
[10, "Monterings diagramme, vloerplanne en verpakking"],
[11, "Bankwese, rente en belasting"],
[12, "Data hantering"]]

sectionList = {"scEMK2": 1.1,
"scEMK3": 1.2,
"scEMK9": 1.3,
"scEMKNM": 1.4,
"scEMKR": 1.5,
"scEMKT": 1.6,
"scEMKZ": 1.7,
"scEMK35": 2.1,
"scEMK36": 2.2,
"scEMK3C": 2.3,
"scEMK3G": 2.4,
"scEMK3J": 2.5,
"scEMK3N": 3.1,
"scEMK3P": 3.2,
"scEMK3T": 3.3,
"scEMK3W": 3.4,
"scEMK45": 4.1,
"scEMK46": 4.2,
"scEMK49": 4.3,
"scEMK4G": 5.1,
"scEMK4H": 5.2,
"scEMK4J": 5.3,
"scEMK4K": 5.4,
"scEMK4M": 5.5,
"scEMK4P": 6.1,
"scEMK4Q": 6.2,
"scEMK4W": 6.3,
"scEMK4Y": 7.1,
"scEMK52": 7.2,
"scEMK54": 7.3,
"scEMK55": 7.4,
"scEMK58": 7.5,
"scEMK5B": 8.1,
"scEMK5C": 8.2,
"scEMK5G": 8.3,
"scEMK5K": 8.4,
"scEMK5M": 8.5,
"scEMK5Q": 9.1,
"scEMK5R": 9.2,
"scEMK5V": 9.3,
"scEMK5Z": 10.1,
"scEMK62": 10.2,
"scEMK63": 10.3,
"scEMK67": 10.4,
"scEMK69": 11.1,
"scEMK6B": 11.2,
"scEMK6H": 11.3,
"scEMK6M": 11.4,
"scEMK6P": 12.1,
"scEMK6Q": 12.2,
"scEMK6S": 12.3,
"scEMK6V": 12.4,
"scEMK6Z": 12.5,
"scEMK74": 12.6,
"scEMK76": 12.7,
"scEMK7C": 12.8,}

sectionListKeys = sectionList.keys()

subsectionList = ["scEMK4",
"scEMK5",
"scEMK6",
"scEMK7",
"scEMK8",
"scEMKB",
"scEMKC",
"scEMKD",
"scEMKF",
"scEMKG",
"scEMKH",
"scEMKJ",
"scEMKK",
"scEMKPN",
"scEMKP",
"scEMKQ",
"scEMKS",
"scEMKV",
"scEMKW",
"scEMKX",
"scEMKY",
"scEMK32",
"scEMK33",
"scEMK37",
"scEMK38",
"scEMK39",
"scEMK3B",
"scEMK3D",
"scEMK3F",
"scEMK3H",
"scEMK3K",
"scEMK3Q",
"scEMK3R",
"scEMK3S",
"scEMK3V",
"scEMK3X",
"scEMK3Y",
"scEMK3Z",
"scEMK42",
"scEMK43",
"scEMK47",
"scEMK48",
"scEMK4B",
"scEMK4C",
"scEMK4D",
"scEMK4R",
"scEMK4S",
"scEMK4T",
"scEMK4V",
"scEMK4Z",
"scEMK53",
"scEMK56",
"scEMK57",
"scEMK5D",
"scEMK5F",
"scEMK5H",
"scEMK5J",
"scEMK5N",
"scEMK5S",
"scEMK5T",
"scEMK5W",
"scEMK5X",
"scEMK64",
"scEMK65",
"scEMK66",
"scEMK6C",
"scEMK6D",
"scEMK6F",
"scEMK6G",
"scEMK6J",
"scEMK6K",
"scEMK6R",
"scEMK6T",
"scEMK6W",
"scEMK6X",
"scEMK6Y",
"scEMK72",
"scEMK73",
"scEMK75",
"scEMK77",
"scEMK78",
"scEMK79",
"scEMK7B",]

wex_dictionary = {"Meting van 'n driehoek se omtrek": 2, 'Die volgorde van bewerkings': 5, 'Om die modus te vind': 6, 'Kontinue en diskrete grafieke': 3, 'Herlei gewone breuke na desimale breuke': 11, 'Klassifiseer persoonlike inkomste': 1, u'Rond af na die ho\xebr of laer getal': 12, "Hoe om 'n munisipale faktuur te verstaan": 1, "Hoe om 'n elektrisiteitsrekening te verstaan": 2, 'Skatting en meting van lengte': 1, "Teken 'n kaart volgens skaal": 6, "'n Grafiek van 'n omgekeerde eweredigheid": 7,
'hoe om met vloerplanne op skaal te werk': 6, "Die beraming van die oppervlakte van 'n reghoek deur van 'n rooster gebruik te maak": 6, "Die gebruik van 'n kalender": 13, "Gaan 'n betaalstrokie na": 7, 'Verstaan kasregisterstrokies': 5, 'Stip van punte': 6, "Interpreteer 'n grafiek wat aan die asse raak": 4, 'Omskakeling van eenhede vir kook': 7, 'Die teken van grafieke en histogramme': 8, "Hoe om 'n boomdiagram te gebruik vir gesamentlike uitkomste/resultate": 2, 'Tydomskakelings (meer ingewikkelde voorbeelde)': 11, "Die lees van 'n vloerplan": 4, 'Om verpakking te verstaan': 7, 'Besluit oor volume-eenhede': 3, "Die gebruik van 'n formule om omtrek te bereken": 5, 'Klassifiseer persoonlike uitgawes': 2, 'Meting van lengte en kosteberekeninge': 2, 'Besluit op die eenheidslengte': 1, 'Omskakeling van tydeenhede': 10, "Gebruik die numeriese skaal en rigtingnavigasie ten opsigte van die rangskikking van skoolbanke in 'n klaskamer": 7, 'Kies tydseenhede': 9, "Die gebruik van 'n rooster": 14, 'Werk met inverse verhoudings': 17, "Begrip van 'n staat": 1, 'Hoe winkelrekeninge werk': 6, "Die gebruik van 'n tweerigting-tabel vir gekombineerde uitkomste/resultate.": 3, "Interpreteer 'n grafiek wat die horisontale as raak": 5, 'Om die plasingswaarde te vind': 2, 'Afbreek en vermenigvuldiging': 6, 'Hoe om met die waarskynlikheidskaal te werk': 1, 'Vereenvoudiging van breuke': 9, "Beraam die oppervlak van 'n driehoek deur 'n rooster te gebruik": 7, 'Werk met vervoertariewe': 9, 'Skryf die verhoudings in eenheid vorm': 14,
'Herleiding van lengte-eenhede': 2, 'Die gebruik van groepering om berekenings makliker te maak': 7, "Voorselling van data in 'n lyngrafiek": 9,
'Vermenigvuldiging met ': 8, 'Om op die eenhede van massa te besluit': 5, 'Verstaan van rente': 5, "Vind ons pad in 'n winkelsentrum": 9, 'Die gebruik van formules om oppervlak te bereken': 10, "'n Grafiek van die maksimum temperatuur oor een week": 2, 'Werk met desimale breuke': 10, "Meting van 'n reghoek se omtrek": 1, 'Skryf van monteringsinstruksies': 3, 'Bereken die koste van massa': 6, "Bepaal die uitgelate waardes in 'n verhouding": 16, "Verstaan 'n fliek se sitplan": 8, "Bereken een getal as 'n persentasie van 'n ander getal": 19, 'Berekening van bankkoste': 3, "Kyk na 'n grafiek in 'n koerant": 1, 'Gebruik die numeriese skaal om afstand te skat': 2, 'Werk met gegroepeerde data': 2, 'Omskakel van eenhede van gewig': 6, "Die lees van 'n weerverslag": 10, 'Begrip van monteringsinstruksies': 2, 'Die gebruik van formules om omtrek te bereken': 4, 'Berekening van tydsverloop': 12, 'Meting van gewig': 3, 'Skryf verhoudings in die vereenvoudigde vorm': 13, 'Hoe om die grafiese en numeriese skale te gebruik': 1, 'Afmeet van volume': 7, 'Besluitneming oor wat die beste manier is om data te versamel': 1, 'Akuraatheid by vergroting/verkleining': 4, 'Die groepering van groot getalle en die oorskryf in woorde': 1, "Om die mediaan te kry wanneer daar 'n onewe aantal datawaardes is": 4, 'Bereken koerse': 15, "Begroting vir 'n partytjie": 3, 'Vind die gemiddeld': 3, 'Werk met tariewe': 7, "Die meting en raming van die oppervlak van 'n sirkel deur 'n rooster te gebruik": 8, 'Die skryf van syfers van klein na groot (stygende volgorde)': 3, 'Identifisering van patrone': 8, "Verstaan 'n selfoonrekening": 4, 'Die tekening van kaarte op skaal ': 5, 'Skakel om tussen 12-uur en 24-uur stelsels': 8, 'Persoonlike massa en gesondheid': 4, 'Om met telefoontariewe te werk': 8, 'Meet van temperatuur': 9, 'Berekening van persentasies van getalle': 18, 'Lees van monteringsinstruksies': 1,
'Die gebruik van die geheuesleutels op jou sakrekenaar': 4, 'Bereken die BTW op aankope': 6, "Verstaan 'n landlyn telefoon rekening": 3, "Om die mediaan te kry wanneer daar 'n ewe aantal datawaardes is": 5, 'Herleiding van volume-eenhede': 4, 'Berekening van kostes': 8, 'Die verstaan van vloerplan uitleg': 5, "Skatting van 'n sirkel se omtrek": 3, 'Die gebruik van die grafiese skaal om werklike lengte te skat': 3, 'Om die variasiewydte te vind': 7}



# number the figure and table references
def fig_ref_fix(xml):
    '''current code is <a href="blah" data-class="InternalLink">blah</a>. We want this to become <a href="blah" data-class="InternalLink">figure x</a> or table x if we are doing the tables'''
    for a in xml.findall('.//a'):
        aTag = etree.Element('a')
        href = a.get('href')  # the href of the tag
        if href in fig_ref_dict:  # we find the hRef in the figure keys
            aTag.clear()  # clear the contents of the tag
            a.text = 'Figure {}'.format(fig_ref_dict[href])  # replace the text of the tag with the value of the key in the fig ref dict and the word Figure
        elif href in table_ref_dict:  # we find the hRef in the table keys
            aTag.clear()  # clear the contents of the tag
            a.text = 'Table {}'.format(table_ref_dict[href])  # replace the text of the tag with the value of the key in the table ref dict and the word Table
    return xml  # returns what we need


# the other piece is to fix the captions
def fig_caption(xml):
    '''current code is <div id="fig-atom-plumpudding" class="figure"><img src="pspicture/90cffe92260bc3815a6825cbb0d87b39.png" alt="90cffe92260bc3815a6825cbb0d87b39.png"/><div class="figcaption"><p>The atom according to the Plum Pudding model.</p></div></div>. We need to identify the figure from the overarching href and then modify the caption div to state: Figure x: blah
    To repeat for tables we need to take the current code: <div id="blah" data-class="FigureTable"><table>code</table><div class="caption"><p>caption</p></div></div>, identify the table and modify the caption to state Table y: blah
    '''
    for div in xml.findall('.//div[@class]'):  # find all divs with attribute class
        if div.attrib['class'] == 'figure':  # only work on the divs we actually want, this may change to be the same as the tables
            caption = div.find('.//div')
            if caption is not None:
                caption = div.find('.//div').find('.//p')  # extract just the caption bit
                try:
                    figId = '#' + div.attrib['id'].replace('-', ':')  # temporary hack to get the id's correct, the # will always be needed but the replace can be removed when the validator updates are completed
                    #div.set('id', figId)  # attempting to put in a hack to fix the id problem
                    if figId in fig_ref_dict:
                        # caption.text = 'Figure ' + fig_ref_dict[figId] + ': ' + caption.text
                        caption.text = 'Figure {}: {}'.format(fig_ref_dict[figId], caption.text)
                except:
                    pass
    for div in xml.findall('.//div[@data-class]'):  # find all the divs with data-class
        if div.attrib['data-class'] == 'FigureTable':  # check that data-class does equal to FigureTable
            caption = div.find('.//div')
            if caption is not None:
                caption = div.find('.//div').find('.//p')  # extract just the caption bit
                try:
                    tableId = '#' + div.attrib['id'].replace('-', ':')  # temporary hack to get the id's correct, the # will always be needed but the replace can be removed when the validator updates are completed
                    div.set('id', tableId)  # attempting to put in a hack to fix the id problem
                    if tableId in table_ref_dict:
                        # caption.text = 'Table ' + table_ref_dict[tableId] + ': ' + caption.text
                        caption.text = 'Table {}: {}'.format(table_ref_dict[tableId], caption.text)
                except:
                    pass
    return xml


# now trying the chapter and section number function
def chapter_section_number(xml):
    '''This updates the appropriate h1 and h2 tags with a number. The number is determined from an appropriate dictionary. This uses the shortcodes to match the section and subsection headers but uses the chapter name to match the chapter numbers. The chapters might need some manual fixing while the sections and subsections should not.'''
    for h1 in xml.findall('.//h1'):  # loop over the h1's
        for i in range(len(chapterList)):  # loop over the chapter list
            if h1.text == chapterList[i][1]:  # check if h1 matches a chapter title.
                newText = 'Hoofstuk {}: {}'.format(str(chapterList[i][0]), h1.text) # If T then add number, else ignore
                h1.text = newText
    # use the shortcode to tag the h2's with a number and the shortcode, repeat for h3's but only add the shortcode
    for div in xml.findall('.//div[@id]'):
        if div.attrib['id'] in sectionListKeys:
            for k in range(len(sectionListKeys)):
                if div.attrib['id'] == sectionListKeys[k]:
                    shortcode = etree.Element('span')
                    shortcode.text = '({})'.format(sectionListKeys[k][2:])
                    shortcode.set('class', 'shortcode')
                    h2 = div.find('h2')
                    try:
                        if h2 is not None:
                            h2.text = '{} {} '.format(str(sectionList[sectionListKeys[k]]), div.find('h2').text)
                            h2.append(shortcode)
                    except UnicodeEncodeError:
                        continue
        # use the shortcode to tag the h3's with the shortcode only
        if div.attrib['id'] in subsectionList:  # iterate through the subsectionList
            for j in range(len(subsectionList)):
                if div.attrib['id'] == subsectionList[j]:
                    shortcode = etree.Element('span')
                    shortcode.text = '({})'.format(subsectionList[j][2:])
                    shortcode.set('class', 'shortcode')
                    h3 = div.find('h3')
                    try:  # for some reason using if h3 is not None fails to stop some errors so reverted to try block
                        h3.text = '{} '.format(div.find('h3').text)  # If the text matches the dictionary then add the number. Else ignore.
                        h3.append(shortcode)
                    except:
                        pass
    return xml  # Return the updated xml


# next up: number the worked examples
def wex_number(xml):
    '''
    Number the worked examples using the wex dictionary. This will be fuzzy matching since it uses the titles and the titles sometimes contain strange characters or maths that cannot be matched.
    Wexes are defined as <div class="worked_example"><h1 class="title">Standard notation</h1>
    This modifies the wex code to be <div class="worked_example"><h1 class="title">Worked example 5: Standard notation</h1>
    '''
    #find the worked examples
    for div in xml.findall('.//div[@class]'):  # find all divs with attribute class
        if div.attrib['class'] == 'worked_example':  # only work on the divs we actually want
            title = div.find('.//h1')
            if title is not None:
                try:
                    if title.text in wex_dictionary:
                        title.text = 'Worked example {}: {}'.format(wex_dictionary[title.text], title.text)  # add the number using the dictionary
                except:
                    pass
    return xml  # return the updated xml


# number the exerices
def exercise_number(xml):
    '''
    Number the exercises using ??.
    Still deciding where to put the number.
    Exercises currently are <div class="section"><h2 class="title" id="toc-id-11">Exercises</h2>
    This part of the script gets complicated and I am not 100% sure why each bit works
    '''
    global exercise_counter  # danger!
    for div in xml.findall('.//div[@class]'):  # find all divs with classes
        title = div.find('.//h2')  # find the title
        ps = div.find('.//div[@class]')  # find the problemset
        if ps != None and ps.attrib['class'] == 'problemset':  # verify that we do have a problemset
            if title != None and title.text == 'Exercises':  # now find just the exercises
                span_code = etree.Element('span')  # make a span
                span_code.set('class', 'exerciseTitle')  # set the class of the span
                span_code.text = 'Oefening {}.{}'.format(file_number, exercise_counter)  # add the counter as text along with the file number
                ps.insert(0, span_code)  # append the exercise counter after the initial problemset
                # to change where span is inserted find the index, see here: http://stackoverflow.com/questions/7474972/python-lxml-append-element-after-another-element
                exercise_counter += 1  # if I have this correctly this only affects the local instance of the counter
                span_end = etree.Element('span')  # trying to add the bit about practice
                span_end.set('class', 'practiceInfo')  # set the class of the span
                bottom_practice_link = etree.SubElement(span_end, 'a')  # make a link
                span_end.text = 'For more exercises, visit '  # change to science for the science one
                bottom_practice_link.set('href', 'http://www.everythingmaths.co.za')  # set the class of the link
                bottom_practice_link.text = 'www.everythingmaths.co.za'  # set the text of the link
                bottom_practice_link.tail = ' and click on "Practice Maths"'  # add a tail to the link
                ps.append(span_end)  # add it to the end of the problemset
                span_top = etree.Element('span')  # trying to add the bit about practice
                span_top.set('class', 'practiceInfo')  # set the class of the span
                top_practice_link = etree.SubElement(span_top, 'a')  # make a link
                span_top.text = 'Practice online to master this topic, visit '  # change to science for the science one
                top_practice_link.set('href', 'http://www.everythingmaths.co.za')  # set the class of the link
                top_practice_link.text = 'www.everythingmaths.co.za'  # set the text of the link
                top_practice_link.tail = ' and click on "Practice Maths"'  # add a tail to the link
                ps.insert(1, span_top)  # add it to the end of the problemset
    return xml

# Put it all together
#path = '/home/heather/Desktop/books/physical-sciences-12/afrikaans/build/epubs/science12/OPS/xhtml/science12'
#path = '/home/heather/Desktop/books/mathematics-10/afrikaans/build/epubs/maths10/OPS/xhtml/maths10'
#path = '/home/heather/Desktop/books/scripts/test-files/new_test'
path = '/home/heather/Desktop/books/grade-10-mathslit-latex/afrikaans/build/epubs/maths-lit10v2/OPS/xhtml/maths-lit10v2'

fileList = os.listdir(path)
fileList.sort()

file_counter = 1  # set a file counter
exercise_counter = 1  # set an exercise counter

for file_name in fileList:
    full_file_name = '{}/{}'.format(path, file_name)

    # Skip directories
    if os.path.isdir(full_file_name):
        continue

    if file_name[0] not in ['0', '1', '2']:  # we need to ignore anything that does not start with a number
        continue

    xml = etree.parse(full_file_name, etree.HTMLParser())

    title_exercise = xml.findall('.//h2')  # trying to find h2's in the file

    file_number = int(file_name[:2])  # set a file number

    random_number = 0  # only way I could think of to do this
    for i in title_exercise:  # find out if there is Exercises in the file
        if i.text == 'Exercises':
            random_number += 1
    if random_number != 0:  # we did find Exercises so now we can play with the counters
        if file_counter != file_number:  # if not then we must increment the file counter and reset the exercise counter
            file_counter += 1
            exercise_counter = 1
    
    fileText = None

    #xml = fig_ref_fix(xml)
    #xml = fig_caption(xml)
    xml = chapter_section_number(xml)
    xml = wex_number(xml)
    xml = exercise_number(xml)
    
    fileText = etree.tostring(xml, pretty_print=True)

    # target_filename = '{}/heather.txt'.format(path)

    if fileText:
        with open(full_file_name, 'w') as file:
            file.write(fileText)
