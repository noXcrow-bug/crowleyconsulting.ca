# crowleyconsulting.ca

Website for **Noah Crowley Asbestos and Designated Substances Consulting** (legal name: Noah Crowley Consulting).
Plain HTML, CSS and JavaScript, hosted free on GitHub Pages. No build step is needed to publish.

## What's here

| Page | Purpose |
| --- | --- |
| `index.html` | Home with the four doors |
| `building-owners.html`, `landlords.html`, `employers.html`, `contractors.html` | One landing page per program |
| `obligation-check.html` | The Obligation Check quiz (routing rules from the business plan) |
| `services.html` | One-off services and list prices |
| `asbestos-testing-*.html` | Local search pages: Windsor, Leamington, Chatham, Sarnia, London |
| `asbestos-testing-before-renovation.html` and three more | Trigger pages for search |
| `guide-*.html` | The four lead-magnet checklists |
| `about.html`, `contact.html`, `privacy.html`, `404.html` | Supporting pages |
| `assets/config.js` | **Your form and booking links go here** |
| `tools/build.py` | Regenerates every page from one place (copy, prices, contact details) |

## Settings

Edit `assets/config.js` on GitHub (pencil icon) and commit:

```js
FORM_ENDPOINT: "https://formspree.io/f/xxxxxxx",   // where form submissions go
BOOKING_URL:   "https://calendly.com/your-link"    // where "Book a call" goes
```

Phone and email are written into every page for search engines. To change them, edit `SITE` at the top of
`tools/build.py` and run `python3 tools/build.py`, or ask Claude to rebuild with your details.
