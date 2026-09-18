import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import { QuartzComponentProps } from "./quartz/components/types"

const isHome = (page: QuartzComponentProps) => page.fileData.slug === "index"

const isTopicIndex = (page: QuartzComponentProps) => {
  const slug = page.fileData.slug ?? ""
  return slug !== "index" && /\/index$/.test(slug)
}

const isArticlePage = (page: QuartzComponentProps) => !isHome(page) && !isTopicIndex(page)

const leftChrome = [
  Component.PageTitle(),
  Component.MobileOnly(Component.Spacer()),
  Component.Search(),
  Component.Darkmode(),
  Component.TopicNav(),
]

// components shared across all pages
export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {},
  }),
}

// components for pages that display a single page (e.g. a single note)
export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs({ rootName: "主頁" }),
      condition: (page) => !isHome(page),
    }),
    Component.ConditionalRender({
      component: Component.ArticleTitle(),
      condition: (page) => {
        const slug = page.fileData.slug ?? ""
        return slug !== "index" && !/\/index$/.test(slug)
      },
    }),
    Component.ConditionalRender({
      component: Component.ContentMeta(),
      condition: (page) => {
        const slug = page.fileData.slug ?? ""
        return slug !== "index" && !/\/index$/.test(slug)
      },
    }),
    Component.ConditionalRender({
      component: Component.ArticleTopics(),
      condition: isArticlePage,
    }),
  ],
  left: [
    ...leftChrome,
    Component.ConditionalRender({
      component: Component.ReaderMode(),
      condition: isArticlePage,
    }),
  ],
  // Keep article pages two-column (no graph rail) for a cleaner read.
  right: [],
  // Article pages: Backlinks after body; client moves it above「相關文章」when present.
  afterBody: [
    Component.ConditionalRender({
      component: Component.Backlinks(),
      condition: isArticlePage,
    }),
  ],
}

// components for pages that display lists of pages  (e.g. tags or folders)
export const defaultListPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs({ rootName: "主頁" }),
    Component.ConditionalRender({
      component: Component.ArticleTitle(),
      condition: (page) => {
        const slug = page.fileData.slug ?? ""
        return !/\/index$/.test(slug) && slug !== "index"
      },
    }),
    Component.ConditionalRender({
      component: Component.ContentMeta(),
      condition: (page) => {
        const slug = page.fileData.slug ?? ""
        return !/\/index$/.test(slug) && slug !== "index"
      },
    }),
  ],
  left: leftChrome,
  right: [],
}
