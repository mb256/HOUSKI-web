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
- Login (login will change to logout after user log in)
- Profil (link to edit user settings is wisible only when user is logged in)   
And there will be small logo of climbing club on the left site of header.

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
There will be picture of the week on the right side of text.

Picture of the week will have short description under the picture (i.e. what is on the picture) and author.
Picture of the week will be visible on the home page but it will have separate independent model.
Picture of the week can be changed by admin only.

#### board (read only)    

This will be section which works as board where members can place short messages or news. It can be an information about what happening in near future.
About activity like climbing trips, bycicle trips, sky-alpinist trips, interesting talks and presentations.
It will be shorter text cca. 2048 letters with max. 5 pictures which can be added.
Without login users can see board for reading but only after login they can add contetn.
There will be displayed latest 25 messages on the page and paging to display previous 25 board records is possible.
The user who created news on the board can edit this news or delete it.

Each news in board will contain:
- Date and time
- author
- potential headline
- text of the news
- Potentially picture or pictures

It should be easy to create new news on the board after login on PC and on mobile phone.
There will be rich text editor for text edit. Just with the basic functionality.
Headline, bolt text, cursiva, bullet points, ...

#### articles (read only)    

Articles will display list of articles writtent by members. Articles are longer texts with pictures (max 10 pictures).
Articles are longer descriptions of some events, trips or expeditions.
User who created the article can edit or delete this article.

Each article will contain:
- Date and time
- author
- headline
- text of the article
- Potentially picture or pictures
- labels: climbing, mountains, sky alpinisme, trecking, other sport, kids, pub (labels can be extended over the time)
There will be separate Category model for labels 

It should be easy to create new article after login on PC and on mobile phone.
There will be rich text editor for text edit. Just with the basic functionality.
Headline, bolt text, cursiva, bullet points, ...

#### activities (read only)    

This will display official planned club activities in near future and history of official activity. This can be 
methodic workshops, organized climbing trips, club meetups, ...
Activity can be added by any logged in user. 
User who created activity can edit or delete this activity.

Activities will contain:
- name
- start date
- end date
- location
- description

There will be rich text editor for text edit. Just with the basic functionality.
Headline, bolt text, cursiva, bullet points, ...

#### contacts (read only)   

Contacts will display public contacts for some team members.
It will be static page for now. No model needed.

#### login (with form for login)

Login page will have form for login (user name + password).
Each member is able to change it's own user data and change it's own password.
First password will be generated when user is created by super user.
Than during first login user is asked to change its password for something unique (secure password is required).
Password for first login will be generated and distributed by superuser.

When user forget its password there is mechanism for reseting user password manually by admin user.
Admin will provide this generated password to the user and after first login user is required to change generated password to his own password.

Django user module will be used.
User will have at minimum these parameters:
- user name (for login)
- email (can be also used for login)
- password (is handled according best security rules practicies)
- telephone (not required)
- roles (roles in the club: (předseda, tajemník, pokladník, člen, instruktor). User can have multiple roles)

So this web-page requires user management.
There will be users with admin rights who can edit anything.
There will be users with rights to see pages, add or edit new artical, add or edit News.


### Style

Web pages design will be in minimalistic style in shades of black and shades of grey for background and shades of white and yellow color. Make webpage look modern and stylish in the same time.
Visuals and design will be separated in static css, js and other folders.
Visualisation will be using best practicies to separate graphics from logic and it should be easy to change it over the time (extend or change parts or whole).


There will be also default super user 
with name: brouk
password: Admin1234#

Image storage — local media files will be used for storrage. Original image files are compressed when uploaded to Max file size cca 400 KB (landscape 1200–1600 px wide image and and equivalently for portrait shape) ?

Use pagination for Articles which looks modern and nice and is typical for this type of web sites.

Backang of the web will be in English but frontend (labels, buttons, headlines, text, ...) will be in Czech naguage. Define language according this.

First there will be local development only and testing in Development Django server.
But in the end it will be deployed into pythonanywhere.com hosting. So there will be also description how to make update and deployement into this web portal.
