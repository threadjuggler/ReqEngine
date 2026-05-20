*** Settings ***
Documentation       Suite 8: Document with embedded requirement-ref nodes.
...                 Tests the full flow of reserving an ID, creating a requirement, embedding
...                 a requirement-ref in a document, and validating the ref attrs rules.
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session
Test Teardown       Cleanup Inline Requirement Test


*** Variables ***
${inline_req_id}    ${NONE}
${inline_doc_id}    ${NONE}


*** Test Cases ***
Full Flow Reserve Requirement Embed In Document And Fetch
    [Documentation]    Reserve ID → POST requirement → create document → PUT with requirement-ref node.
    ...                GET document must still contain the requirement-ref node.
    ...                GET /requirements/{id} must also return the requirement (ref not dangling).
    ${reserved}=    Reserve New ID    Project1
    ${req}=    Create Requirement
    ...    ${reserved}[requirement_number]    ${reserved}[project_id]
    ...    Inline Req Title    Some description    draft    system_requirement    0.1    ${1}
    Set Suite Variable    ${inline_req_id}    ${req}[id]
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${inline_doc_id}    ${doc}[id]
    ${ref_attrs}=    Create Dictionary    requirement_id=${req}[id]    project_id=${req}[project_id]
    ${ref_node}=    Create Dictionary    type=requirement-ref    attrs=${ref_attrs}
    ${root_content}=    Create List    ${ref_node}
    ${doc_content}=    Create Dictionary    type=doc    content=${root_content}
    ${updated}=    Update Document    ${doc}[id]    ${doc_content}
    ${fetched}=    Get Document    ${doc}[id]
    ${first_node}=    Set Variable    ${fetched}[document_content][content][0]
    Should Be Equal    ${first_node}[type]    requirement-ref
    Should Be Equal As Integers    ${first_node}[attrs][requirement_id]    ${req}[id]
    Get Requirement    ${req}[id]

Requirement Ref With Non-Int requirement_id Returns 422
    [Documentation]    PUT /documents/{id} with requirement-ref where requirement_id is a string → 422.
    ...                The sanitizer enforces that requirement_id must be an integer.
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${inline_doc_id}    ${doc}[id]
    ${ref_attrs}=    Create Dictionary    requirement_id=not-an-int    project_id=Project1
    ${ref_node}=    Create Dictionary    type=requirement-ref    attrs=${ref_attrs}
    ${root_content}=    Create List    ${ref_node}
    ${bad_content}=    Create Dictionary    type=doc    content=${root_content}
    Update Document    ${doc}[id]    ${bad_content}    expected_status=422

Requirement Ref With project_id Over 100 Chars Returns 422
    [Documentation]    PUT /documents/{id} with requirement-ref where project_id is >100 chars → 422.
    ...                The sanitizer enforces string project_id must not exceed 100 characters.
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${inline_doc_id}    ${doc}[id]
    ${long_pid}=    Evaluate    "P" * 101
    ${ref_attrs}=    Create Dictionary    requirement_id=${1}    project_id=${long_pid}
    ${ref_node}=    Create Dictionary    type=requirement-ref    attrs=${ref_attrs}
    ${root_content}=    Create List    ${ref_node}
    ${bad_content}=    Create Dictionary    type=doc    content=${root_content}
    Update Document    ${doc}[id]    ${bad_content}    expected_status=422


*** Keywords ***
Cleanup Inline Requirement Test
    [Documentation]    Best-effort teardown: delete the document then the requirement created during test.
    ...                Tolerates 404 from previous test-level deletes.
    IF    $inline_doc_id is not None
        Delete Document    ${inline_doc_id}    expected_status=any
        Set Suite Variable    ${inline_doc_id}    ${NONE}
    END
    IF    $inline_req_id is not None
        Delete Requirement    ${inline_req_id}    expected_status=any
        Set Suite Variable    ${inline_req_id}    ${NONE}
    END
