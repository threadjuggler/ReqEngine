*** Settings ***
Documentation       Suite 2: Link create/delete and cascade rules.
...                 Tests link creation, validation, GET side-effects, deletion, and cascade on requirement delete.
...                 Also verifies that cross-project links are rejected with 422.
Resource            __resources/api.resource
Suite Setup         Create API Session
Test Teardown       Cleanup Linked Requirements


*** Variables ***
${req_a_id}         ${NONE}
${req_b_id}         ${NONE}
${link_id}          ${NONE}


*** Test Cases ***
Create Link Between Two Requirements
    [Documentation]    POST /links with valid start/dest returns 201 and link_id + link project_id.
    ${a}=    Reserve And Create Requirement    Req A For Links
    ${b}=    Reserve And Create Requirement    Req B For Links
    Set Suite Variable    ${req_a_id}    ${a}[id]
    Set Suite Variable    ${req_b_id}    ${b}[id]
    ${link}=    Create Link    refines    ${a}[project_id]    ${b}[project_id]
    Set Suite Variable    ${link_id}    ${link}[id]
    Should Match Regexp    ${link}[project_id]    ^Project1_\\d{8}$
    Should Be Equal As Integers    ${link}[link_start]        ${a}[id]
    Should Be Equal As Integers    ${link}[link_destination]  ${b}[id]

GET Req A Shows Link With Other Side B
    [Documentation]    After creating a link, GET req A must include the link with other_side = req B.
    ${a}=    Reserve And Create Requirement    Req A Side Check
    ${b}=    Reserve And Create Requirement    Req B Side Check
    Set Suite Variable    ${req_a_id}    ${a}[id]
    Set Suite Variable    ${req_b_id}    ${b}[id]
    ${link}=    Create Link    refines    ${a}[project_id]    ${b}[project_id]
    Set Suite Variable    ${link_id}    ${link}[id]
    ${detail_a}=    Get Requirement    ${a}[id]
    Length Should Be    ${detail_a}[list_of_links]    1
    ${litem}=    Set Variable    ${detail_a}[list_of_links][0]
    Should Be Equal As Integers    ${litem}[link_id]              ${link}[id]
    Should Be Equal As Integers    ${litem}[other_side][id]       ${b}[id]
    Should Be Equal                ${litem}[other_side][project_id]    ${b}[project_id]

GET Req B Shows Link With Other Side A
    [Documentation]    After creating a link, GET req B must include the link with other_side = req A.
    ${a}=    Reserve And Create Requirement    Req A Other Side
    ${b}=    Reserve And Create Requirement    Req B Other Side
    Set Suite Variable    ${req_a_id}    ${a}[id]
    Set Suite Variable    ${req_b_id}    ${b}[id]
    ${link}=    Create Link    depends_on    ${a}[project_id]    ${b}[project_id]
    Set Suite Variable    ${link_id}    ${link}[id]
    ${detail_b}=    Get Requirement    ${b}[id]
    Length Should Be    ${detail_b}[list_of_links]    1
    ${litem}=    Set Variable    ${detail_b}[list_of_links][0]
    Should Be Equal As Integers    ${litem}[link_id]              ${link}[id]
    Should Be Equal As Integers    ${litem}[other_side][id]       ${a}[id]

Self Link Is Rejected With 422
    [Documentation]    POST /links where start == dest must return 422 (validation error).
    ${a}=    Reserve And Create Requirement    Req Self Link
    Set Suite Variable    ${req_a_id}    ${a}[id]
    Set Suite Variable    ${req_b_id}    ${NONE}
    Set Suite Variable    ${link_id}    ${NONE}
    Create Link    refines    ${a}[project_id]    ${a}[project_id]    expected_status=422

