# Big Data Processing workspace instructions

## Maintain the course learning paper

For every user request in this workspace that teaches, clarifies, practises, or applies Big Data Processing course material—including lecture questions, quiz/exam questions, and lab work—update the following document in the same turn:

`Summary and Learning Sheet/Big Data Processing - Learning Summary and Cheat Sheet.md`

Apply these maintenance rules:

1. Read the existing document before editing it.
2. Integrate the new learning into the relevant chronological lecture/week section. Do not append a transcript or a dated Q&A log.
3. Improve or replace existing explanations when the new explanation is clearer. Merge overlaps and remove redundancy so the paper remains cohesive and useful for revision.
4. Keep two complementary layers in the one document:
   - **Chronological learning summary:** concepts and explanations arranged in course/lecture order.
   - **Lab and exam cheat sheet:** the most condensed recurring commands, files, code patterns, data flows, common errors, and one-line explanations.
5. Add a cheat-sheet entry only when it is operationally useful in labs or likely to help with assessment revision. Keep lab commands grouped by where they run: local Windows machine, jumphost, EMR master node, or HDFS.
6. For code, explain input, emitted key-value pairs, shuffle/sort behaviour, reducer input, and final output. Prefer small representative patterns over copying long programs.
7. Generalise assignment learning where useful, but do not let assignment-specific implementation details overwhelm the lecture and lab narrative.
8. Use the local course materials as the primary source of truth. Clearly label missing files, version-dependent paths, or points that still need verification.
9. Update the document's `Last updated` date and its coverage line. Do not create extra study documents unless the user requests them.
10. In the final response, briefly identify which section of the learning paper was updated.
11. If the user's intended learning outcome, source week, level of detail, or desired document structure is genuinely unclear and a wrong assumption would materially weaken the paper, ask one concise clarification question. Otherwise make a reasonable assumption and continue.
12. When there is a concrete way to make the learning paper more useful—such as a missing diagram, recall question, worked data-flow example, or clearer grouping—briefly suggest it to the user. Avoid generic improvement suggestions.
13. End each substantive week in the chronological summary with 3–5 short active-recall questions and answers inside a collapsible `<details>` block. Revise these questions as the week's coverage improves; do not merely accumulate more questions.
14. Keep the learning paper and any future summary or cheat-sheet documents in Markdown (`.md`) format unless the user explicitly requests an export format.
15. Keep the Markdown polished and easy to scan: use a consistent heading hierarchy, short paragraphs, tables for exact comparisons, code fences for commands, callouts for important warnings, and diagrams only when they improve understanding.
16. When a visual would materially clarify an architecture, hierarchy, or data flow, search for an authoritative internet source and embed the most relevant visual in the Markdown. Prefer official course, Apache, AWS, or other primary documentation; include descriptive alt text, a linked source caption, and a nearby text explanation or text-diagram fallback. Do not add decorative, redundant, low-resolution, or untraceable images.
