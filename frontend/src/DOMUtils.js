export function updateTag(tagName, keyName, keyValue, attrName, attrValue, attrName2, attrValue2) {
  const node = document.head.querySelector(`${tagName}[${keyName}="${keyValue}"]`)
  if (node && node.getAttribute(attrName) === attrValue) return

  // Remove and create a new tag in order to make it work with bookmarks in Safari
  if (node) {
    node.parentNode.removeChild(node)
  }
  if (typeof attrValue === 'string') {
    const nextNode = document.createElement(tagName)
    nextNode.setAttribute(keyName, keyValue)
    nextNode.setAttribute(attrName, attrValue)
    if (attrName2) {
      nextNode.setAttribute(attrName2, attrValue2)
    }
    document.head.appendChild(nextNode)
  }
}

export function updateMeta(name, content) {
  updateTag('meta', 'name', name, 'content', content)
}

export function updateCustomMeta(property, content) {
  updateTag('meta', 'property', property, 'content', content)
}

export function updateLink(rel, href) {
  updateTag('link', 'rel', rel, 'href', href)
}
