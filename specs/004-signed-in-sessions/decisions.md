# Decisions — 004 Signed-in sessions

## D1 — Only "sign out other sessions", not one chosen session

The issue and R4 both say a person can sign out any session. allauth's browser page offers one
action, which ends every session except the current one. Ending a single chosen session exists only
in allauth's headless API. Article XIII says a feature upstream lacks is raised there first, and
building it here is an ADR. The spec therefore delivers what allauth's page does and records
single-session sign-out as an upstream gap for the maintainer to raise.

## D2 — The browser column shows allauth's raw user-agent

A user-agent string is hard to read, and turning it into "Firefox on macOS" would help a person
recognise a session. allauth shows the raw string and has no parser, and adding one here would be a
feature allauth does not have. The column shows what allauth records.

## D3 — The table scrolls, the page does not

allauth's list has up to five columns (started, IP address, browser, last seen, current marker),
more than a phone screen fits. Hiding a column would hide information a person needs to recognise a
session, so the table keeps every column and scrolls sideways inside its own area.
