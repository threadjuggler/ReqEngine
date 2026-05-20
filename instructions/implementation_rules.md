this file contains rules that should be considered by any agent that starts to work in this project. it shall be used for creating a .claude.md file , a memory.md file or any other file that has influence on the work of the agents

to safe tokens an opus agent shall spawn at least one implementer agent of type Sonnet 4.6 who implements the python files and who implements the robotframework tests
the opus agent shall plan the tasks of the implementer agent before spawning
and check the result after wards
the opus agent shall log the proggress in a file named tasks.md
the implementer agent shall always check if the package he is supposed to use has changed after his learning phase and adaptif possible to the new version of the python or robotframework package
if something is not clear any agent shall always ask before starting to work
each python method or test case shall have a doc string of maximum 5 lines that describe roughly what the function is doing.
to implement tests always the package robotframework for python shall be used
the ruff package shall be used for syntax checks 



