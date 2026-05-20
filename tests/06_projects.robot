*** Settings ***
Documentation       Suite 6: Project create, list, and detail endpoints.
...                 Verifies seeded projects exist, new project creation, uniqueness enforcement,
...                 derived document_count/document_ids, and project_name sanitization.
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session
Test Teardown       Cleanup Created Project


*** Variables ***
${created_project_id}    ${NONE}


*** Test Cases ***
Seeded Projects Exist In List
    [Documentation]    GET /projects must return Project1 (id=1) and Project2 (id=2) from seed.
    ...                Both must appear with correct names in the list response.
    ${projects}=    List Projects
    ${names}=    Create List
    FOR    ${proj}    IN    @{projects}
        Append To List    ${names}    ${proj}[project_name]
    END
    List Should Contain Value    ${names}    Project1
    List Should Contain Value    ${names}    Project2

Create New Project Returns 201 And Appears In List
    [Documentation]    POST /projects with a unique name returns 201 with id, project_name, user_ids.
    ...                The new project must then appear in GET /projects list.
    ${unique_name}=    Evaluate    "TestProj_" + __import__("uuid").uuid4().hex[:8]
    ${proj}=    Create Project    ${unique_name}
    Set Suite Variable    ${created_project_id}    ${proj}[id]
    Should Be Equal    ${proj}[project_name]    ${unique_name}
    Should Not Be Empty    ${proj}[user_ids]
    ${projects}=    List Projects
    ${names}=    Create List
    FOR    ${p}    IN    @{projects}
        Append To List    ${names}    ${p}[project_name]
    END
    List Should Contain Value    ${names}    ${unique_name}

Duplicate Project Name Returns 409
    [Documentation]    POST /projects with an existing project_name must return 409 Conflict.
    ...                Sending "Project1" (seeded) a second time must be rejected.
    Create Project    Project1    expected_status=409
    Set Suite Variable    ${created_project_id}    ${NONE}

Project Detail Returns Document IDs And Count
    [Documentation]    GET /projects/{id} for an existing project returns document_ids list and document_count.
    ...                Both fields must be present; document_count equals the length of document_ids.
    ${detail}=    Get Project    1
    Dictionary Should Contain Key    ${detail}    document_ids
    Dictionary Should Contain Key    ${detail}    document_count
    ${expected_len}=    Get Length    ${detail}[document_ids]
    Should Be Equal As Integers    ${detail}[document_count]    ${expected_len}
    Set Suite Variable    ${created_project_id}    ${NONE}

Project Name HTML Is Sanitized
    [Documentation]    POST /projects with HTML in project_name must strip tags, storing plain text.
    ...                The returned project_name must equal the bleach-cleaned version.
    ...                Uses a random suffix so repeated runs don't collide with prior leftovers.
    ${suffix}=    Evaluate    __import__("uuid").uuid4().hex[:8]
    ${proj}=    Create Project    <b>SanitizedProj_${suffix}</b>
    Set Suite Variable    ${created_project_id}    ${proj}[id]
    Should Be Equal    ${proj}[project_name]    SanitizedProj_${suffix}


*** Keywords ***
Cleanup Created Project
    [Documentation]    No delete endpoint for projects; only log the leftover project id for info.
    ...                Created projects are harmless test artifacts on the server.
    Log    Cleanup: created_project_id=${created_project_id} (no delete endpoint; artifact remains)
