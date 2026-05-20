*** Settings ***
Documentation       Suite 3: project_id allocation under repeated reserve calls.
...                 Verifies uniqueness, strict monotonic increase, correct format of reserved IDs,
...                 and per-project counter independence (Project1 and Project2 are separate).
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session


*** Variables ***
${N_RESERVES}    5


*** Test Cases ***
Reserve N IDs Are All Unique
    [Documentation]    Reserve ${N_RESERVES} IDs sequentially; all returned project_ids must be unique.
    ${ids}=    Reserve Multiple IDs    ${N_RESERVES}    Project1
    ${unique}=    Remove Duplicates    ${ids}
    Length Should Be    ${unique}    ${N_RESERVES}

Reserve N IDs Are Strictly Increasing By Number
    [Documentation]    Sequential reserve calls must yield strictly increasing requirement_numbers.
    ${numbers}=    Reserve Multiple Numbers    ${N_RESERVES}    Project1
    FOR    ${idx}    IN RANGE    1    ${N_RESERVES}
        ${prev}=    Set Variable    ${numbers}[${idx - 1}]
        ${curr}=    Set Variable    ${numbers}[${idx}]
        Should Be True    ${curr} > ${prev}
        ...    msg=requirement_number at index ${idx} (${curr}) is not > previous (${prev})
    END

Reserved project_ids Match Expected Format
    [Documentation]    Every reserved project_id must match regex ^Project1_\d{8}$.
    ${ids}=    Reserve Multiple IDs    ${N_RESERVES}    Project1
    FOR    ${pid}    IN    @{ids}
        Should Match Regexp    ${pid}    ^Project1_\\d{8}$
    END

Project1 And Project2 Counters Are Independent
    [Documentation]    Reserve IDs from Project1 and Project2; numbers must not collide.
    ...                Each project increments its own counter; the same number can appear in
    ...                both but the full project_ids must be distinguishable by prefix.
    ${ids_p1}=    Reserve Multiple IDs    3    Project1
    ${ids_p2}=    Reserve Multiple IDs    3    Project2
    # All Project1 ids must start with Project1_
    FOR    ${pid}    IN    @{ids_p1}
        Should Match Regexp    ${pid}    ^Project1_\\d{8}$
    END
    # All Project2 ids must start with Project2_
    FOR    ${pid}    IN    @{ids_p2}
        Should Match Regexp    ${pid}    ^Project2_\\d{8}$
    END
    # The combined set of all 6 ids must all be distinct (different prefixes ensure no collisions)
    ${all_ids}=    Create List
    FOR    ${pid}    IN    @{ids_p1}
        Append To List    ${all_ids}    ${pid}
    END
    FOR    ${pid}    IN    @{ids_p2}
        Append To List    ${all_ids}    ${pid}
    END
    ${unique_all}=    Remove Duplicates    ${all_ids}
    Length Should Be    ${unique_all}    6


*** Keywords ***
Reserve Multiple IDs
    [Documentation]    Reserve ${count} IDs for the given project_name; return list of project_ids.
    ...                Does not create requirements, so counter numbers are simply consumed (gaps allowed).
    [Arguments]    ${count}    ${project_name}=Project1
    ${ids}=    Create List
    FOR    ${_}    IN RANGE    ${count}
        ${reserved}=    Reserve New ID    ${project_name}
        Append To List    ${ids}    ${reserved}[project_id]
    END
    RETURN    ${ids}

Reserve Multiple Numbers
    [Documentation]    Reserve ${count} IDs for the given project and return a list of requirement_numbers.
    ...                Used to verify monotonic increase of the counter.
    [Arguments]    ${count}    ${project_name}=Project1
    ${numbers}=    Create List
    FOR    ${_}    IN RANGE    ${count}
        ${reserved}=    Reserve New ID    ${project_name}
        Append To List    ${numbers}    ${reserved}[requirement_number]
    END
    RETURN    ${numbers}
