Feature: Note Management
  As a user of AstraNotes
  I want to create, read, update, delete, and search notes
  So that I can manage my personal information securely and privately

  Background:
    Given the application has an empty note store

  # ── FR-01 Create ──────────────────────────────────────────────────────────

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

  # ── SPR-01 Encryption ────────────────────────────────────────────────────

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

  # ── FR-02 Edit ────────────────────────────────────────────────────────────

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

  # ── FR-03 Delete ──────────────────────────────────────────────────────────

  Scenario: Deleting a note removes it from the store
    Given there is a note titled "Temporary" with body "delete me"
    When I delete the note
    Then the note store contains 0 notes

  Scenario: Deleting a non-existent note raises not-found error
    When I try to delete a note with a random UUID
    Then a not-found error is raised

  # ── FR-04 Privacy toggle ─────────────────────────────────────────────────

  Scenario: Toggling a public note to private encrypts its body on disk
    Given the application has an encryption key configured
    And there is a note titled "Diary" with body "personal thoughts"
    When I toggle the note to private
    Then the raw file on disk does not contain "personal thoughts"
    And I can retrieve the note with body "personal thoughts"

  # ── FR-07 Search ─────────────────────────────────────────────────────────

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

  # ── FR-05 Duplicate ──────────────────────────────────────────────────────

  Scenario: Duplicating a note creates a copy with prefixed title
    Given there is a note titled "Template" with body "reusable content"
    When I duplicate the note
    Then the note store contains 2 notes
    And the note store contains a note titled "Copy of Template"
    And the note store contains a note titled "Template"
