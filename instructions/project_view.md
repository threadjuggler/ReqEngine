there shall be a link on the start page that says 'Project view' and when the user clicks on it the project view is opened
on the project view the user shall see a list with all documents that have been created with the 'Create New Document' button. this button shall be on the button bar on the top of the view.

there needs to be a project object in the database
with these attributes:
id: primary key, unique
project_name : string 120 chars
document_ids: self growing list of int representing the id attribute of all in this project created documents
user_ids : growing list of ints defaults to [10, 20] maybe stored as a json string


