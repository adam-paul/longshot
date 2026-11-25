# Verification: dates, policies and data-release facts (venues, licences, terms)

Independent check of first-round claims in `presentation.md`, `new-surveys.md` and `orbit-tooling.md`.
Checked 2026-11-21. Status: complete.

Every verdict rests on a page fetched today, unless the row says otherwise. Quotation marks mean the words were copied from the fetched page.

- Raw pages: `data/research/dl/facts-venues`.
- Scripts: `data/research/scripts/fv_fetch.sh`, `fv_text.py`, `fv_ojap.py`, `fv_mpc_x05.py`.
- Requests to JPL: one (the documentation page). Requests to the MPC API: one. No personal or project detail was sent anywhere.

Verdict words: **confirmed**, **partly confirmed**, **refuted**, **unverifiable**.

## Summary

Almost every date and policy the first round reported is correct. The tables below hold 103 checked statements: 92 confirmed, 4 partly confirmed, 3 refuted or corrected, 3 unverifiable, and 1 new. The three corrections are the MPC API limit, the Open Journal of Astrophysics fee, and one wrong citation for a correct fact.

What the plan must change:

1. **The MPC does publish an API limit.** The first round said there is no documented policy. The MPC FAQ says to keep to "not more than 5 requests per second" on the API, and that an IP address "may be blocked". The API takes one designation per request, so all 43,367 near-Earth objects need at least 2.4 hours.
2. **The MPC bulk observation files are older than their timestamp.** The files were last written on 3 June 2026, but the MPC page says they are "complete through the 2026 APR. 14 batch". Seven months of observations are missing. The API is the only current public source.
3. **arXiv now limits every submitter to two new submissions a month** and three active submissions (since 1 October 2026). The first round did not have this.
4. **The arXiv "one-year ban" for unchecked LLM output is not in arXiv's written policy.** It comes from a post on X by the chair of arXiv's computer-science section, reported by TechCrunch and 404 Media. What arXiv's own pages require is disclosure and full author responsibility.
5. **The Open Journal of Astrophysics is free** (the first round was unsure), and it requires an account of how any AI-run analysis was tested and validated.
6. **The DR1 date for Rubin has two official wordings.** RTN-011 says "mid-2028"; the Early Science page says "Jul-Nov 2028". Use the window.

What the plan may rely on: Gaia DR4 on 2 December 2026 at 12:00 CET; the PDC abstract deadline of 20 December 2026; the LPSC abstract deadline of 5 January 2027; RNAAS as a free first publication; the Gaia non-commercial licence; the JPL one-request rule; the Cloudflare and GitHub hosting limits.

Still open: PDC registration fees, the DPS 2027 primary page, the EPSC 2027 abstract deadline, and whether a characterisation catalog fits the claudestronomy programme.

---

## 1. Gaia DR4

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| Release 2 December 2026, 12:00 CET | confirmed | News item dated 2026-10-08: "the Gaia ESA Archive will be down as of Wednesday 25 November 2026 12:00 CET. The archive will re-open on Wednesday 2 December 2026 at 12:00 CET, featuring the new Gaia DR4 release." The date was first announced on 2026-05-07. | https://www.cosmos.esa.int/web/gaia/news |
| Archive downtime from 25 November | confirmed | Same item. The archive is closed for seven days. | same |
| `sso_source` has 436,551 objects | confirmed | DR4 content table, "Last update: 14 September 2026": `sso_source`, 436,551 rows, 145 MB. The page warns that "changes can be expected". | https://www.cosmos.esa.int/web/gaia/dr4 |
| Mean reflectance spectra | confirmed, with a caveat | `sso_reflectance_spectrum`, "Mean BP/RP reflectance spectra of asteroids", 436,551 rows, 13 MB. The draft data model (26 June 2026) stores each spectrum as arrays, with a quality flag per wavelength. | same; draft data model zip linked from that page |
| Epoch astrometry | confirmed | `sso_observation`, 60,542,356 rows, 13 GB, one row per CCD transit. `sso_xp_epoch_spectrum`, 8,656,146 records, 6.9 GB, new in DR4. | same |
| DR5 not before the end of 2030 | confirmed | "Gaia DR5 ... not before the end of 2030". DR4 is "based on 66 months of data". | https://www.cosmos.esa.int/web/gaia/release |
| Gaia data are CC BY-NC 3.0 IGO | confirmed | "Gaia data are distributed under the CC BY-NC 3.0 IGO license." | https://www.cosmos.esa.int/web/gaia-users/license |
| Commercial use needs ESA authorisation | confirmed | "Prior to any commercial use by the User of any Data or Data Product, including any use or application that directly or indirectly generates a financial gain, a detailed request for authorisation/licence shall be made by the User by sending email to data.licences@esa.int." | https://www.cosmos.esa.int/web/esdc/terms-and-conditions |

Notes:

