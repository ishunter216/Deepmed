import React from 'react'
import {connect} from 'react-redux'
import withStyles from 'isomorphic-style-loader/lib/withStyles'
import s from './Home.css'
import DiagnosisForm from './DiagnosisForm'
import {getData} from '../../reducers/diagnosis'

class Home extends React.Component {
  componentDidMount() {
    if (this.props.diagnosisForm) {
      const values = this.props.diagnosisForm
      const fields = Object.keys(values)
      const fieldsValues = {}
      fields.forEach(field => {
        fieldsValues[field] = {
          value: values[field],
        }
      })
      this.form.setFields(fieldsValues)
    }
  }

  handleSubmit = (e) => {
    e.preventDefault()
    this.form.validateFields((err, values) => {
      if (!err) {
        this.props.getData(values)
      }
    })
  }

  render() {
    return (
      <main className={s.container}>
        <h1 className={s.header}>
          Please input your diagnosis in detail below
        </h1>
        <DiagnosisForm
          className={s.form}
          ref={ref => {
            this.form = ref
          }}
          onSubmit={this.handleSubmit}
        />
      </main>
    )
  }
}

const mapState = state => ({
  ...state.diagnosis,
})

const mapDispatch = {
  getData,
}

export default connect(mapState, mapDispatch)(withStyles(s)(Home))
