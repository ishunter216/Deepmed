import React from 'react'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import cn from 'classnames'
import RCInputNumber from 'rc-input-number'
import s from './InputNumber.scss'

class InputNumber extends React.Component {
  render() {
    const {label, error, ...otherProps} = this.props
    return (
      <div className={cn(error && 'has-error')}>
        {label && <label className='control-label'>{label}</label>}
        <RCInputNumber
          className={s.formControl}
          {...otherProps}
          upHandler={null}
          downHandler={null}
        />
        {error && <span className='help-block'>{error[0]}</span>}
      </div>
    )
  }
}

export default withStyles(s)(InputNumber)
