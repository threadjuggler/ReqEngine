This project shall be started from scratch for my learning.

the file implementation_rules.md contains rules the agent shall stick to.

I want to have an application for editing linking and managing requirements and testcases like Polarion but a lighter version of that.
THe backend shall be a python fastapi app with postgresql access and redis support and as many workers as needed.
The project shall contain a docker file that when someone clones the repository that all necessary services are started befor the backend processs
The package robotframework shall be used for testing the backendinstead of pytest
The database shall be versioned with alembic
The frontend shall be a react.js app
The uv package manager shall be used and the ruff package for syntax checks

The implementation of user administration is saved for a later time in the progression of this project so in the first step when the user surfs to the main page of the frontend the frontend shall show a list with all requirements in the database 
for the first step the user_name 'User1' shall be used where it is needed.

I would like to start with a simple app as the basis for further incremental development.
As the first realization step I would like to have a frontend where I can create new requirements, edit or delete old ones and browse through a list of all requirements stored in that postgresql database table.

The requirement object shall have the following attributes:
id: int for database purpose unique and the primary index parameter
project_id : string 100 characters length
The variable project_name will play a role later when different projects can be managed but not now I will tell when it is time to implement project administration. for now project_name shall be a hard coded variable set to "Project1"
the project_id string shall be unique for each requirement that is created  it shall have the following format: f'{project_name}_{requirement_number:08}" 
requirement_number shall be an integer that starts at 1 and is incremented for each requirement in the project that is connected to project_name 'Project1'
it needs to be considered that if later more tan one project exists that the requirement_number shall start at 1 and be incremented individually in each project later on.
when  new requirement is created a new project_id shall be created for this requirement and be shown in the edit form as a non-editable label. if in the meantime another requirement is created the project_id shall be created new so that two users can edit two different requirement forms and save their result independently.
title: string 200 characters
description: string 500 characters
list_of_links: list of ids of link objects (the attributes of the link object are defined later in this file) self growing list
status: string 20 charaters 'draft', 'in_review','wait_for_approval','approved','expired',
requirement_type: 'string 80 chars can be 'customer requirement', 'system_requirement', 'software_requirement', 'hardware_requirement'
author: string 100 chars contains the name of the user who pressed th create button
last_edited_by: string 100 chars contains the name of the user who edited at last
created_on: timestamp when the create button had been pressed
last_edited_on: timestamp last time when 'Save' Button was pressed
revision: string 30 chars
in the form to edit the requirements there shall be the buttons 'Save', 'Clear Form' , 'Discard'
before the requirement is saved the input data shall be checked for no injection attacks and only html or Text is allowed (utf-8)
in the form for editing a requiement there shall be a text area with horizontal and vertical slider that contains a list of all link in the list_of_links with a minus button at the right hand side of the list that would delete the link id from the list_of_links (in this case when the link only has link_start or link_destination it shall be deleted from the database)
below the text area there shall be a button 'Create Link' that opens a dialog where the user can enter link_start and link_destination manually and click a 'Save' Button to create that link object and add th id into the list_of_links list. there shall be a 'Discard' button which closes the dialog without doing anything. 


Link Object:
id: unique primary key for database operations
project_id: same as for requirement 
link_type: string 60 chars , can be 'refines' or 'depends_on'
link_destination: id of a requirement, must never be the same as link_start
created_on: timestamp
last_edited_on: timestamp
link_start: id of a requirement, must never be the same as link_destination
there shall be no form to edit link objects in the first step


Testcase Object:
id: same as before
project_id: same as before
title: string 100 chars
description: string 1000 chars 
test_state: 'draft', 'in_review', 'waiting_for_approval','approved'
author: username 
last_edited_by: username 
created_on: timestamp
last_edited_on: timestamp 
revision: string 30 chars
list_of_links: int representing a list of id (database index of a link_object)
all strings shall be protectd against injection attacks and 
for the first step please create three test cases on the database/table with the given attributes and title and description have short lore ipsum texts


The frontend first step of project:
all as decribed above 
if the user views  a requirement the lines in the list of links shall contain a html link that when i press it the object on the other side of the link, the number that is unequal to the id of the object that the form is actually showing (that can be destination or start in the attributes of the link) shall be opened in the form, if anything has been edited a dialog shall confirm the discarding of the changes

create the tasks.md first and ask if anything needs further explanation or decisions