*** Settings ***
Documentation       Suite 1: Requirement CRUD happy path.
...                 Exercises reserve-id, create, get, list, update, and delete for a requirement.
Resource            __resources/api.resource
Suite Setup         Create API Session
Test Teardown       Cleanup Created Requirement


*** Variables ***
${created_req_id}       ${NONE}
${created_project_id}   ${NONE}


*** Test Cases ***
Reserve ID Returns Valid project_id
    [Documentation]    POST /requirements/reserve-id must return 200 with a valid project_id.
    ${reserved}=    Reserve New ID
    Should Not Be Empty    ${reserved}[project_id]
    Should Match Regexp    ${reserved}[project_id]    ^Project1_\\d{8}$
    Should Be True    ${reserved}[requirement_number] >= 1

Create Requirement Returns 201 With Correct Fields
    [Documentation]    POST /requirements with valid body must return 201 and match sent fields.
    ${reserved}=    Reserve New ID
    ${req}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    Test Title CRUD    Test description    draft    system_requirement    0.1
    Set Suite Variable    ${created_req_id}       ${req}[id]
    Set Suite Variable    ${created_project_id}   ${req}[project_id]
    Should Be Equal    ${req}[title]                Test Title CRUD
    Should Be Equal    ${req}[status]               draft
    Should Be Equal    ${req}[requirement_type]      system_requirement
    Should Be Equal    ${req}[project_id]            ${reserved}[project_id]
    Should Be Equal As Integers    ${req}[requirement_number]    ${reserved}[requirement_number]
    Length Should Be    ${req}[list_of_links]    0

Get Requirement Returns Fields And Empty Links
    [Documentation]    GET /requirements/{id} after create must return fields and empty list_of_links.
    ${reserved}=    Reserve New ID
    ${created}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    Title For Get Test    A description    draft    customer_requirement
    Set Suite Variable    ${created_req_id}       ${created}[id]
    Set Suite Variable    ${created_project_id}   ${created}[project_id]
    ${req}=    Get Requirement    ${created}[id]
    Should Be Equal    ${req}[title]             Title For Get Test
    Should Be Equal    ${req}[description]       A description
    Length Should Be    ${req}[list_of_links]    0

List Requirements Contains Created Row
    [Documentation]    GET /requirements list must include the requirement just created.
    ${reserved}=    Reserve New ID
    ${created}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    Title For List Test    ${EMPTY}    draft    software_requirement
    Set Suite Variable    ${created_req_id}       ${created}[id]
    Set Suite Variable    ${created_project_id}   ${created}[project_id]
    ${list}=    List Requirements
    ${found}=    Set Variable    ${FALSE}
    FOR    ${item}    IN    @{list}
        IF    ${item}[id] == ${created}[id]
            Set Test Variable    ${found}    ${TRUE}
        END
    END
    Should Be True    ${found}    msg=Created requirement not found in list response

Update Requirement Returns 200 And Changed Fields
    [Documentation]    PUT /requirements/{id} must return 200 and persist the new title and status.
    ${reserved}=    Reserve New ID
    ${created}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    Original Title    ${EMPTY}    draft    hardware_requirement
    Set Suite Variable    ${created_req_id}       ${created}[id]
    Set Suite Variable    ${created_project_id}   ${created}[project_id]
    ${old_edited}=    Set Variable    ${created}[last_edited_on]
    ${updated}=    Update Requirement
    ...    ${created}[id]    Updated Title    New description    approved    hardware_requirement    1.0
    Should Be Equal    ${updated}[title]     Updated Title
    Should Be Equal    ${updated}[status]    approved
    Should Be Equal    ${updated}[revision]  1.0

Delete Requirement Returns 204 And Then 404
    [Documentation]    DELETE /requirements/{id} must return 204; subsequent GET must return 404.
    ${reserved}=    Reserve New ID
    ${created}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    Title To Delete    ${EMPTY}    draft    system_requirement
    # Immediately delete so teardown finds nothing to clean
    Set Suite Variable    ${created_req_id}       ${NONE}
    Set Suite Variable    ${created_project_id}   ${NONE}
    Delete Requirement    ${created}[id]
    ${resp}=    Get On Session    api    /requirements/${created}[id]    expected_status=404
    Should Be Equal As Integers    ${resp.status_code}    404


*** Keywords ***
Cleanup Created Requirement
    [Documentation]    Best-effort DELETE of the requirement created during the test.
    ...                Tolerates 404 if the test already deleted it.
    IF    $created_req_id is not None
        Delete Requirement    ${created_req_id}    expected_status=any
    END
