import React from 'react'
import PropTypes from 'prop-types'
import {connect} from 'react-redux'
import history from '../../history'
import {generateUrl} from '../../router'

function isLeftClickEvent(event) {
  return event.button === 0
}

function isModifiedEvent(event) {
  return !!(event.metaKey || event.altKey || event.ctrlKey || event.shiftKey)
}

class Link extends React.Component {
  static propTypes = {
    to: PropTypes.oneOfType([
      PropTypes.string.isRequired,
      PropTypes.object.isRequired,
    ]),
    children: PropTypes.node.isRequired,
    onClick: PropTypes.func,
  }

  static defaultProps = {
    onClick: null,
  }

  handleClick = (event, to) => {
    if (this.props.onClick) {
      this.props.onClick(event)
    }

    if (isModifiedEvent(event) || !isLeftClickEvent(event)) {
      return
    }

    if (event.defaultPrevented === true) {
      return
    }

    event.preventDefault()
    history.push(to)
  }

  render() {
    const {to, children, ...props} = this.props
    let url
    if (typeof to === 'string') {
      url = generateUrl(to)
    } else {
      url = generateUrl(to.name, to.params)
    }
    return <a href={url} {...props} onClick={(e) => this.handleClick(e, url)}>{children}</a>
  }
}

const mapState = state => ({})

const mapDispatch = {}

export default connect(mapState, mapDispatch)(Link)