- The row count of the reflectance table equals the row count of `sso_source`. It does not say how many objects have a usable spectrum. The stated volume, 13 MB, is about 30 bytes per row, which is too small for a full spectrum in every row. Treat "seven times more spectra than DR3" as unproven until the release.
- The terms cover "Raw and Calibrated Data" and "analysed data and higher-level science products" in the archive. They do not mention values that a third party derives. The non-commercial condition does follow the data into adapted copies, so a table that copies Gaia columns cannot be released as CC BY. Whether a class probability computed from a Gaia spectrum counts as an adaptation is a legal question the page does not answer. Only a written question to data.licences@esa.int settles it.
- No number on the DR4 page gives the count of near-Earth asteroids.

## 2. Planetary Defense Conference 2027

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| 3-7 May 2027, Montreal | confirmed | "10th IAA Planetary Defense Conference, 3-7 May 2027, Montreal, Canada ... held at McGill University". | https://iaaspace.org/event/10th-iaa-planetary-defense-conference-2027/ |
| Abstract deadline 20 December 2026 | confirmed | Event page: "The extended deadline for receipt of abstracts is December 20, 2026." The submission system itself shows "Submission deadline Dec 20, 2026, 11:59 PM" (Canada/Eastern) and "The call for abstracts is open". | same; https://iaa.spacescience.ro/indico/event/5/abstracts/ |
| A "NEO Characterization" session | confirmed | Topic list: "Near-Earth Object (NEO) Characterization". Call for Papers: "Findings related to characterizing NEO physical, dynamical, and orbital properties"; "Technologies to characterize NEOs via remote sensing and spacecraft flyby/rendezvous/landing". | same; https://iaaspace.org/wp-content/uploads/2026/06/2027_PDC_Call_for_Papers.pdf |
| Abstracts of 250 to 500 words; notification by 22 January 2027 | confirmed | "Technical paper abstracts (250 to 500 words in length)"; "Author notifications of acceptance will be sent on or before January 22, 2027." | event page |
| Who may submit | confirmed: no restriction stated | Abstracts "in the areas described above or otherwise related to planetary defense will be accepted electronically". No membership or affiliation rule appears on the event page, the Call for Papers or the submission page. | same |
| Fees | unverifiable | Registration runs on event.fourwaves.com/pdc, open 24 August 2026 to 24 February 2027, hybrid event. Fees appear only inside the registration application. The event page names an "early-bird registration period" that ends after 22 February 2027. | https://event.fourwaves.com/pdc |

Other facts on the page:

- The June 2026 Call for Papers PDF still gives the old deadline, 23 November 2026. The event page and the submission system give 20 December.
- Full manuscripts and poster or presentation files are due 28 April 2027. Accepted papers go into the conference proceedings and "may be considered for publication in a special issue of Acta Astronautica".
- After submission an author can upload a two-minute pitch video.
- Student competition entries needed proof of enrolment "before November 23, 2026".

## 3. Other 2027 venues

| Venue | Verdict | Evidence | Source |
|---|---|---|---|
| EPSC 2027, 19-24 September 2027, Toulouse | confirmed | "EPSC2027 will take place at the Pierre Baudis Congress Centre in Toulouse, France, from 19-24 September 2027." EPSC 2028 is in Padova, 24-29 September 2028. | https://www.europlanet.org/epsc/ |
| The URL the first report cited for EPSC 2027 | refuted as a source | `europlanet-society.org/?p=29893` is the April 2024 call for hosts. It does not name Toulouse. The fact is right; the citation is wrong. | https://www.europlanet.org/apply-to-host-epsc-in-2026-and-2027/ |
| EPSC 2027 abstract deadline | unverifiable | The conference site www.epsc2027.eu did not answer today. | |
| DPS 2027, same week, Providence | partly confirmed | dps.aas.org and aas.org return HTTP 403 to scripts. A search-engine summary of the DPS page gives Providence, Rhode Island Convention Center, 19-24 September 2027. The Europlanet 2024 call says DPS "will take place that week in Providence, RI, US". EPSC and DPS are therefore on the same days on two continents. | search result for dps.aas.org; Europlanet page above |
| LPSC 2027 | confirmed (new detail) | 15-19 March 2027, The Woodlands, Texas, and virtual. "January 5, 2027: Deadline for abstract submission". | https://www.hou.usra.edu/meetings/lpsc2027/ |
| ACM | confirmed | The 15th ACM was held 6-10 July 2026 in Poznań. The series runs every three years. The next is "tentatively scheduled for 2029"; the host was to be announced at the 2026 banquet and I did not find the announcement. | https://www.astro.amu.edu.pl/en/conference-asteroids-comets-meteors-acm-2026-in-poznan/ ; https://acm2026.syskonf.pl/acm2029 |
| Space Resources Roundtable | partly confirmed | The 26th meeting was 2-5 June 2026 at Colorado School of Mines; abstracts (two pages) were due 16 March 2026. No 2027 date is posted. The domain spaceresources.org is parked. | https://ces.mines.edu/conferences/srr/ |
| Minor Planet Mailing List | confirmed | groups.io/g/mpml: 1,615 members, 23,287 topics. "MPML is open to all with an interest in asteroids and comets." "Archive is visible to anyone." "Posts from new users require approval from the moderators." Topics on the front page today include an archival-DECam trans-Neptunian candidate and an open-source orbit-determination tool, so agent-era work is already being posted there. | https://groups.io/g/mpml |

