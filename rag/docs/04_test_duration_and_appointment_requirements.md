# Test Duration and Appointment Requirements

> **Demo knowledge-base document for Medbot.** Durations in this
> document are intentionally generic examples. Production values must
> come from the diagnostic center's approved scheduling data.

## Purpose

This document provides example information for questions about
appointment duration and scheduling requirements.

## General Scheduling Rules

The appointment system should determine:

-   Whether the requested test requires an appointment
-   Available dates and times
-   Expected appointment duration
-   Whether preparation must be completed before arrival
-   Whether the patient needs to arrive early
-   Whether a referral or order is required

## Duration

Test duration should be retrieved from the approved diagnostic-center
data rather than guessed by the LLM.

For example, a knowledge-base entry could use this structure:

``` text
Test: <test name>
Typical appointment duration: <duration supplied by the facility>
Early-arrival requirement: <facility requirement>
Preparation: <link or reference to preparation protocol>
```

## Booking Flow

The Medbot should collect the information required by the booking tool.

According to the project specification, the external appointment API
requires:

-   Preferred diagnostic center
-   Desired booking time

After those values are gathered, the booking tool handles the
appointment request.

## Important Separation

The LLM can explain scheduling requirements, but the external booking
API is responsible for the actual appointment operation.

## Retrieval Keywords

`duration`, `appointment`, `booking`, `arrival`, `schedule`, `time`,
`referral`
