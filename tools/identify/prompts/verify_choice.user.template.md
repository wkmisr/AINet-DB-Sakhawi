RECORD: {{record}}
PART OF THE BOOK: {{part}}
HEADING: {{heading}}
ENTRY BEFORE: {{before_id}} {{before_heading}}
ENTRY AFTER: {{after_id}} {{after_heading}}

TEXT (the mention to decide is marked ⟦{{mention}}⟧ … ⟦/{{mention}}⟧):
{{text}}

MENTION: {{mention}} | words: «{{quote}}» | part in the text: {{role}} | speaker: {{speaker}}

CANDIDATES (random order):
{{#candidates}}
- {{id}} | {{heading}}{{#status}} | {{status}} → {{target}}{{/status}}
{{/candidates}}
- none of these
- cannot decide

Choose, and return the JSON object described in your instructions.
