"""Convento Archiver attempts to make inroads into archiving articles
from the My Convento newsroom platform.

We're interested in two links from My Convento resources, the press-release
itself, and the PDF copy of the same release.

    Original: https://myconvento.com/public/newsroom/data/plugin/news/run/show_news/news_id/2998166/lang/22/id/
    PDF: https://myconvento.com/application/controllers/newsroom/pdf.php?news_id=enc2_YVdaaU9YQmxNM05FTVhWT1VscEJSREJrV2s4MmR6MDk&l=22&lang=22&id=

Process:

    1. Cycle through index pages capturing all IDs.
    2. Create a listing of links to specific press releases.
    3. Read each page of the press release for the PDF link.
    4. Return a list of PDFs and press releases. These are formatted in
        html and json for now.
    5. Optionally, submit to the Internet Archive (not implemented...).

"""

import configparser
import json
import re
import sys
import urllib.request

# Config all happens below. It requires config.cfg files to be setup
# correctly and to be provided as arguments to the script. We could
# maybe wrap all of this into a function, but as is, it will run first
# thing in the script, and ensures everything is setup okay. If not,
# the script won't run which is essentially what we're looking for if
# the configuration isn't correct.
CONFIG = ""
try:
    CONFIG = sys.argv[1]
except IndexError as err:
    print(
        "Make sure you have provided one argument, e.g. `python conventoarchiver.py yourconfig.cfg`:",
        err,
        file=sys.stderr,
    )
    sys.exit(1)

config = configparser.ConfigParser()
config.read(CONFIG)

try:
    indices_url = config["main"]["convento_indices"]
    pages = int(config["main"]["number_of_pages"])
    suffix = config["main"]["sitemap_suffix"]
except KeyError as err:
    print("Problem reading config cannot access key:", err, file=sys.stderr)
    sys.exit(1)


def _id_regex():
    """ID regex defines six groups of patterns, for which we are
    interested in the fifth group (match[4]) which should be a
    large integer that representa a page ID. The string that it should
    match against looks as follows:

    `a href="https://myconvento.com/public/newsroom/data/plugin/news/run/show_news/news_id/3107954/lang/`

    :return: regex string for matching press release IDs (string)
    """
    return '(a class="" )(href=")(.*)(news_id/)(\d*)(\/lang\/)'


def _title_regex():
    """Regex that defines three groups of which we are interested in
    the second (match[1]) which should provide us with the title as
    defined in HTML for a webpage. The string that it should match
    against looks as follows:

    `<title>Newsroom der ...</title>`

    :return: regex string for matching the title element in an HTML
        (string)
    """
    return "(<title>)(.*)<(/title>)"


def _pdf_url_regex():
    """Regex that defines five groups of patterns, for which we are
    interested in the fourth group (match[3]) which should be a URL
    pointing at a PDF copy of a press release for which we already have
    a link to the HTML version.

    `<i class="fa fa-file-pdf-o"></i> <a href="https://myconvento.com/application/controllers/newsroom/pdf.php?news_id=enc2_YVdaaU9YQmxNM05FTVhWT1VscEJSREJrV2s4MmR6MDk&l=22&lang=22&id=" rel=`

    :return: regex string for matching PDF URLs (string)
    """
    return '(i class=")(fa fa-file-pdf-o)(.*href=")(.*)(" rel=")'


def capture_ids(indices_url):
    """Capture all IDs for press releases from the My Convento index
    pages.

    :param indices_url: My Convento index base URL, ending in page=
        which will be incremented page=1, page=2 etc. to capture all
        ids until there are no more ids to capture ()
    :return: list of press-release IDs (list).
    """
    ids = []
    curr_ids = []
    for page in range(1, pages):
        page_url = "{}{}".format(indices_url, page)
        print("Page URL:", page_url, file=sys.stderr)
        resp = urllib.request.urlopen(page_url)
        data = resp.read().decode("utf8")
        id_re = re.compile(_id_regex())
        matches = re.findall(id_re, data)
        page_ids = [match[4] for match in matches]
        if curr_ids and page_ids == curr_ids:
            break
        curr_ids = page_ids
        ids = ids + page_ids
    print("Number of IDs:", len(set(ids)), file=sys.stderr)
    return set(ids)


