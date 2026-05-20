*** Settings ***
Documentation       Suite 9: Chapter numbering algorithm unit tests (data-driven).
...                 Verifies the Compute Chapter Numbers keyword against known heading-level
...                 sequences, matching the algorithm from tasks.md Phase 4 step 3.
Library             Collections
Library             ${CURDIR}/lib/chapter_numbering.py
Resource            __resources/api.resource


*** Test Cases ***
Flat Headings All Level 1
    [Documentation]    Three consecutive h1 headings must number as 1, 2, 3.
    ...                Each h1 increments counter[0] and zeroes counters[1..7].
    ${levels}=    Create List    ${1}    ${1}    ${1}
    ${result}=    Compute Chapter Numbers    ${levels}
    Should Be Equal    ${result}[0]    1
    Should Be Equal    ${result}[1]    2
    Should Be Equal    ${result}[2]    3

Two Levels With Resets
    [Documentation]    [1,2,2,1,2] must produce ['1','1.1','1.2','2','2.1'].
    ...                The second h1 resets h2 counter; h2 after that restarts at 1.
    ${levels}=    Create List    ${1}    ${2}    ${2}    ${1}    ${2}
    ${result}=    Compute Chapter Numbers    ${levels}
    Should Be Equal    ${result}[0]    1
    Should Be Equal    ${result}[1]    1.1
    Should Be Equal    ${result}[2]    1.2
    Should Be Equal    ${result}[3]    2
    Should Be Equal    ${result}[4]    2.1

Skip Level Produces Zero Segment
    [Documentation]    [1,3] must produce ['1','1.0.1'] — the skipped level 2 remains zero.
    ...                The number joins all counters[0:3] = [1,0,1] as '1.0.1'.
    ${levels}=    Create List    ${1}    ${3}
    ${result}=    Compute Chapter Numbers    ${levels}
    Should Be Equal    ${result}[0]    1
    Should Be Equal    ${result}[1]    1.0.1

Deep Nesting After Reset
    [Documentation]    [4,5,5,1,2] — heading 4 with no h1/h2/h3 ancestor produces 0.0.0.1.
    ...                After h1 resets all sub-counters, h2 produces 1.1.
    ${levels}=    Create List    ${4}    ${5}    ${5}    ${1}    ${2}
    ${result}=    Compute Chapter Numbers    ${levels}
    Should Be Equal    ${result}[0]    0.0.0.1
    Should Be Equal    ${result}[1]    0.0.0.1.1
    Should Be Equal    ${result}[2]    0.0.0.1.2
    Should Be Equal    ${result}[3]    1
    Should Be Equal    ${result}[4]    1.1
