# Clinical Contraindications and Safety Screening

> **Demo knowledge-base document for Medbot.** This is not a clinical
> protocol. Production content must be reviewed and approved by
> qualified healthcare professionals.

## Purpose

This document gives the Retriever example safety-screening information
for diagnostic procedures.

## General Rule

A diagnostic test may require additional screening when a patient has a
medical condition, implanted device, allergy, medication, or other
factor that could affect the procedure.

The assistant should not diagnose the patient or decide independently
that a procedure is safe. When a possible contraindication is
identified, the system should surface the relevant protocol and direct
the patient to the responsible clinical team.

## Example: MRI Screening

Before an MRI appointment, the workflow may need to screen for:

-   Implanted medical devices
-   Certain metallic objects or fragments
-   Other device-specific restrictions described by the MRI facility

The exact screening requirements must come from the facility's approved
MRI safety protocol.

## Example: Contrast Procedures

If a procedure uses contrast material, the workflow may need to collect
or verify information required by the facility's protocol.

The assistant should not make an independent clinical determination
about whether contrast is appropriate.

## Medbot Behavior

When a retrieved document indicates a possible contraindication:

1.  Explain that additional screening may be required.
2.  Avoid giving a personal medical clearance.
3.  Refer the patient to the appropriate clinical professional or
    diagnostic center.
4.  Use the approved protocol as the source of the response.

## Retrieval Keywords

`contraindication`, `screening`, `MRI`, `implant`, `metal`, `contrast`,
`safety`
