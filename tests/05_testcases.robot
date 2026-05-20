*** Settings ***
Documentation       Suite 5: GET /api/testcases returns seeded test cases.
...                 Verifies at least 3 entries exist, each has a valid project_id, and
...                 the expected seed titles are present in the response.
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session


*** Variables ***
${SEED_TITLE_1}    Lorem ipsum basic flow
${SEED_TITLE_2}    Consectetur adipiscing validation
${SEED_TITLE_3}    Ut labore et dolore boundary check


*** Test Cases ***
Testcases Endpoint Returns At Least Three Entries
    [Documentation]    GET /testcases must return 200 with a list of at least 3 items.
    ${resp}=    Get On Session    api    /testcases    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    ${count}=    Get Length    ${items}
    Should Be True    ${count} >= 3    msg=Expected at least 3 testcases, got ${count}

Each Testcase Has Valid project_id Format
    [Documentation]    Every testcase in the response must have a project_id matching ^Project1_\d{8}$.
    ${resp}=    Get On Session    api    /testcases    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    FOR    ${tc}    IN    @{items}
        Should Match Regexp    ${tc}[project_id]    ^Project1_\\d{8}$
    END

Seed Titles Are Present In Testcases Response
    [Documentation]    The three seeded testcase titles must all appear in the GET /testcases response.
    ${resp}=    Get On Session    api    /testcases    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    ${titles}=    Create List
    FOR    ${tc}    IN    @{items}
        Append To List    ${titles}    ${tc}[title]
    END
    List Should Contain Value    ${titles}    ${SEED_TITLE_1}
    List Should Contain Value    ${titles}    ${SEED_TITLE_2}
    List Should Contain Value    ${titles}    ${SEED_TITLE_3}

Each Testcase Has Required Fields
    [Documentation]    Every testcase entry must contain id, project_id, title, test_state, author fields.
    ${resp}=    Get On Session    api    /testcases    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    FOR    ${tc}    IN    @{items}
        Dictionary Should Contain Key    ${tc}    id
        Dictionary Should Contain Key    ${tc}    project_id
        Dictionary Should Contain Key    ${tc}    title
        Dictionary Should Contain Key    ${tc}    test_state
        Dictionary Should Contain Key    ${tc}    author
    END
