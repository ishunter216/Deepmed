import React from 'react'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Spin.css'

class Spin extends React.Component {
  render() {
    const {spinning} = this.props
    return spinning ? (
      <div className={s.wrapper}>
        <div className={s.spinner}>
          <div className={s.inner}/>
        </div>
      </div>
    ) : null
  }
}

export default withStyles(s)(Spin)
