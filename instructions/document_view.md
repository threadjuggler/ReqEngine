the requirements management tool shall have a document view.
there shall be a link on the main page saying 'document view' which leads the browser to a virtual editable DIN A 4 document.
The user shall be able to write text into this document which entends the document into the downward vertical direction as much as is needed to keep all the entered texts
on the top tere should be a button bar same like in any graphical text editor with the possibility to configure the text style and font and font size etc. 
This document view shall provide the user with a possibility to add headings of levels 'Heading 1' the biggest heading style and the highest level in the content overview to 'heading 8' the smallest in font size and the lowest in the chapter hierarchie.
the first entry in this drop down menu should always be 'Standard' for the user to choose the standard text style.
when the user chooses a heading 1 to 8 then only this line where the cursor is at the moment is formatted in this style and the chapter number is automatically added to the start of the line e.g. user chooses heading 1 then the chapter number is one digits X if the  user chooses heading 2 the chapter number would be two digit separated by a dot X.X, the X represents the latest number in the chapter hierarchy. e.g. previous chapter was 1.3 then choosing header 1 would lead to the chpter number 2  if the last chapter number is 4.5.5 and the ser chooses heading 4 than the chapter number would be 4.5.5.1
the default color for the standard text style is black and font Arial True Type and the font size is 10
the default color for all the headings is dark gray and style bold
also in the button bar on the top of this view there shall be a plus button that gives the user the opportunity to add a requirement of the given requirement types
does the user choose to add a requirement the project name of the requirement is added on top of a black framed box on the left hand side. in side the box the label 'Title:' is shown 
with a text field of one line to enter the requirement's title 
below that there shall be the label 'Description:' and a text area for the user to enter the description in the same way as in the text field in the form that is opened when the user creates a new requirement.

to store such documents in the database there shall be a docmument table for the document objects.
attributes:
id: int primary unique index
project_id: created in the same way as for all other objects
project_id_number: int the database id of the project object is is attached to. 
created_on: timestamp when a new document is created
author: user that created that document
last_change_by: user who pressed save last
last_edit_on: timestap of last time save was pressed
document_content: somehow all objects and texts that are entered in the document view need to be stored here maybe in json format 