## 4. arXiv

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| From 21 January 2026 an institutional email is no longer enough | confirmed | "As of January 21, 2026, arXiv will no longer accept institutional email addresses ... as the sole qualifier of endorsement for new authors." | https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/ |
| Two paths: email plus prior authorship, or personal endorsement | confirmed | "The first path requires both 1) an institutional email address ... and 2) previous authorship on an existing paper which has been accepted to the arXiv 'endorsement domain' ... New submitters who cannot meet these requirements can pursue the second path, which is seeking personal endorsement directly from an established arXiv author in the same endorsement domain." | same |
| Staff cannot waive it | confirmed | "arXiv staff cannot waive endorsement requirements or provide a personal endorsement for authors." | same |
| Endorsers need papers between three months and five years old | confirmed | "we only count papers that have been submitted between three months and five years ago". "At least one positive endorsement is required per endorsement category". Help page last modified 10 November 2026. | https://info.arxiv.org/help/endorsement.html |
| Since May 2026, unchecked LLM output earns a one-year ban, then peer review first | partly confirmed | The words are from a post on X by Thomas Dietterich, chair of arXiv's computer-science section, on 14 May 2026: "a 1-year ban from arXiv followed by the requirement that subsequent arXiv submissions must first be accepted by a reputable peer-reviewed venue". TechCrunch (16 May 2026) and 404 Media report it. It is not on arXiv's moderation page or code of conduct (both last modified 10 November 2026), and the arXiv blog has no post about it. | https://techcrunch.com/2026/05/16/research-repository-arxiv-will-ban-authors-for-a-year-if-they-let-ai-do-all-the-work/ ; https://info.arxiv.org/help/moderation/index.html |

What an unaffiliated first-time submitter to astro-ph.EP needs: a personal endorsement from one established arXiv author in the astro-ph endorsement domain. The help page says the endorser "should know the person that you endorse or you should see the paper that the person intends to submit", and that it is "inappropriate to email large numbers of potential endorsers at once".

arXiv's written policy on generative AI (moderation page): authors must "report in their work any significant use of sophisticated tools ... we now include in particular text-to-text generative AI"; each author takes "full responsibility for all its contents, irrespective of how the contents were generated"; "generative AI language tools should not be listed as an author".

New since the first round, rate limit: "arXiv now limits submitters to up to two submissions per calendar month, with a limit of three total active submissions at any given time." It took effect on 1 October 2026 and counts rejected submissions. Source: https://blog.arxiv.org/2026/10/01/updated-rate-limit-policy/

## 5. Research Notes of the AAS and the AAS policy on AI

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| 1,500 words, one figure or one table | confirmed | "1,500 words or fewer, with no more than a single figure or table (but not both)". The count "includes title, headers, captions, and references with 150 words reserved for the required abstract". | https://journals.aas.org/research-note-preparation-guidelines |
| No charge | confirmed | "Research Notes are free to read and currently carry no author publication charges." Published under CC-BY 4.0. | same |
| Moderated, not peer reviewed | confirmed | "not peer reviewed; they are, however, moderated by an editor for appropriateness and format". The moderator is AAS Lead Editor Chris Lintott. | same; https://journals.aas.org/research-notes/ |
| Indexed in ADS, citable | confirmed | "Each RNAAS is issued a DOI and indexed by ADS". "typically published within 72 hours of manuscript receipt". | same |
| Null results in scope | confirmed | Scope: "works in progress, comments and clarifications, null results, or timely reports of observations". | https://journals.aas.org/research-notes/ |
| Catalogs in scope | partly confirmed | Catalogs are not named in the scope. Data tables are handled by reference: "Authors are encouraged to use established repositories such as Zenodo to host data tables which otherwise do not fit". A Note can describe one result and point to the catalog. | preparation guidelines |
| AAS AI policy posted 9 September 2026 | confirmed | "These guidelines were initially posted on 9 September 2026." | https://journals.aas.org/author-llm-guidelines |
| AI cannot be an author; use must be disclosed | confirmed | "AI cannot be listed as an author on publications". "If LLMs are used in the preparation of a submitted manuscript, the authors must disclose this use." | same |
| "LLMs may not be used to generate any portion of a manuscript unsupervised." | confirmed | Exact sentence on the page. | same |
| The policy covers the manuscript, not the analysis | confirmed | "these guidelines concern the manuscript, not the data analysis. Therefore, this paragraph makes no recommendation on the use of AI in data analysis or writing code." | same |

