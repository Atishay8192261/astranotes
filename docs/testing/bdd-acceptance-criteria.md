# BDD Acceptance Criteria — AstraNotes

Written in Gherkin syntax (Given / When / Then).  
Executable step definitions: `tests/bdd/test_notes_bdd.py`  
Feature file: `tests/bdd/notes.feature`

---

## Feature: Note Management

```gherkin
Feature: Note Management
  As a user of AstraNotes
  I want to create, read, update, delete, and search notes
  So that I can manage my personal information securely

  Background:
    Given the application has an empty note store

  # FR-01 ──────────────────────────────────────────────────────────────────

  Scenario: Create a new public note
    When I create a note with title "Shopping List" and body "Milk, Eggs, Bread"
    Then the note store contains 1 note
    And the note title is "Shopping List"
    And the note body is "Milk, Eggs, Bread"
    And the note is not private

  Scenario: Creating a note with a blank title is rejected
    When I try to create a note with title "   " and body "some content"
    Then a validation error is raised
    And the note store contains 0 notes

  Scenario: Creating a note with special characters in title succeeds
    When I create a note with title "Q&A — #important!" and body "details here"
    Then the note store contains 1 note
    And the note title is "Q&A — #important!"

  # SPR-01 ─────────────────────────────────────────────────────────────────

  Scenario: Private note body is encrypted on disk
    Given the application has an encryption key configured
    When I create a private note with title "Secret" and body "TopSecret123"
    Then the note store contains 1 note
    And the raw file on disk does not contain "TopSecret123"
    And I can retrieve the note with body "TopSecret123"

  Scenario: Creating a private note without an encryption key fails
    Given the application has no encryption key
    When I try to create a private note with title "Secret" and body "hidden"
    Then a persistence error is raised

  # FR-02 ──────────────────────────────────────────────────────────────────

  Scenario: Edit an existing note changes its content
    Given there is a note titled "Draft" with body "version 1"
    When I update the note title to "Final" and body to "version 2"
    Then the note title is "Final"
    And the note body is "version 2"
    And the note's modified timestamp is later than its created timestamp

  Scenario: Updating a note with a blank title is rejected
    Given there is a note titled "Good Title" with body "body"
    When I try to update the note title to "  "
    Then a validation error is raised

  # FR-03 ──────────────────────────────────────────────────────────────────

  Scenario: Deleting a note removes it from the store
    Given there is a note titled "Temporary" with body "delete me"
    When I delete the note
    Then the note store contains 0 notes

  Scenario: Deleting a non-existent note raises not-found error
    When I try to delete a note with a random UUID
    Then a not-found error is raised

  # FR-04 ──────────────────────────────────────────────────────────────────

  Scenario: Toggling a public note to private encrypts its body on disk
    Given the application has an encryption key configured
    And there is a note titled "Diary" with body "personal thoughts"
    When I toggle the note to private
    Then the raw file on disk does not contain "personal thoughts"
    And I can retrieve the note with body "personal thoughts"

  # FR-07 ──────────────────────────────────────────────────────────────────

  Scenario: Search matches notes by keyword in title
    Given there is a note titled "Grocery List" with body "milk, eggs"
    And there is a note titled "Unrelated" with body "nothing here"
    When I search for "Grocery"
    Then the search results contain "Grocery List"
    And the search results do not contain "Unrelated"

  Scenario: Search matches notes by keyword in body (case-insensitive)
    Given there is a note titled "Meeting Notes" with body "discuss MILK delivery"
    When I search for "milk"
    Then the search results contain "Meeting Notes"

  Scenario: Empty search keyword returns no results
    Given there is a note titled "Alpha" with body "beta"
    When I search for ""
    Then the search results are empty

  # FR-05 ──────────────────────────────────────────────────────────────────

  Scenario: Duplicating a note creates a copy with prefixed title
    Given there is a note titled "Template" with body "reusable content"
    When I duplicate the note
    Then the note store contains 2 notes
    And the note store contains a note titled "Copy of Template"
    And the note store contains a note titled "Template"
```

---

## Manual Acceptance Criteria (UI layer — not automatable headlessly)

```gherkin
Feature: Dynamic UI State Management

  Scenario: Delete and Duplicate buttons are disabled on startup
    Given the application has just launched
    When no note has been selected
    Then the Delete button is greyed out and non-clickable
    And the Duplicate button is greyed out and non-clickable

  Scenario: Buttons enable when note is selected
    Given there is at least one note in the list
    When the user clicks a note in the sidebar
    Then the Delete button becomes active
    And the Duplicate button becomes active

  Scenario: Buttons disable when New Note is clicked
    Given a note is selected and buttons are enabled
    When the user clicks "+ New"
    Then the Delete button is greyed out
    And the Duplicate button is greyed out

Feature: System Health Dashboard

  Scenario: Admin panel shows live statistics
    Given the application has 3 notes (2 public, 1 private)
    When the user clicks the "System" button in the header
    Then a popup appears showing:
      | Field                  | Value        |
      | Application            | ● Running    |
      | JSON Storage           | ● Accessible |
      | Total Notes            | 3            |
      | Public Notes           | 2            |
      | Private Notes          | 1            |

Feature: Locked Private Note Display

  Scenario: Private note appears with lock indicator when not unlocked
    Given the app was launched without entering a passphrase
    And there is a private (encrypted) note on disk
    When the sidebar is rendered
    Then the private note appears with a 🔒 prefix in its title
    And the subtitle says "encrypted — click to unlock"

  Scenario: Clicking a locked note prompts for passphrase
    Given the app shows a 🔒 note in the sidebar
    When the user clicks the locked note
    Then a passphrase dialog appears
    And on correct passphrase entry the note opens in the editor
```
