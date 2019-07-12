import React from 'react'
import cn from 'classnames'

class Input extends React.Component {
  render() {
    const {label, error, ...otherProps} = this.props
    return (
      <div className={cn(error && 'has-error')}>
        {label && <label className='control-label'>{label}</label>}
        <input className='form-control' type='text' {...otherProps}/>
        {error && <span className='help-block'>{error}</span>}
      </div>
    )
  }
}

export default Input
