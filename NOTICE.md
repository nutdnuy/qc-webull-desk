# Notice

## What this is

QuantCorner Desk for Webull is an independent plugin written by QuantCorner. It
is not made, reviewed or endorsed by Webull, and it is not an official Webull
product. It connects to Webull only through the user's own Webull MCP connection.

## Provenance

- Written from scratch on 2026-11-26. The idea of a research-desk plugin with a
  `/start` menu is common to several broker and research plugins; the text,
  workflows, calculators, report template and data handling here are original
  and are built around the tools Webull's MCP server exposes.
- No text, code, template or image from another broker's plugin is included.
- Report styling follows QuantCorner's own design system (Broadsheet Empiricism 1.6.0).
- Fonts are loaded from Google Fonts under the SIL Open Font License:
  Newsreader, Noto Serif Thai, IBM Plex Sans Thai Looped, IBM Plex Mono.

## Referral link

The plugin contains one referral link, set in `partner.json`. It is shown only
to people who say they have no Webull account or who ask how to open one, and
in the report footer, always with a sentence disclosing that QuantCorner may
receive a referral benefit. To change or remove it, edit `partner.json` and run
`python3 tools/build.py`. Setting `show_in_report_footer` to `false` removes
the footer line.

## Not advice

Outputs are general information and analysis for the user's own consideration.
They are not investment advice, a recommendation or a solicitation. AI output
can be wrong. Check figures against the original source before acting.
