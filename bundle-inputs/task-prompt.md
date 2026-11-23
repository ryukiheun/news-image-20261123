# Task prompt — news-image-20261123 build session

Build the make.fun bounty entry news-image-20261123 (image + program).
Do NOT submit yet — the parent agent reports review results to the user
first, then submits.

Bounty: "Sum up 23 November's world news in one image". Prize $100
(1st $20, top 50 share), no entry fee. Entries close 2026-11-25 09:00 KST;
result due 2026-12-09 17:00 KST.

Read first: ~/workspace/makefun/오답노트.md (follow its pre-submit
checklist), ~/workspace/custom-skills/makefun-playbook/SKILL.md (skill
1.5.241 — do NOT upgrade), and the -21 entry's submit notes and research
log (follow its format and standard: 6 stories, entry.png 1024x1024,
main.py, research log, 2 review rounds, kit check, presubmit gate).

Layout guide: use Q1 (top-left quadrant) of the supplied guide image
only — masthead with thin double rule, large lead-photo slot centre
right, two-column article columns left, four-column story grid below,
wide photo/banner slot at the bottom — compressed into one 1024x1024
square: masthead (date 23 NOVEMBER 2026 + title), lead story on top,
6 story cards in a grid below. High contrast, big headlines, red lead
band as the anchor so it reads at 256px. Do NOT use Q2 (Busan ad +
QR code), Q3 (real press photo of Lee Jae-myung), or Q4 (garbled
Korean headline). Q1's grey bars and X-boxes are placeholders only;
copy no fake wording from them.

Research: only events that happened or were first reported on
23 November 2026. Six stories, each verified by opening 2+ named
wire/press article bodies (Reuters, AP, AFP, Al Jazeera, The Hindu,
etc.). No dateless items, aggregators, or social posts. Pending
outcomes are phrased as in-progress/due only, never invented.
Sensor Studio YouTube is a lead only (check its RSS for 23 Nov
videos); no card may depend on a video alone. Record facts, dates,
source URLs, and rejected alternates in
news-image-20261123-research.md in the -21 format.

Build: entry.png 1024x1024 drawn from scratch by the program (PIL,
no external images or copied photos, deterministic output — two runs,
identical sha256). No /output root deletion. README (all template
placeholders filled), LICENSE (MIT, SPDX line), git repo + commit,
bundle-inputs/ — same structure as the -21 entry. Fetch a fresh kit
per bounty into ~/workspace/makefun/news-image-20261123-kit/ and
record kit.json sha256. Write all code in this session; do not re-type
lines first seen in tool output (thinking_reproduces trap).

Verify: egm-review 2 rounds (fresh reviewers each time), fix all
Blockers and re-verify. Run the kit check and the presubmit gate
(~/workspace/makefun/bin/presubmit.sh), plus a tmpfs-mount rehearsal.
Report: entry.png (sha256, byte size), the 6-story list, review
rounds (Blocker/Major counts + fixes), kit check result, presubmit
result, entry count and cutline % (top 50 / entries).