Other limits on the page: "A limit of twenty Notes in any 12 month period by a given first author". "RNAAS is unable to publish substantially novel theories". Notes are published as submitted, with no copy-editing. A single-author Note is written in the first person singular. The AI guidelines list penalties "up to and including retraction of the manuscript and banning of the author(s) from further publication in AAS journals".

## 6. Planetary Science Journal, Open Journal of Astrophysics, JOSS, Zenodo

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| PSJ 2026: $69.51 per text quantum, $61.40 per figure or table | confirmed | "2026 Planetary Science Journal Rates: Text Quanta Charge $69.51; Figure Charge $61.40; Table Charge $61.40; MRT Charge $61.40". One quantum is 350 words; authors, affiliations, acknowledgements and references are not counted. The rates are for calendar year 2026. | https://journals.aas.org/article-charges-and-copyright/ |
| A 20-quanta, 8-figure paper costs about $1,880 | confirmed | 20 x 69.51 + 8 x 61.40 = $1,881.40. Each machine-readable table adds $61.40. | my arithmetic |
| OJAp fee status unclear | refuted: it is free | "Papers can be submitted for publication free of charge, are refereed free of charge and are published (online only) free of charge." The only "not free" sentence on the page refers to an optional outside copy-editing service. | https://astro.theoj.org/for-authors (text is embedded in the page source) |
| OJAp sits behind the arXiv gate | confirmed | "the final version must be on the arXiv in order to be published". Scope is anything suitable for astro-ph. | same |
| OJAp has a "Use of Generative AI" section | confirmed | "We do not operate a blanket ban ... you must declare it in the acknowledgments section ... if GenAI methods are used for any form of calculation, analysis, or data visualization you must include an account of what steps you have taken to test and validate these methods. Articles containing direct evidence of the use of GenAI, such as hallucinated references or prompts in the text will not be accepted." | same |
| JOSS: no fees | confirmed | "There are no fees for submitting or publishing in JOSS." | https://joss.readthedocs.io/en/latest/submitting.html |
| JOSS: repository public for more than six months | confirmed | "The repository must have been public for more than six months prior to submission, with active development spanning that period." | same |
| JOSS: evidence of research use; not new results; not a one-off tool | confirmed | "There must be evidence that the software is being used for research". "Your paper must not focus on new research results accomplished with the software." "rather than being a one-off tool for a single analysis". | same |
| JOSS: AI use must be disclosed | confirmed | An "AI usage disclosure" must name the tools and versions, the scope of help, and confirm human review. | same |
| Zenodo: 50 GB and 100 files per record | confirmed | "We currently accept up to 50GB per record with a maximum of 100 files." A one-time increase to 200 GB is possible. | https://support.zenodo.org/help/en-gb/1-upload-deposit/80-what-are-the-size-limitations-of-zenodo |
| Zenodo: each version is a new record with its own DOI | confirmed | "a completely new record with separate metadata, files and persistent identifier". | https://help.zenodo.org/docs/deposit/manage-versions/ |
| Zenodo: a concept DOI covers all versions | confirmed (was recalled, now checked) | "The last DOI represents all the versions ... We therefore also call the them Version DOIs and Concept DOIs". | https://support.zenodo.org/help/en-gb/1-upload-deposit/97-what-is-doi-versioning |
| Zenodo asks for fair use | confirmed | Not fair use: "Uploading very large number of records (independent of data volume)" and splitting a dataset to get around the limit. | size-limits page |
| GitHub release gives a new Zenodo DOI | confirmed | "Zenodo archives your repository and issues a new DOI each time you create a new GitHub release." | https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content |

## 7. claudestronomy.com and macrogrants.com

Both pages were fetched today. claudestronomy.com was last modified 2026-11-21 and macrogrants.com 2026-11-20 ("Updated November 11, 2026").

| Claim | Verdict | Evidence |
|---|---|---|
| "$100,000 program" on one page, $50,000 on the other | confirmed | claudestronomy.com: "A $100,000 program from macrogrants" and "seeded with $100,000". macrogrants.com: "Grant program · $50,000" and "Will DePue is seeding macrogrants with the first $50,000, for the astronomy program." The pages disagree. |
| Grants $500 to $25,000, approved in a day or two | confirmed, with a caveat | The range is on macrogrants.com only: "Grants from $500 to $25,000, approved in a day or two"; "typically run from about $500 to $25,000". claudestronomy.com names no amount: "compute, Claude, Codex, Grok or Gemini credits and small grants". |
| No application form; email or text | confirmed | "email or text us ... with a short description of what you want to look for. If you already know which archive you want to use, what you've tried, or what would help, include that. These are suggestions, not requirements, and there is no application form." macrogrants adds: "A rough budget or a link to something you've built helps". |
| The six standards quoted by the first report | confirmed | All six sentences are on the page, word for word, under "Some things we care about". |
| No reporting schedule or deliverable format | confirmed | Neither page states one. What is described: the six standards, a Signal group chat, a grantee group chat, and a planned yearly retreat in California. |
| Telescope-time help | confirmed | "if a candidate earns telescope time, we can help you ask for it." Nothing more specific. |
| For-profit work excluded | confirmed | "Some things don't fit inside a nonprofit: for-profit initiatives, political work ... We can't fund those from macrogrants, but we're happy to match you with people who'll give without the deduction". |
| Characterisation in scope | unverifiable | The programme is "for finding new objects in public sky data". Its five target lists are things that move, transit, change, are nearby, or "become interesting across archives". Characterising known asteroids is not named. macrogrants.com describes it more broadly, as "AI agents for astronomical research with public sky archives", "Open to anyone, from first-timers to professional astronomers". Fit has to be asked. |
| Static page of about 24 KB on Vercel | confirmed | 23,774 bytes; `server: Vercel`. |

