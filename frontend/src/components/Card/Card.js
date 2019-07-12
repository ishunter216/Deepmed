import React from 'react'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Card.css'
import cn from 'classnames'
import {Spin} from '../'

class Card extends React.Component {
  render () {
    const {className, title, children, loading} = this.props
    return (
      <div className={cn(s.card, className)}>
        {!loading ? (
          <React.Fragment>
            {title && <h4 className={s.header}>{title}</h4>}
            {children}
          </React.Fragment>
        ) : (
          <Spin spinning/>
        )}
      </div>
    )
  }
}

export default withStyles(s)(Card)
