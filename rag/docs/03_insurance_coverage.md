# Insurance Coverage Requirements

> **Demo knowledge-base document for Medbot.** This document describes
> an example software workflow, not real insurance policy rules.

## Purpose

The Retriever uses this document category to find insurance-related
requirements before a diagnostic appointment is scheduled.

## General Workflow

Insurance requirements may depend on:

-   The diagnostic test or procedure
-   The patient's insurance provider
-   The insurance plan
-   Whether prior authorization is required
-   The diagnostic center
-   The ordering clinician or facility

The assistant should not claim that a test is covered unless the
connected insurance or laboratory system provides that information.

## Example Verification Flow

1.  Identify the requested diagnostic test.
2.  Identify the selected diagnostic center.
3.  Use the applicable insurance verification service when available.
4.  Check whether prior authorization is required.
5.  Present the returned coverage information to the patient.
6.  If verification cannot be completed, tell the patient that coverage
    still needs to be confirmed.

## Privacy Rule for Medbot

The patient's National Health ID or insurance member number is a
**non-prompt input**.

It should be handled by the application/backend and passed only to the
authorized insurance or booking service when required.

It should not be inserted into the normal LLM prompt or retrieved
knowledge documents.

## Retrieval Keywords

`insurance`, `coverage`, `prior authorization`, `member number`,
`verification`, `insurance provider`