Link To Non-Existent Requirement Returns 404
    [Documentation]    POST /links with a dest project_id that does not exist must return 404.
    ${a}=    Reserve And Create Requirement    Req Non Exist Link
    Set Suite Variable    ${req_a_id}    ${a}[id]
    Set Suite Variable    ${req_b_id}    ${NONE}
    Set Suite Variable    ${link_id}    ${NONE}
    Create Link    refines    ${a}[project_id]    Project1_99999999    expected_status=404

Delete Link Removes Link From Requirements
    [Documentation]    DELETE /links/{link_id} returns 204; GET req A must then have empty list_of_links.
    ${a}=    Reserve And Create Requirement    Req A Delete Link
    ${b}=    Reserve And Create Requirement    Req B Delete Link
    Set Suite Variable    ${req_a_id}    ${a}[id]
    Set Suite Variable    ${req_b_id}    ${b}[id]
    ${link}=    Create Link    refines    ${a}[project_id]    ${b}[project_id]
    Set Suite Variable    ${link_id}    ${NONE}
    Delete Link    ${link}[id]
    ${detail_a}=    Get Requirement    ${a}[id]
    Length Should Be    ${detail_a}[list_of_links]    0

Cascade Delete Req A Removes Link From Req B
    [Documentation]    Deleting req A must cascade-delete the link; GET req B shows empty list_of_links.
    ${a}=    Reserve And Create Requirement    Req A Cascade
    ${b}=    Reserve And Create Requirement    Req B Cascade
    Set Suite Variable    ${link_id}    ${NONE}
    ${link}=    Create Link    refines    ${a}[project_id]    ${b}[project_id]
    # Delete req A; set req_a_id to NONE so teardown skips it (already gone)
    Delete Requirement    ${a}[id]
    Set Suite Variable    ${req_a_id}    ${NONE}
    Set Suite Variable    ${req_b_id}    ${b}[id]
    ${detail_b}=    Get Requirement    ${b}[id]
    Length Should Be    ${detail_b}[list_of_links]    0

Cross-Project Link Is Rejected With 422
    [Documentation]    POST /links with start in Project1 and dest in Project2 must return 422.
    ...                Both endpoints must belong to the same project_id_number.
    ${reserved_p1}=    Reserve New ID    Project1
    ${req_p1}=    Create Requirement
    ...    ${reserved_p1}[requirement_number]    ${reserved_p1}[project_id]
    ...    Cross Link P1 Req    ${EMPTY}    draft    system_requirement    0.1    ${1}
    Set Suite Variable    ${req_a_id}    ${req_p1}[id]
    ${reserved_p2}=    Reserve New ID    Project2
    ${req_p2}=    Create Requirement
    ...    ${reserved_p2}[requirement_number]    ${reserved_p2}[project_id]
    ...    Cross Link P2 Req    ${EMPTY}    draft    system_requirement    0.1    ${2}
    Set Suite Variable    ${req_b_id}    ${req_p2}[id]
    Set Suite Variable    ${link_id}    ${NONE}
    # project_id_number=1 but dest belongs to project 2 → 422
    Create Link    refines    ${req_p1}[project_id]    ${req_p2}[project_id]
    ...    expected_status=422    project_id_number=${1}


*** Keywords ***
Reserve And Create Requirement
    [Documentation]    Reserve an ID from Project1 and create a requirement with the given title.
    ...                Returns the full requirement detail dict including id and project_id.
    [Arguments]    ${title}
    ${reserved}=    Reserve New ID    Project1
    ${req}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    ${title}    ${EMPTY}    draft    system_requirement    0.1    ${1}
    RETURN    ${req}

Cleanup Linked Requirements
    [Documentation]    Best-effort teardown: delete the link (if any) then req A and req B.
    ...                Tolerates 404 so previous test-level deletes do not cause failures.
    IF    $link_id is not None
        Delete Link    ${link_id}    expected_status=any
    END
    IF    $req_a_id is not None
        Delete Requirement    ${req_a_id}    expected_status=any
    END
    IF    $req_b_id is not None
        Delete Requirement    ${req_b_id}    expected_status=any
    END
