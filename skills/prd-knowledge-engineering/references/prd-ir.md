# PRD IR Operational Summary

Schema: `../../../schemas/prd-ir.schema.json`  
Format Profile Schema: `../../../schemas/prd-format-spec.schema.json`

Rules:

1. Keep content separate from publishing configuration.
2. Store semantic Logic `kind`; do not store display numbering or hand-written labels.
3. Limit nested Logic to three levels.
4. Register every `x-` Logic Kind in the resolved Format Profile.
5. Require sources for confirmed high-risk logic.
6. Declare every referenced Asset and verify local files exist.
7. Do not mark a document `confirmed` while a blocking question remains open.
8. Validate with `validators/validate_prd_ir.py` before rendering.

Renderer output must never mutate the validated IR.
