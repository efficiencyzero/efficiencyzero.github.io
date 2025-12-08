"""
A LEVEL COMPUTER SCIENCE NEA
 -- WIKIPEDIA VISUALISER --
"""

##### LIBRARIES AND MODULES #####
import re
import time

# Web scraping modules
import requests
'''
requests is used to make a GET request to a specified URL.
requests documentation: https://requests.readthedocs.io/en/latest/
'''
import webbrowser
'''
The webbrowser module is used to automatically display url using the default browser.
webbroser documentation: https://docs.python.org/3/library/webbrowser.html
'''
from bs4 import BeautifulSoup, NavigableString
'''
BeautifulSoup is a library that is used for web scraping.
It converts an HTML document into a tree of python objects that represents HTML elements on the web page.
bs4 documentation: https://beautiful-soup-4.readthedocs.io/en/latest/#
'''

# Graphing module
'''
pyvis generates a network graph in python, with a wrapper around a javascript library, visJS.
It allows me to modify the graphing code in python without changing its source code.

pyvis documentation: https://pyvis.readthedocs.io/en/latest/index.html
source code: https://visjs.github.io/vis-network/standalone/umd/vis-network.min.js
html reference: view-source:https://visjs.github.io/vis-network/examples/network/basicUsage.html
'''

# Web server modules
import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
'''
The http.server module is a subclass of socketserver.TCPServer.
It creates and listens at the HTTP socket, dispatching the requests to a handler.
http.server documentation: https://docs.python.org/3/library/http.server.html
'''
import socketserver
'''
The socketserver module simplifies the task of writing network servers.
socketserver documentation: https://docs.python.org/3/library/socketserver.html
'''





