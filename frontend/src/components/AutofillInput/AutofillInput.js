import React from 'react'

// TODO trying to fix autocomplete on iOS Chrome
// https://github.com/facebook/react/issues/1159
class AutofillInput extends React.Component {
  componentDidMount(){
    this.input.addEventListener('blur', (e)=> {
      this.props.onChange(e)
    })
  }

  refInput = (input) => this.input = input

  render() {
    const {...otherProps} = this.props

    return (
      <input
        {...otherProps}
        ref={this.refInput}
      />
    )
  }
}

export default AutofillInput
