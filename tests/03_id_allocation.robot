*** Settings ***
Documentation       Suite 3: project_id allocation under repeated reserve calls.
...                 Verifies uniqueness, strict monotonic increase, and correct format of reserved IDs.
Library             Collections
Resource            __resources/api.resource
Suite Setup         Create API Session


*** Variables ***
${N_RESERVES}    5


*** Test Cases ***
Reserve N IDs Are All Unique
    [Documentation]    Reserve ${N_RESERVES} IDs sequentially; all returned project_ids must be unique.
    ${ids}=    Reserve Multiple IDs    ${N_RESERVES}
    ${unique}=    Remove Duplicates    ${ids}
    Length Should Be    ${unique}    ${N_RESERVES}

Reserve N IDs Are Strictly Increasing By Number
    [Documentation]    Sequential reserve calls must yield strictly increasing requirement_numbers.
    ${numbers}=    Reserve Multiple Numbers    ${N_RESERVES}
    FOR    ${idx}    IN RANGE    1    ${N_RESERVES}
        ${prev}=    Set Variable    ${numbers}[${idx - 1}]
        ${curr}=    Set Variable    ${numbers}[${idx}]
        Should Be True    ${curr} > ${prev}
        ...    msg=requirement_number at index ${idx} (${curr}) is not > previous (${prev})
    END

Reserved project_ids Match Expected Format
    [Documentation]    Every reserved project_id must match regex ^Project1_\d{8}$.
    ${ids}=    Reserve Multiple IDs    ${N_RESERVES}
    FOR    ${pid}    IN    @{ids}
        Should Match Regexp    ${pid}    ^Project1_\\d{8}$
    END


*** Keywords ***
Reserve Multiple IDs
    [Documentation]    Reserve ${count} IDs via POST /requirements/reserve-id; return list of project_ids.
    ...                Does not create requirements, so counter numbers are simply consumed (gaps allowed).
    [Arguments]    ${count}
    ${ids}=    Create List
    FOR    ${_}    IN RANGE    ${count}
        ${reserved}=    Reserve New ID
        Append To List    ${ids}    ${reserved}[project_id]
    END
    RETURN    ${ids}

Reserve Multiple Numbers
    [Documentation]    Reserve ${count} IDs and return a list of the raw requirement_number integers.
    ...                Used to verify monotonic increase of the counter.
    [Arguments]    ${count}
    ${numbers}=    Create List
    FOR    ${_}    IN RANGE    ${count}
        ${reserved}=    Reserve New ID
        Append To List    ${numbers}    ${reserved}[requirement_number]
    END
    RETURN    ${numbers}