def construct_pr_html_url(id_):
    """Construct a URL for the html press-release pages.

    :param id_: ID of a press release in My Convento.
    :return: URL (string).
    """
    canonical_convento_url = (
        "https://myconvento.com/public/newsroom/data/plugin/news/run/show_news/news_id/"
    )
    return "{}{}".format(canonical_convento_url, id_)


def capture_pdf_links(urls):
    """Capture links for press-release PDF files from My Convneto
    press-release HTML pages.

    The list output from here looks as follows:

        [
            (title (string), url (string), pdf_link (string)),
            (title (string), url (string), pdf_link (string)),
            (title (string), url (string), pdf_link (string)),
            (title (string), url (string), pdf_link (string)),
        ]

    Access to the values in the second position of the list might look
    as follows, given list link_tuples:

        title = link_tuples[1][0]
        url = link_tuples[1][1]
        pdf = link_tuples[1][2]

    Through iteration, the caller can access all items.

    :param urls: list of press-release URLs (list)
    :return: list of PDF links (list)
    """
    pdfs = []
    for url in urls:
        resp = urllib.request.urlopen(url)
        data = resp.read().decode("utf8")
        title_re = re.compile(_title_regex())
        try:
            title = title_re.findall(data)[0][1].replace("Newsroom der  - ", "")
        except IndexError:
            title = None
            pass
        pdf_re = re.compile(_pdf_url_regex())
        pdf_link = pdf_re.findall(data)[0][3]
        pdfs.append((title, url, pdf_link))
    return pdfs


def output_simple_html(link_tuples):
    """Output a simple HTML listing of all press-releases and PDF links.

    :param link_tuples: list of tuples containing, title, link, and PDF
        values (list)
    :return: None (nonetype)
    """
    links = ""
    for linkset in link_tuples:
        links = "{}   <ul>\n".format(links)
        links = "{}      <li>Title: {}</li>\n".format(links, linkset[0])
        links = '{}      <li>HTML: <a href="{}">{}</a></li>\n'.format(
            links, linkset[1], linkset[1]
        )
        links = '{}      <li>PDF: <a href="{}">{}</a></li>\n'.format(
            links, linkset[2], linkset[2]
        )
        links = "{}   </ul>".format(links)

    html = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "   <head><title>Newsroom Sitemap</title></head>\n"
        "   <body>\n{}\n   </body>\n"
        "</html>"
    )

    with open("sitemap-{}.htm".format(suffix), "wb") as sitemap:
        sitemap.write(html.format(links).encode("utf8"))


def output_simple_json(link_tuples):
    """Output a simple JSON listing of all press-releases and PDF links.

    :param link_tuples: list of tuples containing, title, link, and PDF
        values (list)
    :return: None (nonetype)
    """
    with open("sitemap-{}.json".format(suffix), "wb") as sitemap:
        sitemap.write(json.dumps(link_tuples, indent=2, sort_keys=True).encode("utf8"))


def output_simple_text(link_tuples):
    """Output a simple text listing of all press-releases and PDF links.

    :param link_tuples: list of tuples containing, title, link, and PDF
        values (list)
    :return: None (nonetype)
    """
    with open("sitemap-{}.txt".format(suffix), "wb") as sitemap:
        for link in link_tuples:
            sitemap.write("{}\n".format(link[1]).encode("utf8"))
            sitemap.write("{}\n".format(link[2]).encode("utf8"))


def main():
    """Primary entry point of the script."""

    ids = capture_ids(indices_url)
    urls = [construct_pr_html_url(id_) for id_ in ids]
    pdfs_releases = capture_pdf_links(urls)

    output_simple_html(pdfs_releases)
    output_simple_json(pdfs_releases)
    output_simple_text(pdfs_releases)


if __name__ == "__main__":
    main()