class WebScraper:
  '''
  The WebScraper class extracts the content of a web page based on the URL passed into the class
  Reference: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#making-the-soup
  '''
  
  def __init__(self, url):
    self.__url = url
    self.__soup = ""
    self.__body = ""
    self.__hyperlinks = ""
    # an array of filtered hyperlinks (in HTML format)
    self._filteredLinks = []    
    self.__badTitle = ""
    self.__noArticle = ""

    # HTML tags that should be filtered out and deleted are stored in an array as a tuple (tag, class)
    self._tagsToBeDeleted = [("div","mw-heading"),("ol","references"),("sup","reference"),
                            ("sup","noprint Inline-Template Template-Fact"),("table","infobox"),
                            ("div","mbox-text-span"),("div","side-box-flex"),("th","navbox-title"),
                            ("a","external text"),("div","boilerplate metadata plainlinks"),
                            ("div","vector-menu-content"),("div","hatnote navigation-not-searchable"),
                            ("td","mbox-text"),("span","unicode haudio"),("div","legend")]

    self.__file = ""
    self.__localSoup = ""
    self.__script = ""
   

  def _soup(self):
    '''
    This method gets and parses the contents of a web page, 
    by using the requests module to make a GET request to the specified URL.
    The content is returned and stored into a temporary variable (reponse), 
    then it is passed into the BeautifulSoup constructor to parse the HTML. 
    The constructor returns a tree of python objects that represents HTML elements on the web page, 
    stored into the self.__soup attribute.
    '''
    # send GET request to url
    response = requests.get(self.__url)
    # parse the whole html
    self.__soup = BeautifulSoup(response.text, "html.parser")  
    return self.__soup

  def _localSoup(self, url):
    '''
    This method opens and parses a local html file with the BeautifulSoup constructor
    It returns a tree of python objects that represents HTML elements in the file
    '''
    # open local html file, where url = file name
    self.__file = open(url)
    # parse local html file with BeautifulSoup
    self.__localSoup = BeautifulSoup(self.__file, "html.parser")
    return self.__localSoup 

  def _findHeading(self):
    '''
    This method finds the 'h1' tag (heading) and returns the result as a string
    '''
    # find heading with 'h1' tag and id='firstHeading' in parsed html (bs4)
    self.__heading = self._soup().find("h1", id = "firstHeading")
    # gets the text within the tag
    self.__heading = self.__heading.text  
    return self.__heading 

  def _findBody(self):
    '''
    This method finds the body of the HTML and returns the result as a Tag object
    '''
    # find body with 'div' tag and class='mw-body-content' in parsed html (bs4)
    self.__body = self.__soup.find("div", class_ = "mw-body-content") 
    return self.__body  
    
  def _findScript(self):
    '''
    This method finds the 'script' tag in the local HTML file and returns the result as a Tag object
    '''
    # find script with 'h1' tag and id='firstHeading' within local html file (bs4)
    self.__script = self.__localSoup.find("script", id = "network")
    return self.__script
  

  def _decomposeSoup(self):
    '''
    This method iterates through the self._tagsToBeDeleted list and finds all elements with the specified tag and class,
    then completely removes the tag and its contents from the parsed tree (soup)
    '''
    for tag, tagClass in self._tagsToBeDeleted:
      ##print("decomposing:", tag, tagClass)
      
      # finds all elements with the specified tag and class
      element = self.__body.find_all(tag, class_ = tagClass)
      for content in element:
        # decompose() is a function in BeautifulSoup that deletes a tag and its contents from the parsed tree
        content.decompose()


  def _validArticle(self):
    '''
    This method checks whether a Simple Wikipedia article exists 
    by finding key elements in the parsed tree (bs4) that shows when an article does not exist
    It returns True if the article exists and False if the article does not exist
    '''
    # find heading with 'h1' tag, if the heading is 'Bad title', the article is not valid
    self.__badTitle = self.__soup.find("h1")
    if self.__badTitle.string == "Bad title":
      print("bad title")

    # find division with 'div' tag and class='noarticletext mw-content-ltr' 
    # if this division is found, the article is not valid
    self.__noArticle = self.__soup.find("div", class_ = "noarticletext mw-content-ltr")
    if self.__noArticle != None:
      print("no article")

    # the article is valid if the 'noarticletext' division does not exist AND the heading does not say 'Bad title'
    if self.__noArticle == None and self.__badTitle.string != "Bad title":
      return True
    else:
      return False


  def _findHyperlinks(self):
    '''
    This method finds all the 'a' tag (hyperlinks) in the parsed HTML tree, 
    then iterate through the results to filter out invalid hyperlinks
    Valid hyperlinks are stored and returned as an array (self._filteredLinks)
    '''
    # find hyperlinks with the tag <a> and a limit of 5
    self.__hyperlinks = self.__body.find_all("a", limit=5) 

    # iterate through the hyperlinks and add/filter them into a list if the hyperlink is not none, valid and not an url
    for link in self.__hyperlinks:  
      if link.string != None and self._validArticle() and (re.search("https://", link.string)) == None:  
        self._filteredLinks.append(link)

    return self._filteredLinks


  def scrape(self):
    '''
    This method is the main public method of the WebScraper class
    It calls the functions needed to scrape a web page and returns a list of filtered hyperlinks in html format
    '''
    # create soup (a tree of python objects that represents HTML elements on the web page)
    self._soup()

    if self._validArticle():
      self._findBody()
      self._decomposeSoup()
      self._findHyperlinks()
    
    return self._filteredLinks 

    


class IDGenerator:
  '''
  IDGenerator stores a counter for the current ID and generates an unique ID in self._nextID()
  '''
  def __init__(self):
    self._count = 0

  def _nextID(self):
    '''
    This method gets the next available ID to prevent ID duplicates, which could lead to data collision
    '''
    self._count = self._count + 1
    ##print("current ID:", self._count)
    return self._count
    




