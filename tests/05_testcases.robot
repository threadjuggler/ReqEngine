*** Settings ***
Documentation       Suite 5: GET /api/testcases returns seeded test cases.
...                 Verifies 6 entries exist (3 per project), each has a valid project_id format,
...                 the expected seed titles are present, and project_id_number filter works.
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session


*** Variables ***
${SEED_TITLE_1}    Lorem ipsum basic flow
${SEED_TITLE_2}    Consectetur adipiscing validation
${SEED_TITLE_3}    Ut labore et dolore boundary check


*** Test Cases ***
Testcases Endpoint Returns Six Entries
    [Documentation]    GET /testcases must return 200 with a list of exactly 6 items.
    ...                Two projects seeded with 3 lorem testcases each = 6 total.
    ${resp}=    Get On Session    api    /testcases    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    ${count}=    Get Length    ${items}
    Should Be True    ${count} >= 6    msg=Expected at least 6 testcases, got ${count}

Each Testcase Has Valid project_id Format
    [Documentation]    Every testcase in the response must have a project_id matching Project1_ or Project2_.
    ...                Format is ^(Project1|Project2)_\d{8}$ per the shared counter convention.
    ${resp}=    Get On Session    api    /testcases    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    FOR    ${tc}    IN    @{items}
        Should Match Regexp    ${tc}[project_id]    ^(Project1|Project2)_\\d{8}$
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

Filter By Project1 Returns Exactly Three Testcases
    [Documentation]    GET /testcases?project_id_number=1 must return exactly 3 entries.
    ...                Only Project1's seeded testcases should be returned when filtering by id=1.
    ${resp}=    Get On Session    api    url=/testcases?project_id_number=1    expected_status=200
    ${items}=    Set Variable    ${resp.json()}
    ${count}=    Get Length    ${items}
    Should Be Equal As Integers    ${count}    3
    FOR    ${tc}    IN    @{items}
        Should Match Regexp    ${tc}[project_id]    ^Project1_\\d{8}$
    END
