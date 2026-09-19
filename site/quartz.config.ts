import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "The Storyline",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "zh-TW",
    baseUrl: "news-wiki.pages.dev",
    ignorePatterns: ["private", "templates", ".obsidian"],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "local",
      cdnCaching: true,
      typography: {
        header: "SF Pro Display",
        body: "SF Pro Text",
        code: "SF Mono",
      },
      colors: {
        lightMode: {
          light: "#fafaf8",
          lightgray: "#e7e7e4",
          gray: "#8a8a86",
          darkgray: "#3a3a38",
          dark: "#161615",
          secondary: "#161615",
          tertiary: "#5c5c58",
          highlight: "rgba(0, 0, 0, 0.04)",
          textHighlight: "#e8e8e4aa",
        },
        darkMode: {
          light: "#111110",
          lightgray: "#2a2a28",
          gray: "#8d8d88",
          darkgray: "#d4d4d0",
          dark: "#f4f4f1",
          secondary: "#f4f4f1",
          tertiary: "#c4c4be",
          highlight: "rgba(255, 255, 255, 0.06)",
          textHighlight: "#ffffff22",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.AiSynthesis(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // Keep builds fast and deployment-friendly.
      // Plugin.CustomOgImages(),
    ],
  },
}

export default config