class Node:
  '''
  Nodes are objects that contains an unique ID, a title, an URL, 
  as well as an array of its child nodes as its main attributes
  '''
  def __init__(self, ID, title, wikiPath):
    self.__id = ID
    self.__title = title
    self.__baseurl = "https://simple.wikipedia.org/"
    self.__wikiPath = wikiPath
    self.__ownPath = "wiki/" + self.__title.replace(" ","_")
    self.__url = ""
    self._childNodes = set()
    '''
    A set is a collection of unique and unordered values.
    It is used as a data structure for self._childNodes 
    because it ensures that there will be no duplicates of child nodes.
    The order of child nodes does not matter in this case.
    '''


  def getID(self):
    '''
    This is a public method to get node ID.
    '''
    return self.__id

  def getURL(self): 
    '''
    This is a public method to set/get node URL.
    It concatenates the protocol, domain name and its directory path, 
    where wikiPath (if found from WebScraper) is preferred over ownPath as it is more accurate.
    '''
    if self.__wikiPath == None:
      self.__url = self.__baseurl + self.__ownPath
    else:
      self.__url = self.__baseurl + self.__wikiPath
    return self.__url

  def getTitle(self):
    '''
    This public method to get node title, replacing an underscore with a space for better readability
    '''
    self.__title = self.__title.replace("_"," ")
    return self.__title
  
  def getWikiTitle(self):
    '''
    This is a public method to set/get node title from the heading of a Simple Wikipedia article by scraping the url in Node object
    '''
    w = WebScraper(self.getURL())
    self.__title = w._findHeading()
    return self.__title

  def isValidNode(self):
    '''
    This method checks if a node is valid (by redirecting to WebScraper._validArticle method)
    returns True if valid and false if article is invalid
    '''
    if self.__title != "":
      w = WebScraper(self.getURL())
      w._soup()
      if w._validArticle():
        return True
      else:
        return False
    else:
      print("isValidNode(): no title")

  
  def expandNode(self, depth):
    '''
    This method finds its child nodes recursively by web scraping the node 
    and traversing through its parsed tree using depth-first search
    This is a RECURSIVE DEPTH-FIRST SEARCH ALGORITHM
    '''
    print("expanding", self.getID(), self.getTitle(), "with depth", depth)
    w = WebScraper(self.getURL())

    for hyperlink in w.scrape():
      title = hyperlink.text
      wikiPath = hyperlink.attrs.get("href")
      ##print("expandNode():", title, wikiPath)

      # check if the hyperlink already exists in the dictionary (nodeObjByTitle)
      node = GraphNodes.findByTitle(title)
      if node == None and title != "":
        # create a new child node if it does not exist in the dictionary
        node = Node(gen._nextID(), title, wikiPath)
        
      # add new child node to the array of child nodes
      self._childNodes.add(node)
      # add new child node ID/title (key) and the node (value) to the dictionaries
      GraphNodes.addToDict(node)
      
    if depth <= 1:   # base case
      return None   
    
    else:           
      # expand for each node object
      for childNode in self._childNodes:
        childNode.expandNode(depth-1)    # calls itself and moves towards the base case





class GraphNodes:
  '''
  GraphNodes is a container class that stores the existing nodes of the current graph in dictionaries
  '''
  def __init__(self):
    self._nodeObjByID = {}      # key: ID, value: node object 
    self._nodeObjByTitle = {}   # key: title, value: node object


  def addToDict(self, node):
    self._nodeObjByID[node.getID()] = node
    self._nodeObjByTitle[node.getTitle()] = node

  def findByID(self, ID):
    return self._nodeObjByID.get(ID)

  def findByTitle(self, title):
    return self._nodeObjByTitle.get(title)

  def clearDict(self):
    self._nodeObjByID.clear() 
    self._nodeObjByTitle.clear()
    ##print("dictionaries cleared:", self._nodeObjByID, self._nodeObjByTitle)





