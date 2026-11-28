RECORD: {{record}}
PART OF THE BOOK: {{part}}
HEADING: {{heading}}
ENTRY BEFORE: {{before_id}} {{before_heading}}
ENTRY AFTER: {{after_id}} {{after_heading}}

TEXT (mentions are marked ⟦mN⟧ … ⟦/mN⟧; nothing else in the text has been changed):
{{text}}

MENTIONS:
{{#mentions}}
- {{id}} | words: «{{quote}}» | part in the text: {{role}} | speaker: {{speaker}}{{#out_of_scope_list}} | on the out-of-scope list: {{registry_id}} {{label}}{{/out_of_scope_list}}
{{/mentions}}

PRE-SEARCH (name search, nasab shift and neighbours, run by script; `why` shows what matched):
{{#mentions}}
{{id}}:
{{#candidates}}
  {{rank}}. {{id}} | {{heading}}{{#status}} | {{status}} → {{target}}{{/status}} | score {{score}} | {{why}}
{{/candidates}}
{{^candidates}}
  (no candidates)
{{/candidates}}
{{/mentions}}

ENTRIES THAT REFER TO THE SUBJECT OF THIS BIOGRAPHY (from reviewed records; may be incomplete):
{{#reverse}}
- {{id}} | {{heading}}
{{/reverse}}

Identify every mention and return the JSON object described in your instructions.