Also on the pages: macrogrants is "a California nonprofit public benefit corporation, incorporated October 10, 2026"; its 501(c)(3) application "was filed with the IRS on October 13, 2026 and is pending". The programme says "We're happy to help you validate your results" and that a "calibrated non-detection with a completeness curve is a valuable result".

## 8. Minor Planet Center

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| October 2026 newsletter warns about automated and AI-assisted submissions | confirmed | Dated 30 October 2026, section "Data integrity in the Age of Automation and AI": "observers are responsible for ensuring that their submissions are accurate, reliable, and scientifically meaningful. Using an automated tool should never mean submitting results without understanding or verifying them." | https://buttondown.com/MPC_newsletter/archive/newsletter-october-2026 |
| "More rigorous requirements" for observatory codes and programmes | confirmed | "We intend to introduce more rigorous requirements to ensure that observers and observing programs demonstrate an appropriate understanding of astrometric measurements, data validation, and quality control." | same |
| Archival astrometry goes through a review committee | confirmed | "Programs submitting archival astrometry already undergo a review through the Singletons and Archival Review Committee (SARC)". | same |
| The newsletter complains about long AI-written helpdesk tickets | confirmed | "an increasing number of AI-generated tickets that are unnecessarily long"; "we encourage tickets to be no longer than 250 words". | same |
| No documented MPC API policy | refuted | MPC FAQ (last modified 19 November 2026): "If you submit too many requests to the MPC in a short time, your IP Address may be blocked. Please limit queries to https://data.minorplanetcenter.net/api/ endpoints to not more than 5 requests per second. Exceeding this rate may induce an HTTP status code of 429". The get-obs page itself states no limit, which is what the first round read. | https://docs.minorplanetcenter.net/mpc-ops-docs/faqs/ |
| One designation per request | confirmed | Parameter `desigs`: "List of one single string". | https://docs.minorplanetcenter.net/mpc-ops-docs/apis/get-obs/ |
| Bulk files NumObs.txt.gz and UnnObs.txt.gz last modified 2026-06-03 | confirmed, and worse than stated | HTTP headers today: NumObs.txt.gz, Last-Modified 3 June 2026, 9,109,431,211 bytes; UnnObs.txt.gz, 3 June 2026, 455,768,106 bytes. The index page says the files "are complete through the 2026 APR. 14 batch of Minor Planet Circulars". The mid-month files are dated 26 November 2025. | https://www.minorplanetcenter.net/iau/ECS/MPCAT-OBS/MPCAT-OBS.html |
| `NEA.txt` orbits are current | confirmed | Last-Modified 21 November 2026. | https://www.minorplanetcenter.net/iau/MPCORB/NEA.txt |
| SBN replica licence: internal use, non-transferable | confirmed | "MPC Distributed Postgres Database Terms Of Service, Version 1.0, 9/28/2023": "a non-exclusive, non-transferable, non-sublicensable license to replicate, access, and use our database's data for your internal purposes." | https://sbnmpc.astro.umd.edu/MPC_database/replication-info.shtml |
| Derived products must be marked | confirmed | "any modifications or derived data products must be explicitly and clearly marked as such if they are redistributed." | same |
| Replica needs a 24-hour server, 3-day initial download, about 4 TB | confirmed | "SSD - 4 TB", "RAM - 32-48 GB", "24/7 service", initial download "within 3 days", Postgres 14 or higher. | same |

New findings:

- The MPC states a redistribution condition for its observation data: "any use of these data, or of data derived from these data, requires you to maintain the reference information on any redistribution." (MPCAT-OBS page.) The FAQ also says "Data from the MPC's database is made freely available to the public."
- A third bulk route exists. The Small Bodies Node runs the MPC Advanced Queries Interface (MAQI) at https://maqi.astro.umd.edu/ for "authorized users" who want complex queries on the replica. It is in beta and needs an account (MPC newsletter of 11 May 2026).
- The MPC "strongly advise[s] our users to not replicate the tables unless they are sure that they have the required resources".
- From 30 December 2026 the MPC accepts only ADES v2022 submissions (and the old 80-column format). From 12 November 2026 a submission with duplicated timestamps in a tracklet is rejected.
- The MPC used a solar-radiation-pressure fit to decide that 2026 QQ8 is natural. That is the same physics as the project's area-to-mass channel.