class Graph:
  '''
  Graph is a class that generates a network graph and writes to a html file
  '''
  def __init__(self, root):
    self.__root = root  # Node object

    # use WebScraper to parse html file and find script section
    w = WebScraper("network-graph.html")
    self._htmlFile = w._localSoup("network-graph.html") # given that the html file is stored in the same place as this python file
    self.__script = w._findScript()


  def _addNode(self):
    '''
    This method converts nodes to JSON format and add to html file
    '''
    for node in GraphNodes._nodeObjByID.values():
      # format node ID and title into JSON
      nodeString = NavigableString(f"{{ id: {node.getID()}, label: \"{node.getTitle()}\" }},")
      # NavigableString is a BeautifulSoup class used to contain text within HTML tags
      # append() is a BeautifulSoup method that adds to a specific tag of the html without rewriting the whole html
      self.__script.append(nodeString)

  
  def _addEdge(self):
    '''
    This method converts edges into JSON format using a nested for loop and add to html file
    '''
    # a temporary set is used to track the edges and avoid duplicates
    edges = set()
    for node in GraphNodes._nodeObjByID.values():
      for child in node._childNodes:
        # format parent node ID and child node ID into JSON 
        edges.add(NavigableString(f"{{ from: {node.getID()}, to: {child.getID()} }},"))

    # add edgeString to the script section of the html
    for edgeString in edges:
      self.__script.append(edgeString)
        

  def _writeFile(self):
    '''
    This method writes and saves to a html file
    '''
    # write to html file
    with open("network-graph.html", "wb") as file:
       file.write(self._htmlFile.prettify("utf-8"))

    # close file to save it
    file.close()



  def generateGraph(self, error): 
    '''
    This public method creates a network graph and writes it into a html file
    ''' 
    # clear script section in HTML file so that it generates a new graph each time
    self.__script.clear()
    
    # add nodes (in JSON) to a list (in javascript) and create a new dataset through vis.js library
    self.__script.append(NavigableString("var nodes = new vis.DataSet(["))
    self._addNode()
    self.__script.append(NavigableString("]);"))
    
    # add edges (in JSON) to a list (in javascript) and create a new dataset through vis.js library
    self.__script.append("var edges = new vis.DataSet([")
    self._addEdge()
    self.__script.append(NavigableString("]);"))

    # create a network graph through vis.js library
    self.__script.append(NavigableString("var container = document.getElementById(\"mynetwork\");"))
    self.__script.append(NavigableString("var data = {nodes: nodes, edges: edges,};"))
    self.__script.append(NavigableString("var options = {};"))
    self.__script.append(NavigableString("var network = new vis.Network(container, data, options);"))

    '''
    The source code to handle all vis.js methods are stored in a javascript file and accessed through the html file.
    Both files should be in the same place as this python file.
    vis.js source code: https://visjs.github.io/vis-network/standalone/umd/vis-network.min.js 
    '''

    # pop up window alert if unable to connect to the internet
    if error != None and (type(error) == requests.exceptions.ConnectionError): 
      print("Connection error")
      self.__script.append(NavigableString("window.alert('Connection error. Check your internet connection.');"))
    
    # pop up window alert if search is invalid
    elif self.__root == None:
      print("Invalid search")
      self.__script.append(NavigableString("window.alert('Unable to generate graph. Please try another word.');"))

    # pop up window alert for any other unexpected errors
    elif error != None:
      print("An unexpected error occurred: ", error)
      self.__script.append(NavigableString("window.alert('An unexpected error occurred. Please try again.');")) 
      

    # write and save to html file
    self._writeFile()






class UserInterface:
  '''
  UserInterface is a class that interacts with the user
  '''
  
  def __init__(self):
    self.__root = None
    self.__parentNode = None
    self.__depth = 1    # depth is set to 1 to speed up processing time


  def start(self, query, ID, error):
    '''
    This public method receives input from the user and calls the generateGraph() method
    '''
    try:  # try and except block to handle any errors 
      
      if query == None:
        # This should happen at the start, before any search is inputted
        print("no query")
        self.__root = Node(0, "", None)

      elif ID == '':
        # This should happen to every new search, where no ID is assigned yet
        print("no ID")
        # clear root
        self.__root = None 
        query = query.replace("+","_")

        # create a temporary node and check if new node is valid to avoid creating and adding an invalid node to the graph
        newNode = Node(0, query, None)
        ##print(query, newNode.isValidNode())
        
        if newNode.isValidNode():
          # if new node is valid, create an actual node as the root node and expand
          self.__root = Node(0, newNode.getWikiTitle(), None)
          GraphNodes.addToDict(self.__root)
          self.__root.expandNode(self.__depth)
           
      else:
        # This should happen every time a node is double clicked, as the ID and query are already known
        query = query.replace("+","_")
        #########self.__parentNode = GraphNodes.nodeObjByID.get(int(ID))
        self.__parentNode = GraphNodes.findByID(int(ID))
        self.__parentNode.expandNode(self.__depth)

    except Exception as e:
      print("Errors in ui.start():", e)
      error = e

    # generate a network graph
    graph = Graph(self.__root)
    graph.generateGraph(error)






