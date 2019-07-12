const MarkdownIt = require('markdown-it')
const fm = require('front-matter')

module.exports = function markdownLoader(source) {
  const md = new MarkdownIt({
    html: true,
    linkify: true,
    xhtmlOut: true,
    breaks: true,
    typographer: true,
  })

  const frontmatter = fm(source)
  frontmatter.attributes.html = md.render(frontmatter.body)

  return `module.exports = ${JSON.stringify(frontmatter.attributes)};`
}
