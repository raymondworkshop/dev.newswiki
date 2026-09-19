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
          light: "#f5f4f0",
          lightgray: "#dddcd6",
          gray: "#8a8680",
          darkgray: "#3c3a36",
          dark: "#191816",
          secondary: "#2f5c4e",
          tertiary: "#4d7d6c",
          highlight: "rgba(47, 92, 78, 0.07)",
          textHighlight: "#e4edc8aa",
        },
        darkMode: {
          light: "#131512",
          lightgray: "#2b2f2c",
          gray: "#8a908b",
          darkgray: "#d5d6d2",
          dark: "#f3f2ee",
          secondary: "#8fbfab",
          tertiary: "#b3d4c4",
          highlight: "rgba(143, 191, 171, 0.12)",
          textHighlight: "#5a7a3088",
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
