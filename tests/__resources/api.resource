*** Settings ***
Documentation       Shared keywords for ReqEngine API tests.
...                 Provides session setup and reusable request helpers for all suites.
Library             RequestsLibrary
Library             Collections
Resource            variables.resource


*** Keywords ***
Create API Session
    [Documentation]    Create a RequestsLibrary session named 'api' pointing at ${API_BASE_URL}.
    ...                Called from Suite Setup in each test suite.
    Create Session    api    ${API_BASE_URL}    headers={"Content-Type": "application/json"}

Reserve New ID
    [Documentation]    Call POST /requirements/reserve-id and return the parsed JSON body.
    ...                Returns a dict with keys: requirement_number (int), project_id (str).
    ${resp}=    Post On Session    api    /requirements/reserve-id    expected_status=200
    RETURN    ${resp.json()}

Create Requirement
    [Documentation]    POST /requirements with provided fields and return the parsed JSON body.
    ...                Arguments: requirement_number (int), project_id (str), title (str),
    ...                description (str), status (str), requirement_type (str), revision (str).
    [Arguments]    ${requirement_number}    ${project_id}    ${title}
    ...            ${description}=    ${status}=draft
    ...            ${requirement_type}=system_requirement    ${revision}=0.1
    ${payload}=    Create Dictionary
    ...            requirement_number=${requirement_number}
    ...            project_id=${project_id}
    ...            title=${title}
    ...            description=${description}
    ...            status=${status}
    ...            requirement_type=${requirement_type}
    ...            revision=${revision}
    ${resp}=    Post On Session    api    /requirements    json=${payload}    expected_status=201
    RETURN    ${resp.json()}

Get Requirement
    [Documentation]    GET /requirements/{req_id} and return the parsed JSON body.
    ...                Returns the full requirement detail dict including list_of_links.
    [Arguments]    ${req_id}
    ${resp}=    Get On Session    api    /requirements/${req_id}    expected_status=200
    RETURN    ${resp.json()}

List Requirements
    [Documentation]    GET /requirements and return the parsed JSON list of summary dicts.
    ...                Returns a list of summary objects (id, project_id, title, status, etc.).
    ${resp}=    Get On Session    api    /requirements    expected_status=200
    RETURN    ${resp.json()}

Update Requirement
    [Documentation]    PUT /requirements/{req_id} with provided fields and return parsed JSON.
    ...                Arguments: req_id (int), title, description, status, requirement_type, revision.
    [Arguments]    ${req_id}    ${title}    ${description}=    ${status}=draft
    ...            ${requirement_type}=system_requirement    ${revision}=0.1
    ${payload}=    Create Dictionary
    ...            title=${title}
    ...            description=${description}
    ...            status=${status}
    ...            requirement_type=${requirement_type}
    ...            revision=${revision}
    ${resp}=    Put On Session    api    /requirements/${req_id}    json=${payload}    expected_status=200
    RETURN    ${resp.json()}

Delete Requirement
    [Documentation]    DELETE /requirements/{req_id}; expects 204 No Content by default.
    ...                Pass expected_status=any to allow 404 (e.g. best-effort teardown).
    [Arguments]    ${req_id}    ${expected_status}=204
    ${resp}=    Delete On Session    api    /requirements/${req_id}    expected_status=${expected_status}
    RETURN    ${resp}

Create Link
    [Documentation]    POST /links with link_type, start and destination project_ids; returns parsed JSON.
    ...                Arguments: link_type (str), start_project_id (str), dest_project_id (str).
    [Arguments]    ${link_type}    ${start_project_id}    ${dest_project_id}    ${expected_status}=201
    ${payload}=    Create Dictionary
    ...            link_type=${link_type}
    ...            link_start_project_id=${start_project_id}
    ...            link_destination_project_id=${dest_project_id}
    ${resp}=    Post On Session    api    /links    json=${payload}    expected_status=${expected_status}
    RETURN    ${resp.json()}

Delete Link
    [Documentation]    DELETE /links/{link_id}; expects 204 No Content by default.
    ...                Returns the raw response object for optional further inspection.
    [Arguments]    ${link_id}    ${expected_status}=204
    ${resp}=    Delete On Session    api    /links/${link_id}    expected_status=${expected_status}
    RETURN    ${resp}
