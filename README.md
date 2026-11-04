# crowleyconsulting.ca

Website for **Noah Crowley Asbestos and Designated Substances Consulting** (legal name: Noah Crowley Consulting).
Plain HTML, CSS and JavaScript, hosted free on GitHub Pages. No build step is needed to publish.

## What's here

| Page | Purpose |
| --- | --- |
| `index.html` | Home: building owners, landlords, contractors, reports |
| `building-owners.html`, `landlords.html` | Building programs (Compliance Essentials, Project Ready, Facility Partner) |
| `contractors.html` | Cleared-to-Start Pass, the contractor compliance desk |
| `employers.html` | O. Reg. 490/09 duties; exposure monitoring quoted per job (workplace program parked) |
| `obligation-check.html` | The Obligation Check quiz (routing rules from the business plan) |
| `services.html` | Report menu with public "from" prices |
| `asbestos-testing-*.html` | Local search pages: Windsor, Leamington, Chatham, Sarnia, London |
| `asbestos-testing-before-renovation.html` and three more | Trigger pages for search |
| `guide-*.html` | The four lead-magnet checklists |
| `about.html`, `contact.html`, `privacy.html`, `404.html` | Supporting pages |
| `assets/config.js` | **Your form and booking links go here** |
| `tools/build.py` | Regenerates every page from one place (copy, prices, contact details). Prices follow price book PB-2026.11: the site quotes only its public "from" prices |

## Settings

Edit `assets/config.js` on GitHub (pencil icon) and commit:

```js
FORM_ENDPOINT: "https://formspree.io/f/xxxxxxx",   // where form submissions go
BOOKING_URL:   "https://calendly.com/your-link"    // where "Book a call" goes
```

Phone and email are written into every page for search engines. To change them, edit `SITE` at the top of
`tools/build.py` and run `python3 tools/build.py`, or ask Claude to rebuild with your details.