## 9. JPL SSD API terms

The page https://ssd-api.jpl.nasa.gov/doc/ was fetched once today. It carries no date. Exact wording, under "SSD API Service - Fair Use Policy":

- "You agree to limit requests to those reasonably necessary for your application or use case. Automated processes must not make unnecessarily frequent, repetitive, or redundant requests. Where practical, applications should cache and reuse results rather than repeatedly requesting unchanged or predictably changing data."
- "You agree to submit only one API request at a time (no simultaneous requests)."
- "You agree to configure automated processes to appropriately handle errors, rate limits, and service unavailability, including by backing off or reducing request rates rather than repeatedly retrying failed requests."
- "Applications making automated connections must provide a valid, application-specific User-Agent request header that includes correct product name, version, and contact information."
- "JPL may rate-limit, throttle, or block access that places an unreasonable load on the service or is inconsistent with this Fair Use Policy. If these restrictions affect a legitimate use, please contact us for assistance; we may be able to suggest a more efficient way to obtain the needed data."
- "You may not embed these APIs in your website (per NASA CORS policy)."
- "You understand that API data formats can change without notice."
- "You should always check the version field in the API output to detect any change".
- "You understand that there is no guarantee any particular API will be available indefinitely."

| Claim | Verdict |
|---|---|
| One request at a time | confirmed |
| No embedding in websites | confirmed |
| User-Agent with product name, version and contact information for automated clients | confirmed. The first report's quotation was a close paraphrase; the exact sentence is above. |

The User-Agent rule conflicts with this project's rule of sending no identifying detail. The owner has to choose a contact address for the production pipeline before it calls JPL automatically.

## 10. Reuse terms for the source catalogs, and the GRSS licence

| Source | Verdict on the first-round claim | What the page says today | Source |
|---|---|---|---|
| SsODNet (IMCCE, now signed "LTE") | confirmed: no licence stated | "the following acknowledgment would be appreciated: This research has made use of LTE's SsODNet VO service (https://ssp.imcce.fr/webservices/ssodnet/)", plus Berthier et al. 2023. "A personal Web interface can easily be developed ... Feel free to make your own." The acknowledgement names LTE, not IMCCE. | https://ssp.imcce.fr/webservices/ssodnet/ |
| MP3C | confirmed: no licence stated | "© 2022 Observatoire de la Côte d'Azur". Requested sentence: "This work is based on data provided by the Minor Planet Physical Properties Catalogue (MP3C) of the Observatoire de la Côte d'Azur". Version 3.3.3-beta.1 (2025-10-03); 1,461,616 bodies; 6,113,272 properties; 3,513 sources. | https://mp3c.oca.eu/ |
| LCDB | confirmed | "Copyright (c) 2021 by Brian D. Warner. All rights reserved." Credit: "Warner, B.D., Harris, A.W., Pravec, P. (2009). Icarus 202, 134-146. Updated [Date of version used]". "The latest release is dated 2023 October 1". | https://minplanobs.org/mpinfo/php/lcdb.php |
| Spitzer NEO table | confirmed: no licence file | GitHub reports `license: null`; last push 2020-01-10. README: "The data compiled here are publicly available. If you use the data, please cite Trilling et al. 2010 and Trilling et al. 2016." 2,204 estimates for 2,132 objects. | https://github.com/mommermi/spitzerneos |
| NEOWISE diameters and albedos (PDS) | confirmed | Release date 2019-03-11. Required citation: "Mainzer, A., Bauer, J., Cutri, R., Grav, T., Kramer, E., Masiero, J., Sonnett, S., and Wright, E., Eds. (2019). NEOWISE Diameters and Albedos V2.0. urn:nasa:pds:neowise_diameters_albedos::2.0. NASA Planetary Data System; doi: 10.26033/18S3-2Z54." No licence text on the page. | https://sbn.psi.edu/pds/resource/neowisediam.html |
| NEOWISE images and catalogs (IRSA) | confirmed | Final release dated 14 November 2024. IRSA: "Most data served by IRSA is public, with no usage restrictions." The page gives a required acknowledgement paragraph. | https://irsa.ipac.caltech.edu/data/WISE/docs/release/NEOWISE/ ; https://irsa.ipac.caltech.edu/data_use_terms.html |
| MITHNEOS | new (the first round could not reach the site) | "Spectra presented here are considered to be in the public domain and may be freely used for any purpose." An acknowledgement paragraph is requested. The data "are unpublished and therefore have not undergone peer review", though much is now in Binzel et al. 2019 and Marsset et al. 2022. | http://smass.mit.edu/minus.html |
| MANOS | confirmed: access unclear | The public site states no licence and no download. It has a login link. Per-object classes are in the published papers. | https://manos.lowell.edu/ |
| GRSS is GPL-3.0 | confirmed | GitHub API for `rahil-makadia/grss`: licence `GPL-3.0`; last push 2026-10-26. PyPI: version 4.6.0, GNU GPL version 3. | https://api.github.com/repos/rahil-makadia/grss ; https://pypi.org/pypi/grss/json |

