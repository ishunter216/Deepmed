import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Register.scss'

class Register extends React.Component {
  componentWillUnmount() {
  }

  render() {

    return (
      <main>
      </main>
    )
  }
}

const mapState = state => ({
  ...state.register,
})

const mapDispatch = {
}

export default connect(mapState, mapDispatch)(withStyles(s)(Register))
