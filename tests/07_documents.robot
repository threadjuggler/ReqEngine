*** Settings ***
Documentation       Suite 7: Document CRUD and content sanitization.
...                 Covers create, GET roundtrip, PUT with valid and invalid content, text sanitization,
...                 and DELETE with subsequent 404 verification.
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session
Test Teardown       Cleanup Created Document


*** Variables ***
${created_doc_id}    ${NONE}


*** Test Cases ***
Create Blank Document Under Project1
    [Documentation]    POST /documents with project_id_number=1 returns 201 with empty content dict.
    ...                author must equal User1; document_content must be {type:doc, content:[]}.
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${created_doc_id}    ${doc}[id]
    Should Be Equal    ${doc}[author]    User1
    Should Be Equal    ${doc}[document_content][type]    doc
    ${content_list}=    Set Variable    ${doc}[document_content][content]
    Length Should Be    ${content_list}    0

Document project_id Follows Project1 Format
    [Documentation]    The allocated project_id of a new document must match ^Project1_\d{8}$ format.
    ...                Consecutive documents must have different project_ids (counter increments).
    ${doc1}=    Create Document    ${1}
    ${doc2}=    Create Document    ${1}
    Should Match Regexp    ${doc1}[project_id]    ^Project1_\\d{8}$
    Should Match Regexp    ${doc2}[project_id]    ^Project1_\\d{8}$
    Should Not Be Equal    ${doc1}[project_id]    ${doc2}[project_id]
    Set Suite Variable    ${created_doc_id}    ${doc2}[id]
    Delete Document    ${doc1}[id]

PUT Valid Content Roundtrips Correctly
    [Documentation]    PUT /documents/{id} with a valid paragraph+text node, then GET returns same content.
    ...                The text value must survive the bleach roundtrip unchanged (no HTML present).
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${created_doc_id}    ${doc}[id]
    ${text_node}=    Create Dictionary    type=text    text=Hello world
    ${content_list}=    Create List    ${text_node}
    ${para_node}=    Create Dictionary    type=paragraph    content=${content_list}
    ${root_content}=    Create List    ${para_node}
    ${new_content}=    Create Dictionary    type=doc    content=${root_content}
    ${updated}=    Update Document    ${doc}[id]    ${new_content}
    Should Be Equal    ${updated}[document_content][type]    doc
    ${fetched}=    Get Document    ${doc}[id]
    ${fetched_text}=    Set Variable    ${fetched}[document_content][content][0][content][0][text]
    Should Be Equal    ${fetched_text}    Hello world

PUT Disallowed Node Type Returns 422
    [Documentation]    PUT /documents/{id} with a node type not in the allowlist must return 422.
    ...                Allowed types: doc, paragraph, heading, requirement-ref, text.
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${created_doc_id}    ${doc}[id]
    ${bad_node}=    Create Dictionary    type=table
    ${root_content}=    Create List    ${bad_node}
    ${bad_content}=    Create Dictionary    type=doc    content=${root_content}
    Update Document    ${doc}[id]    ${bad_content}    expected_status=422

PUT Heading Level 9 Returns 422
    [Documentation]    PUT /documents/{id} with heading.attrs.level=9 must return 422.
    ...                Heading level must be 1–8 per the sanitizer rules.
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${created_doc_id}    ${doc}[id]
    ${attrs}=    Create Dictionary    level=${9}
    ${heading_node}=    Create Dictionary    type=heading    attrs=${attrs}    content=${EMPTY LIST}
    ${root_content}=    Create List    ${heading_node}
    ${bad_content}=    Create Dictionary    type=doc    content=${root_content}
    Update Document    ${doc}[id]    ${bad_content}    expected_status=422

PUT Text With Script Tag Is Sanitized
    [Documentation]    PUT with a text node containing <script>xss</script> must succeed (200).
    ...                Fetched text must equal the bleach-cleaned value (tags stripped).
    ${doc}=    Create Document    ${1}
    Set Suite Variable    ${created_doc_id}    ${doc}[id]
    ${text_node}=    Create Dictionary    type=text    text=<script>xss</script>safe
    ${content_list}=    Create List    ${text_node}
    ${para_node}=    Create Dictionary    type=paragraph    content=${content_list}
    ${root_content}=    Create List    ${para_node}
    ${xss_content}=    Create Dictionary    type=doc    content=${root_content}
    ${updated}=    Update Document    ${doc}[id]    ${xss_content}
    ${fetched}=    Get Document    ${doc}[id]
    ${fetched_text}=    Set Variable    ${fetched}[document_content][content][0][content][0][text]
    Should Not Contain    ${fetched_text}    <script>
    Should Contain    ${fetched_text}    safe

DELETE Document Returns 204 And Subsequent GET Returns 404
    [Documentation]    DELETE /documents/{id} must return 204; a subsequent GET must return 404.
    ...                Verifies that the document is truly removed from the database.
    ${doc}=    Create Document    ${1}
    ${doc_id}=    Set Variable    ${doc}[id]
    Set Suite Variable    ${created_doc_id}    ${NONE}
    Delete Document    ${doc_id}
    Get Document    ${doc_id}    expected_status=404


*** Variables ***
${EMPTY LIST}    @{EMPTY}


*** Keywords ***
Cleanup Created Document
    [Documentation]    Best-effort DELETE of the document created during the test.
    ...                Tolerates 404 if the test already deleted it.
    IF    $created_doc_id is not None
        Delete Document    ${created_doc_id}    expected_status=any
        Set Suite Variable    ${created_doc_id}    ${NONE}
    END