What GPL-3.0 means for a published pipeline that imports GRSS:

- The Free Software Foundation's reading is that a program that uses a GPL library forms one combined work: "the terms of the GPL apply to the entire combination. The software modules that link with the library may be under various GPL compatible licenses, but the work as a whole must be licensed under the GPL." The same reading applies to Python bindings. (https://www.gnu.org/licenses/gpl-faq.html, entries IfLibraryIsGPL and IfInterpreterIsGPL.)
- So the project's own files may carry MIT or Apache-2.0, both of which are GPL-compatible, but anyone who distributes the pipeline together with GRSS must do so under GPL-3.0. The simplest honest label for the orbit-fitting part is GPL-3.0-or-later.
- The catalog is not affected: "The output of a program is not, in general, covered by the copyright on the code of the program." (entry WhatCaseIsOutputGPL.) The data can be CC BY whatever the code licence is.
- Running the pipeline without distributing it creates no obligation. GPL-3.0 is not the AGPL, so a website built from the output is also free of it.
- This is the FSF's interpretation, not legal advice. ASSIST and REBOUND, which layup uses, are GPL-3.0 as well, so a switch of engine does not remove the question.

Practical rule, unchanged from the first round: publish derived values with identifiers and pointers to their sources; do not republish LCDB, MP3C or SsODNet tables wholesale; keep a credits page with the exact sentences above. Only LCDB asserts "All rights reserved". A written permission from IMCCE/LTE and from OCA would remove the remaining doubt.

## 11. SPHEREx, Rubin, NEO Surveyor

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| SPHEREx DR1 on 12 November 2026 | confirmed | News release dated "November 12th, 2026": "Data Release 1 (DR1) is now available at IRSA." IRSA: "IRSA released SPHEREx Data Release 1 (DR1) in November 2026." DOIs 10.26131/IRSA678 and IRSA679. | https://spherex.caltech.edu/news/spherex-data-release-1-dr1-is-now-available-at-irsa ; https://irsa.ipac.caltech.edu/data/SPHEREx/docs/overview_dr1.html |
| Solar-system legacy catalog due May 2028 (Bock et al., Table 4) | confirmed | Table 4 of arXiv:2511.02985v2: "Legacy Catalogs: Stellar/Brown Dwarfs, Galaxy Clusters, Solar System — May 2028". The abstract says "3 years after launch". "KASI currently curates the solar system objects catalog". | https://arxiv.org/abs/2511.02985 |
| No public SPHEREx solar-system product | confirmed | The mission's data-products schedule lists spectral images, all-sky cubes and a High Reliability Source Catalog (August 2027, January 2028). None is a solar-system product. | https://spherex.caltech.edu/page/data-products |
| LSST started 2026-06-29 | confirmed | "The start of the LSST was formally declared on 2026-06-29." RTN-011 v10.0, dated 2026-11-19. | https://rtn-011.lsst.io/ |
| Offline 2026-07-15 to 2026-10-27 | confirmed | "the extreme weather event that took the observatory offline for ∼3.5 months between 2026-07-15 and 2026-10-27". | same |
| Camera shut down on 15 November | confirmed | Forum post of 17 November 2026: "On Sunday we experienced a loss of cooling capacity in our pumped coolant system ... This required us to shutdown the camera (the camera is safe), and we remain in that state for now". | https://www.rubin.community/t/rubin-status-november-17-2026/12959 |
| Public alerts since 2026-02-24 | confirmed | "The first Rubin alerts began 2026-02-24". "Alerts are fully world-public". The alerts page: "They are world public and have no proprietary period." Seven full-stream brokers. | RTN-011; https://rubinobservatory.org/for-scientists/data-products/alerts-and-brokers |
| DR1 expected mid to late 2028 | confirmed | Early Science page, updated 19 November 2026: "The current expectation window is Jul-Nov 2028." RTN-011: "approximately 24 months after the start of the LSST survey (mid-2028)", and "The precise content of DR1 remains under discussion". | https://rubinobservatory.org/for-scientists/resources/early-science ; RTN-011 |
| PPDB due 2026-11-30; full DP2 due 2026-12-15 | confirmed | RTN-011 schedule table: "PPDB Release, 30 Nov 2026, Planned"; "Data Preview 2, 15 Dec 2026, Planned". "Access to the PPDB service requires data rights, but the data are public." | RTN-011 |
| Rubin reports to the MPC ad hoc | confirmed | "Solar System discoveries will be reported to the Minor Planet Center on an ad-hoc basis during Early Operations, with a goal of increased automation". | RTN-011 |
| Rubin observations are public at the MPC under code X05 | confirmed and replicated | One call to the MPC API for 2025 MN45 returned 597 observations, 580 of them from station X05 (Lr 205, Lg 119, Li 113, g 54, i 43, r 40, Lu 4, u 2), dated 2025-04-22 to 2025-05-04, with magnitudes to 0.001 and `rmsmag`. This matches the first round exactly. | `fv_mpc_x05.py`; https://data.minorplanetcenter.net/api/get-obs |
| NEO Surveyor launch no earlier than September 2027 | confirmed | NASA: "Launch: No earlier than September 2027". JPL: "NEO Surveyor will launch no earlier than September 2027." | https://science.nasa.gov/mission/neo-surveyor/ ; https://www.jpl.nasa.gov/missions/near-earth-object-surveyor/ |

