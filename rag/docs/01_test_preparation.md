# Test Preparation Protocols

> **Demo knowledge-base document for Medbot.** This content is for
> software-development/testing purposes only. Replace it with approved
> protocols from the relevant diagnostic laboratory or healthcare
> organization before production use.

## Purpose

This document contains example preparation guidance that the Medbot
Retriever can use when answering questions about diagnostic-test
preparation.

## General Rules

-   Preparation requirements depend on the specific test.
-   Do not assume that every blood test requires fasting.
-   The patient should follow the preparation instructions supplied by
    the ordering clinician or diagnostic laboratory.
-   If the patient has questions about medication, food, or drink
    restrictions, the system should direct them to the responsible
    healthcare professional or laboratory rather than inventing a rule.

## Example: Fasting Blood Test

For a test whose laboratory protocol explicitly requires fasting:

-   The protocol should state the required fasting duration.
-   The protocol should specify whether plain water is allowed.
-   The protocol should identify any medication instructions.
-   The patient should follow the laboratory's written instructions if
    they differ from generic guidance.

## Example: Imaging Test

For an imaging procedure:

-   Check whether fasting is required.
-   Check whether the patient needs to avoid particular food or drink.
-   Check whether contrast material is involved.
-   Check whether additional screening is required before the procedure.

## Retrieval Keywords

`fasting`, `food`, `water`, `medication`, `preparation`, `blood test`,
`imaging`, `contrast`
