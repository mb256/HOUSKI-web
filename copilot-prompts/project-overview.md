## HOUSKI web

Plan to create websites for local climbing club HOUSKi.   
This is local climbing club based in Pilsen with rich history. Club connects friends with common activities like:   
climbing, mounteneering, expeditions, bouldering, sky-alpinism, cross-country skying and other outdoor activity.   

### Technology

This web page will be developed as Django web app with Python framework and poetry 2.4.x as virtual management tool. Database will be implemented in SQLite database.      

### Structure of web app

The web page will have main info page and several other sections.
There will be public web pages which are visible for everyone and there will be sections which are visible only after login.   
So there will be django user management involved wich fill follow Django best practicies for user management.
   

### Design

Web pages are responsible web-pages so it looks nicelly in PC and in mobile phone as well.   
The webpages will have header with links:
- Home    
- Nástěnka   
- Články   
- Plánované aktivity   
- Kontakty   
- Login   

The main section where default main section is Home page.   
The webpage will have footer section with author information and contacts.

Links will have coresponding code sections:
Home = home   
Nástěnka = board   
Články = articles   
Plánované aktivity = activities    
Kontakty = contacts    
Login = login    


Publically visible pages:   
- home (read only)    
- board (read only)    
- articles (read only)    
- activities (read only)    
- contacts (read only)   
- login (with form for login)   


There will be users with admin rights who can edit anything.
There will be users with rights to see pages, add or edit new artical, add or edit news on board.

When user is login he can according his rights:
- Add new record to the board
- Edit existing board record on the board which was previously created by him
- Add new article
- Edit existing article record in articles which was previously created by him
- Add new activity
- Edit existing activity record in activities which was previously created by him


#### Individual pages design and contant

Over all design of web pages will be dark with black and gray coulours.
Links, text, headlines will be in light color i.e. light grey, white, yellow.
Make web pages with kind of minimalistic design but they should look modern and cool.

#### home page (read only)    

This will display static information about climbing club (exact text content will be added later).
Here will be basic information about club (summary of what club does, number of members, history, ...).

#### board (read only)    

This will be section which works as board where members can place short messages or news. It can be an information about what happening in near future.
About activity like climbing trips, bycicle trips, sky-alpinist trips, interesting talks and presentations.
It will be shorter text cca. 2028 letters with max. 5 pictures which can be added.
Without login users can see board for reading but only after login they can add contetn.
There will be displayed latest 25 messages on the page and paging to display previous 25 board records is possible.

Each news in board will contain:
- Date and time
- author
- potential headline
- text of the news
- Potentially picture or pictures

It should be easy to create new board after login on PC and on mobile phone.

#### articles (read only)    

Articles will display list of articles writtent by members. Articles are longer texts with pictures (max 10 pictures).
Articles are longer descriptions of some events, trips or expeditions.

Each article will contain:
- Date and time
- author
- headline
- text of the article
- Potentially picture or pictures
- labels: climbing, mountains, sky alpinisme, trecking, other sport, kids, pub (labels can be extended over the time) 

It should be easy to create new article after login on PC and on mobile phone.


#### activities (read only)    

This will display official planned club activities in near future and history of official activity. This can be 
methodic workshops, organized climbing trips, club meetups, ...

#### contacts (read only)   

#### login (with form for login)

t.b.d. ...

So this web-page requires user management.
There will be users with admin rights who can edit anything.
There will be users with rights to see pages, add or edit new artical, add or edit News.



Design of the page will be in minimalistic style in shades of dark (black ... grey) and yellow color.

Text for main page and for individual news and articals will be added later via Admin interface.

There will be also default super user 
with name: brouk
password: Admin1234#