Also from the MPC (February 2026 newsletter): on 5 February 2026 Rubin sent "approximately 20,000 candidate discoveries, corresponding to roughly 246,000 individual observations". Rubin submissions go through a separate MPC pipeline with extra manual vetting.

## 12. Hosting limits

| Claim | Verdict | Evidence | Source |
|---|---|---|---|
| Cloudflare Pages free: 500 builds a month | confirmed | Free 500, Pro 5,000, Business 20,000. One build at a time; a build times out after 20 minutes. Page "Last updated Nov 19, 2026". | https://developers.cloudflare.com/pages/platform/limits/ |
| 20,000 files per site (100,000 on paid plans) | confirmed | "Cloudflare Pages sites can contain up to 20,000 files on the Free plan." | same |
| 25 MiB per file | confirmed | "The maximum file size for a single Cloudflare Pages site asset is 25 MiB." | same |
| 100 custom domains per project | confirmed | Free 100, Pro 250, Business 500. | same |
| Workers static assets have the same limits | confirmed | 20,000 files per Worker version on Free, 100,000 on Paid; 25 MiB per file. | https://developers.cloudflare.com/workers/platform/limits/ |
| R2 free tier: 10 GB, 1 million class A, 10 million class B, free egress | confirmed | Page last updated 30 October 2026. | https://developers.cloudflare.com/r2/pricing/ |
| GitHub Pages: 1 GB, 100 GB a month, 10 builds an hour | confirmed | "Published GitHub Pages sites may be no larger than 1 GB." "soft bandwidth limit of 100 GB per month". "soft limit of 10 builds per hour. This limit does not apply if you build and publish your site with a custom GitHub Actions workflow." Deployments time out after 10 minutes. | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |
| GitHub Pages is not for running a business | confirmed | "not intended for or allowed to be used as a free web-hosting service to run your online business, e-commerce site, or any other website that is primarily directed at either facilitating commercial transactions or providing commercial software as a service (SaaS)." | same |

Other limits on the Cloudflare page: 100 header rules, 2,100 redirects, 100 projects per account. A deployment older than 30 days is deleted unless it is among the 100 most recent or is the current production deployment, so old releases cannot be kept as preview deployments.

The file-count arithmetic of the first round holds with today's SBDB count: 43,367 near-Earth objects at two files each is 86,734 files, over the 20,000 limit. The NHATS list at two files each fits.

---

## Dates that affect the schedule

| Date | Event |
|---|---|
| 25 November 2026, 12:00 CET | Gaia archive closes |
| 30 November 2026 | Rubin PPDB planned (data-rights holders; same data through brokers) |
| 2 December 2026, 12:00 CET | Gaia DR4 |
| 15 December 2026 | Rubin DP2 planned (data-rights holders) |
| 20 December 2026, 23:59 Eastern | PDC 2027 abstract deadline |
| 30 December 2026 | MPC accepts only ADES v2022 |
| 5 January 2027 | LPSC 2027 abstract deadline |
| 22 January 2027 | PDC acceptance notices |
| 24 February 2027 | PDC registration closes |
| 15-19 March 2027 | LPSC 2027, The Woodlands and virtual |
| 28 April 2027 | PDC manuscripts and presentation files due |
| 3-7 May 2027 | PDC 2027, Montreal |
| September 2027 or later | NEO Surveyor launch |
| 19-24 September 2027 | EPSC 2027 (Toulouse) and DPS 2027 (Providence), same week |
| May 2028 | SPHEREx solar-system legacy catalog |
| July to November 2028 | Rubin DR1 expectation window |

## What I could not verify

- PDC 2027 registration fees. They are shown only inside the registration application.
- The DPS 2027 dates from the DPS site itself. The site refuses scripted requests.
- The EPSC 2027 abstract deadline. The conference site did not answer.
- A 2027 date for the Space Resources Roundtable. None is posted.
- The host of ACM 2029.
- Whether the arXiv one-year ban applies outside computer science, or is written down anywhere official.
- Whether claudestronomy funds characterisation work.
- Whether ESA treats derived values as covered by the Gaia licence.
