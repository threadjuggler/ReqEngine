*** Settings ***
Documentation       Suite 4: Input sanitization.
...                 Verifies that HTML script tags are stripped, oversized titles are rejected,
...                 and dangerous img tags are removed from descriptions.
Resource            __resources/api.resource
Suite Setup         Create API Session
Test Teardown       Cleanup Sanitization Req


*** Variables ***
${sanitized_req_id}    ${NONE}


*** Test Cases ***
Script Tag In Title Is Stripped To Plain Text
    [Documentation]    POST with a title containing a script tag must succeed (201).
    ...                Persisted title must contain the inner text only (bleach strips tags).
    ${reserved}=    Reserve New ID    Project1
    ${payload}=    Create Dictionary
    ...    requirement_number=${reserved}[requirement_number]
    ...    project_id=${reserved}[project_id]
    ...    project_id_number=${1}
    ...    title=<script>alert(1)</script>
    ...    description=${EMPTY}
    ...    status=draft
    ...    requirement_type=system_requirement
    ...    revision=0.1
    ${resp}=    Post On Session    api    /requirements    json=${payload}    expected_status=201
    ${req}=    Set Variable    ${resp.json()}
    Set Suite Variable    ${sanitized_req_id}    ${req}[id]
    Should Be Equal    ${req}[title]    alert(1)
    ${fetched}=    Get Requirement    ${req}[id]
    Should Be Equal    ${fetched}[title]    alert(1)

Title Exceeding 200 Chars Is Rejected
    [Documentation]    POST with a 201-character title must return 422 (Pydantic length validation).
    ${reserved}=    Reserve New ID    Project1
    ${long_title}=    Evaluate    "A" * 201
    ${payload}=    Create Dictionary
    ...    requirement_number=${reserved}[requirement_number]
    ...    project_id=${reserved}[project_id]
    ...    project_id_number=${1}
    ...    title=${long_title}
    ...    description=${EMPTY}
    ...    status=draft
    ...    requirement_type=system_requirement
    ...    revision=0.1
    Post On Session    api    /requirements    json=${payload}    expected_status=422

Img Tag In Description Is Stripped
    [Documentation]    POST with an img onerror tag in description must succeed (201).
    ...                Persisted description must contain no img tag.
    ${reserved}=    Reserve New ID    Project1
    ${desc_with_img}=    Set Variable    Safe text <img src=x onerror=alert(1)> more text
    ${payload}=    Create Dictionary
    ...    requirement_number=${reserved}[requirement_number]
    ...    project_id=${reserved}[project_id]
    ...    project_id_number=${1}
    ...    title=Img Tag Test
    ...    description=${desc_with_img}
    ...    status=draft
    ...    requirement_type=system_requirement
    ...    revision=0.1
    ${resp}=    Post On Session    api    /requirements    json=${payload}    expected_status=201
    ${req}=    Set Variable    ${resp.json()}
    ${existing}=    Set Variable    ${sanitized_req_id}
    IF    $existing is None
        Set Suite Variable    ${sanitized_req_id}    ${req}[id]
    ELSE
        Delete Requirement    ${existing}    expected_status=any
        Set Suite Variable    ${sanitized_req_id}    ${req}[id]
    END
    Should Not Contain    ${req}[description]    <img
    ${fetched}=    Get Requirement    ${req}[id]
    Should Not Contain    ${fetched}[description]    <img


*** Keywords ***
Cleanup Sanitization Req
    [Documentation]    Best-effort DELETE of the requirement created in the sanitization test.
    ...                Tolerates 404 if the test left nothing or already cleaned up.
    IF    $sanitized_req_id is not None
        Delete Requirement    ${sanitized_req_id}    expected_status=any
        Set Suite Variable    ${sanitized_req_id}    ${NONE}
    END
