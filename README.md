# conventoarchiver

Repository for collecting scripts to help capture MyConvento newsroom
press-releases from the MyConvento PR management suite.

## Introduction

MyConvento is a "newsroom" platform. It provides a means for organizations to
write press releases and other similar assets and then publish them online.

Integration, at least in some observable cases is via iframe and redirect. The
host organization only ever points to a page on a MyConvento newsroom site.

Archiving of MyConvento content is difficult because most agents cannot easily
navigate to the content directly. The content exists an iframe, remote to the
site being called, the crawler tends to only retrieve the host website, not
the press-release.

## Demo

Take a look at how the redirect works on what I think is a demo site:

* https://myconvento.com/public/newsroom/data/plugin/news/run/show_news/news_id/3451175/lang/22/id/4337/integration/js

Redirects to:

* https://www.membratech-b2b-portal.com/media-newsroom/#newsroom/data/plugin/news/run/show_news/news_id/3451175/lang/22/id/4337/integration/js

The second link here is the one you would normally see from a corporate
website. The link to MyConvento is entirely opaque unless you inspect the
source and identify where the content is being retrieved from.

If you try to save the second link in the internet archive (today December
2021) you end up with an IA slug that looks as follows:

* `/web/20211217121622/https://www.membratech-b2b-portal.com/media-newsroom/`

Today's archive page:

* https://web.archive.org/web/20211217121622/https://www.membratech-b2b-portal.com/media-newsroom/

NB. That IA slug is: https://www.membratech-b2b-portal.com/media-newsroom/

From there you cannot see the news article information at the original site
that we were trying to save.

Working through the permutation here, then it is difficult to see exactly how
to archive MyConvento sites.

After truncating the MyConvento URL, reducing it just to the article ID, then
one can create a URL that links directly to a URL hosted by MyConvento without
the redirect to the host organizaiton and associated iframe content.

* https://myconvento.com/public/newsroom/data/plugin/news/run/show_news/news_id/3451175

Which can be archived more conventionally.

* https://web.archive.org/web/20211217131419/https://myconvento.com/public/newsroom/data/plugin/news/run/show_news/news_id/3451175

## Process

To archive a myconvento newsroom, therefore, you need to take the source URL
of the newsroom - this acts like an index. Using the example above the index
would look as follows:

* https://myconvento.com/public/index.php?controller=newsroom&action=data&plugin=news&run=list_news&lang=22&id=4337&integration=js&page=

That redirects to:

* https://www.membratech-b2b-portal.com/media-newsroom/#index.php?controller=newsroom&action=data&plugin=news&run=list_news&lang=22&id=4337&integration=js&page=1

From the newsroom page, save all the story items approx 40 on a full page but
that may also be configurable by the host (it does not look like parameters
work).

For each story, identify the PDF associated with the story, and optionally
read the page title.

Save each out to a list to then be processed, i.e. saved to an internet
archive.

Other aspects of pages, including media files (`<!-- Mediafiles -->`) could be
archived too, but this is best left to the system doing that by setting save
outlinks where possible.

## License

GNU GPLv3.
