from os import name, replace, umask
import requests
from bs4 import BeautifulSoup
import time
import shutil
from pathlib import Path
import os

                                #####################################
                                ############### GLOBAL ##############
                                #####################################
                                

URL='http://books.toscrape.com/index.html'
books = []
csvs = []

                                #####################################
                                ##### DECLARATION DES FONCTIONS #####
                                #####################################



####
# Étape 1) je Récupére l'url de toutes les caégories 
####

def searchLink():
    links =[]
    url ='http://books.toscrape.com/index.html'
    response = requests.get(url)
    search = BeautifulSoup(response.text, 'html.parser')
    if response.ok: 
        find_ul = search.find('ul', class_='nav nav-list').find_next('li')
        findLinks = find_ul.find_next('ul').find_all('li')
        for li in findLinks: 
            link = li.a.get('href')
            links.append('http://books.toscrape.com/' + link)
            print('Récupération des Url des catégories !')
            #if len(links) <= 10:
            #   break
    else: 
        print('Une erreur est survenue lors de la récupération des url catégories')
    return links

####
# Étape 2) je fait une pagination sur les categories 
####

def searchPage():
    urlSupInPage = []
    for url in searchLink():
        response = requests.get(url)
        search_allUrl = BeautifulSoup(response.text, 'html.parser')
        urlSupInPage.append(url)
        if response.ok :
            print('récupération pages dans la catégorie : ok ')
            condition = search_allUrl.find_all('ul', class_='pager')
            if len(condition) == 1:
                for i in range(2,9):
                    urlSupInPage.append(url.replace('index.html', 'page-' + str(i) + '.html'))
        else:
            print('Erreur lors de la recupération des pages dans les catégories ..')
    return urlSupInPage

####
# Étape 3) je récupére tout les Urls des livres 
####

def searchElementsInCatLinks():
    books_link =[]
    for item in searchPage():
        response = requests.get(item)
        search_book = BeautifulSoup(response.text, 'html.parser')
        if response.ok : 
            get_wayLink = search_book.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
            for a in get_wayLink:
                fullLink = a.find_all('a')
                for ref in fullLink:
                    link = ref.get('href')
                    books_link.append('http://books.toscrape.com/catalogue' + link.replace('../../..', ''))
                    books_link = list(dict.fromkeys(books_link))
                    print(' recuperation OK : ' + str(len(books_link)))
    return books_link

####
# Étape 4) Je cherche tout les éléments demander et les met dans un dico  
####

def findElements(books):
    for element in searchElementsInCatLinks():
        response = requests.get(element)
        finder = BeautifulSoup(response.text, 'html.parser')
        if response.ok:
            recup_tableInfo = finder.find_all('td')
            url = element
            title = finder.find('h1').text.replace(':', ' ' ).replace(',', ' ')
            uProductC = recup_tableInfo[0].text
            Available = recup_tableInfo[5].text
            priceWithTax = recup_tableInfo[3].text
            priceWithoutTax = recup_tableInfo[2].text
            find_category = finder.find_all('a', string="Books")
            for name_cat in find_category:
                category = name_cat.find_next('a').text    
            get_description = finder.find_all('div', id="product_description")
            for infos in get_description:
                Description = infos.find_next('p').text.replace(';' , ',')
            get_Rating = finder.find('p' , class_='star-rating')['class']
            Rating = ' = '.join(get_Rating)
            get_img = finder.find_all('div', class_='item active')
            for image_src in get_img:
                img = image_src.find('img')['src'].replace('../..', 'http://books.toscrape.com')
            print(Rating)
            book = {
                "product_page": url,
                "uProductC": uProductC,
                "Title": title,
                "price_with_tax": priceWithTax,
                "price_without_tax": priceWithoutTax,
                "available": Available,
                "description":  Description,
                "category": category,
                "Rating": Rating,
                "Img_url": img
            }
            books.append(book)
            #time.sleep(0.5)
            print('élements de livre : ok ' + str(len(book)))
            print(str(book["category"]))
        else :
            print('une erreur est survenue lors de la récupération des éléments ')
    print('voici les éléments demandé :  #######  ' + str(len(books)))
    return book

####
# Étape 5) je crée tout les csv 
####

def create_csvs(csvs):
    REPONSE = requests.get(URL)
    SOUP = BeautifulSoup(REPONSE.text , 'html.parser')
    if REPONSE.ok: 
        Search_cat_ul = SOUP.find('ul', class_='nav nav-list').find_next('li')
        Search_cat_li = Search_cat_ul.find_next('ul').find_all('li')
        for name_cat in Search_cat_li:
            find_name_link = name_cat.find('a').text.strip()
            csvs.append(find_name_link)
            with open(str(find_name_link) + '.csv', 'w', encoding="utf-8" ) as infile:
                infile.write('Product_page_url ; Universal_product_code ; Title ;'
                             'Product_incluing_taxe ; Product_exluding_tax ; Number_available ;'
                             'Product_description ; Category ; Review_rating ; Image_url\n'
                             )
        print('fichiers CSV créer !')
    else:
        print("Une erreur c'est produit lors de la création des CSV")
    return infile
    
####
# Étape 6) je rentre les bonnes infos dans les CSV en les ouvrant par rapport a leurs nom 
####

def insert_books_in_csvs(books):
    for book in books: 
        with open(book["category"] + '.csv', 'a', encoding="utf-8") as infile:
            infile.write(str(book['product_page']) + ' ; ' + str(book['uProductC']) + ' ; ' + str(book['Title']) + ' ; ' +
                str(book['price_with_tax']) + ' ; ' + str(book['price_without_tax']) + ' ; ' +
                str(book['available']) + ' ; ' + str(book['description']) + ' ; ' + str(book['category']) + ' ; ' +
                str(book['Rating']) + ';' + str(book['Img_url']) + '\n'
                )
        print('copie succesful')
                
####
# Étape 7) Je télécharge Toutes les images et les met dans un dossier 
####        
          
def Img_download(books):
    directory = Path.cwd()
    directory = directory / "image"
    directory.mkdir(exist_ok= True)
    os.chdir(directory)  
    for image in books:
        response = requests.get(image['Img_url'], stream=True)  
        print(response)
        if response.status_code == 200:
            with open(str(image['Title'].replace('/','_')) + '.jpg', 'wb' ) as images:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, images)
                print('image téléchargé ####')
        else:
            print("erreur lors du telechargement de l'image")
# join the title with . or _ otherwise it won't work. don't use / otherwise it won't work again ... simply use replace() 

                                #####################################
                                #####    APPEL DES FONCTIONS    #####
                                #####################################

findElements(books)

create_csvs(csvs)

insert_books_in_csvs(books)

Img_download(books)

                                #####################################
                                ##########   COMMENTAIRES  ##########
                                #####################################


####
# Étape 1) je Récupére l'url de toutes les caégories 
####

####
# Étape 2) je fait une pagination sur les categories 
####

####
# Étape 3) je récupére tout les Urls des livres 
####

####
# Étape 4) Je cherche tout les éléments demander et les met dans un dico  
####

####
# Étape 5) je crée tout les csv 
####

####
# Étape 6) je rentre les bonnes infos dans les CSV en les ouvrant par rapport a leurs nom 
####

####
# Étape 7) Je télécharge Toutes les images et les met dans un dossier 
####

