import React from 'react'
import VectorMap from './VectorMap'

class VectorMapWrapper extends React.PureComponent {
  render() {
    return (
      typeof window !== 'undefined' &&
      typeof $ !== 'undefined' &&
      typeof $.fn !== 'undefined' &&
      typeof $.fn.vectorMap !== 'undefined'
    ) ? (
      <VectorMap {...this.props}/>
    ) : null
  }
}

export default VectorMapWrapper