class Handler(http.server.SimpleHTTPRequestHandler):
  '''
  Handler is a custom class that extends SimpleHTTPRequestHandler from the http.server module  
  It handles customised requests with the do_GET() function
  '''
  
  def do_GET(self):
    start = time.time()
    '''
    This is a method from SimpleHTTPRequestHandler class that processes the GET requests from REST API and retrieves data from the user.
    REST API is a application programming interface (API) that follows the design principles 
    of the representational state transfer (REST) architectural style.
    '''
    # check if path contains '/WikipediaVisualiser' using regular expression
    isWikiVisualiser = (re.search("(/WikipediaVisualiser).*", self.path) != None)
    
    if isWikiVisualiser:
      # if it is the correct path, run the rest of the code
      self.send_response(200) # OK
      self.send_header("Content-type", "text/html") # ensure content is sent in html format
      self.end_headers()

      try:  # extract request parameter
        info = self.path.split("?")[1]
        query = info.split("&")[0].split("=")[1]
        ID = info.split("&")[1].split("=")[1]
        isExpand = info.split("&")[2].split("=")[1]
      except IndexError:
        query = None
        ID = None
        isExpand = False

      ##print("do_GET():", query, ID, isExpand)

      if isExpand == 'False':
        '''
        if no double click event, it means the query is a new search
        graphNodes dictionaries have to be cleared so that the graph becomes empty
        '''
        GraphNodes.clearDict()
        
      elif isExpand == 'True':
        '''
        if a node is double-clicked, the user intends to expand the node
        so current nodes have to remain in the graph and items in the graphNodes dictionaries stay the same
        '''
      # set error to None and pass it into ui.start()
      error = None
      ui.start(query, ID, error)

      # read from local html file
      w = WebScraper("network-graph.html")
      html = str(w._localSoup("network-graph.html"))
      # send response to user
      self.wfile.write(bytes(html, "utf-8"))

      ##print("path: ", self.path)
      end = time.time()
      print("time taken:", end - start)

    else:
      '''
      otherwise use default do_GET function inherited from parent class (SimpleHTTPRequestHandler)
      documentation on parent class: https://docs.python.org/3/library/http.server.html#http.server.SimpleHTTPRequestHandler
      '''
      super().do_GET()  
      




##### MAIN #####

# create instances of classes
gen = IDGenerator()
GraphNodes = GraphNodes() 
ui = UserInterface()

handler = Handler # Handler class

def runServer(port):
  '''
  This method runs a local server using the socketserver module.
  The code is referenced from from http.server docs: pyvis.readthedocs.io/en/latest/index.html 
  '''
  with socketserver.TCPServer(("", port), handler) as httpd:
      print("Running server at port", port)
      httpd.serve_forever()

def main():
  try:
    # displays url of local host using the default browser
    webbrowser.open("http://127.0.0.1:8080/WikipediaVisualiser")
    runServer(8080)
        
  except OSError:
    print("OSError: Address already in use")
    print("Trying alternate port 8000")
    webbrowser.open("http://127.0.0.1:8000/WikipediaVisualiser")  # this opens a new tab in addition to port 8080
    runServer(8000) # alternate server

'''
If the webbrowser module does not automatically open a browser and display the url,
Do it manually - the local host is at http://127.0.0.1:8080/WikipediaVisualiser
Depending on the port, it could be port 8080 or port 8000
'''


if __name__ == '__main__':  #boilerplate
    main()






